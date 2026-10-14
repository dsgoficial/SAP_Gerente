"""Repository model of the service: domains and class rules (no QGIS imports).

A repository may carry a model (`GET /repos/{id}/model`, capability
`repository_model`): domains with labels and, per class, the rules a save
must respect. The model is immutable and identified by its digest; a root
and all its clones share it, so `Models` downloads each digest once and
asks the service only whether the digest it knows is still the installed
one (`?known=`).

`ClassRules.check` applies the rules the service applies at save time
(`Model::check` in backend/storage-gpkg/src/model.rs), with the same codes
and the same reasons, so a refusal reads the same whether the client or the
service found it. The service remains the authority: this check only avoids
a round trip and keeps the edit buffer.

Reals of 4 bytes. A field whose source type is `real` is a binary32 in the
source base and a binary64 in the repository. The client rounds a typed
value to the nearest binary32 before saving and shows the shortest decimal
text that reads back to the same binary32, so a feature read and saved
without change produces no version.
"""
import json
import math
import struct
import threading
from urllib.parse import quote

# Capabilities of /api/info: the model route, and `violations` in a refused save.
CAPABILITY='repository_model'
VIOLATIONS='save_violations'
# Codes of a refusal, as the service names them.
DOMAIN='domain'; CHECK='check'; MAX_LENGTH='max_length'; OUT_OF_RANGE='out_of_range'; LIST='list'; IDENTITY='identity_form'
# Accepted values listed in a `check` reason (LISTED_CODES of the service).
LISTED_CODES=30
INT64_MIN=-(2**63); INT64_MAX=2**63-1
# Parsed models kept in memory (the full EDGV model is about 225 KB).
CACHE_MAX=8


def float32(value):
    """The binary32 nearest to `value`, as a Python float; ValueError when it does not fit."""
    try:
        return struct.unpack('<f',struct.pack('<f',float(value)))[0]
    except OverflowError:
        raise ValueError('fora da faixa de um real de 4 bytes') from None


def float32_text(value):
    """Shortest decimal text that reads back to the binary32 nearest to `value`."""
    single=float32(value)
    if single==0 or not math.isfinite(single):
        return repr(0.0 if single==0 else single)
    for digits in range(1,10):
        text='%.*g'%(digits,single)
        try:
            if float32(float(text))==single: return repr(float(text))
        except ValueError:
            continue
    return repr(single)


def float32_display(value):
    """The float whose shortest text is `float32_text(value)` (0.1 for 0.10000000149011612)."""
    return float(float32_text(value))


def is_canonical_uuid(text):
    """36 characters, lowercase hexadecimal digits and hyphens (as the service checks)."""
    return (isinstance(text,str) and len(text)==36 and
            all(c=='-' if k in (8,13,18,23) else c in '0123456789abcdef' for k,c in enumerate(text)))


def _is_integer(value):
    return isinstance(value,int) and not isinstance(value,bool)


def _code_text(code):
    return str(code)


# Mark of a code the domain of the model does not have.
UNKNOWN_CODE='código sem rótulo'


def code_label(code,label):
    """"rótulo (código)" of a value of a domain. Labels of a source base such
    as the EDGV already end with the code ("Leito natural (1)") and are kept."""
    label=str(label or '').strip(); suffix='('+_code_text(code)+')'
    if not label: return _code_text(code)
    return label if label.endswith(suffix) else label+' '+suffix


def plain_text(value):
    """A stored value as a person reads it, without the model."""
    if value is None: return '(sem valor)'
    if isinstance(value,bool): return 'true' if value else 'false'
    if isinstance(value,(dict,list)): return json.dumps(value,ensure_ascii=False)
    return str(value)


def shown_value(rules,name,value):
    """Text shown for the stored `value` of the field `name`: with `rules`
    (ClassRules or None), a field of a domain shows "rótulo (código)" and a
    list field one label per element; a code the domain does not have is
    shown as stored, marked. Any other field shows the value."""
    return plain_text(value) if rules is None else rules.shown(name,value)


def state_names(rules,*states):
    """Names of the fields to show for `states` (features or None): the
    fields of the class in its order, or those the states carry."""
    if rules is not None: return list(rules.kinds)
    names=[]
    for state in states:
        for name in ((state or {}).get('properties') or {}):
            if name not in names: names.append(name)
    return names


def change_lines(rules,before,after):
    """One line per field of a version: "campo: antes → depois" when it
    changed, "campo: valor" otherwise (also for an insertion or a deletion,
    which have one state)."""
    lines=[]
    for name in state_names(rules,before,after):
        old=None if before is None else shown_value(rules,name,(before.get('properties') or {}).get(name))
        new=None if after is None else shown_value(rules,name,(after.get('properties') or {}).get(name))
        if old is None or new is None or old==new: lines.append(name+': '+(new if new is not None else old))
        else: lines.append(name+': '+old+' → '+new)
    return lines


def compare_lines(rules,columns):
    """One line per field of the states of a merge item: `columns` is a list
    of (title, state or None, text for an absent state)."""
    lines=[]
    for name in state_names(rules,*(state for _,state,_ in columns)):
        parts=[title+' '+(shown_value(rules,name,(state.get('properties') or {}).get(name)) if state is not None else absent)
               for title,state,absent in columns]
        lines.append(name+': '+' · '.join(parts))
    return lines


class ClassRules:
    """Rules of one class of a repository: its fields in the model, the
    domains they use and the fields the class specification requires."""

    def __init__(self,dataset,kinds,document,required=()):
        described=(document.get('classes') or {}).get(dataset) or {}
        self.dataset=dataset
        # Canonical kind of each field of the class (integer, text, json, ...).
        self.kinds=dict(kinds)
        self.identity=described.get('identity')
        self.fields={name:rule for name,rule in (described.get('fields') or {}).items() if name in self.kinds}
        self.domains=document.get('domains') or {}
        self.required=frozenset(required or ())
        self.digest=document.get('digest')
        self._sets={}

    def rule(self,name):
        return self.fields.get(name) or {}

    def codes(self,name):
        """[(code, label)] the class accepts in `name`, in domain order
        (the `allowed` subset when the class has one), or None without domain."""
        rule=self.rule(name)
        entries=self.domains.get(rule.get('domain')) if rule.get('domain') else None
        if entries is None: return None
        allowed=rule.get('allowed')
        accepted=None if allowed is None else {(type(code),code) for code in allowed}
        return [(entry['code'],entry.get('label') or _code_text(entry['code'])) for entry in entries
                if accepted is None or (type(entry['code']),entry['code']) in accepted]

    def labels(self,name):
        """{(type, code): "rótulo (código)"} of the whole domain of `name`
        (not only what the class accepts: a stored value may be older than
        the restriction), or None when the field has no domain."""
        rule=self.rule(name)
        entries=self.domains.get(rule.get('domain')) if rule.get('domain') else None
        if entries is None: return None
        cached=self._sets.get((name,'labels'))
        if cached is None:
            cached=self._sets[(name,'labels')]={(type(entry['code']),entry['code']):code_label(entry['code'],entry.get('label'))
                                                 for entry in entries}
        return cached

    def shown(self,name,value):
        """Text shown for the stored `value` of `name` (see `shown_value`)."""
        labels=self.labels(name)
        if labels is None and self.single(name) and isinstance(value,(int,float)) and not isinstance(value,bool):
            # A real of 4 bytes of the source base, by its shortest text.
            try: return float32_text(value)
            except ValueError: return plain_text(value)
        if labels is None or value is None: return plain_text(value)
        def one(code):
            if isinstance(code,str) and self.kinds.get(name)=='integer':
                # A number kept as its lexeme (values.Number).
                try: code=int(str(code))
                except ValueError: pass
            key=(type(code),code) if isinstance(code,(int,str)) and not isinstance(code,bool) else None
            label=labels.get(key) if key is not None else None
            return label if label is not None else plain_text(code)+' ('+UNKNOWN_CODE+')'
        if self.rule(name).get('list'):
            items=self._list(value)
            if items is None: return plain_text(value)
            return ', '.join(one(item) for item in items) if items else '(lista vazia)'
        return one(value)

    def default(self,name):
        """(True, value) when the model gives a literal default; expressions are ignored."""
        default=self.rule(name).get('default')
        if isinstance(default,dict) and 'value' in default: return True,default['value']
        return False,None

    def single(self,name):
        """Whether `name` is a real of 4 bytes in the source base."""
        return self.kinds.get(name)=='real' and self.rule(name).get('source_type')=='real'

    def singles(self):
        return [name for name in self.kinds if self.single(name)]

    # Reals of 4 bytes ---------------------------------------------------------

    def display(self,properties):
        """`properties` with the reals of 4 bytes as the shortest text shows them."""
        names=[name for name in self.singles() if isinstance(properties.get(name),(int,float)) and not isinstance(properties.get(name),bool)]
        if not names: return properties
        shown=dict(properties)
        for name in names:
            try: shown[name]=float32_display(properties[name])
            except ValueError: pass
        return shown

    def storage(self,properties,stored=None):
        """`properties` with the reals of 4 bytes rounded to binary32. A value
        that still equals what `display` showed for the stored state is kept
        as stored, so an untouched field never changes."""
        out=dict(properties)
        for name in self.singles():
            value=out.get(name)
            if isinstance(value,bool) or not isinstance(value,(int,float)): continue
            before=None if stored is None else stored.get(name)
            if isinstance(before,(int,float)) and not isinstance(before,bool):
                try:
                    if float32_display(before)==value or before==value:
                        out[name]=before; continue
                except ValueError:
                    pass
            try: out[name]=float32(value)
            except ValueError as error: raise ValueError('Campo '+name+': valor '+repr(value)+' '+str(error)+'.') from None
        return out

    # Check --------------------------------------------------------------------

    def _set(self,name,key):
        cached=self._sets.get((name,key))
        if cached is None:
            rule=self.rule(name)
            if key=='domain': codes=[entry['code'] for entry in self.domains.get(rule.get('domain')) or []]
            else: codes=rule.get('allowed') or []
            cached=self._sets[(name,key)]={(type(code),code) for code in codes}
        return cached

    def _scalar(self,name,rule,value,prefix,add):
        """One value against the rules of its field (`check_scalar` of the service)."""
        integer=_is_integer(value); text=isinstance(value,str)
        shown=_code_text(value) if integer or text else 'de outro tipo'
        if integer:
            low=rule.get('min',INT64_MIN); high=rule.get('max',INT64_MAX)
            if value<low or value>high:
                source=rule.get('source_type')
                add(OUT_OF_RANGE,prefix+'valor '+str(value)+' fora da faixa '+str(low)+' a '+str(high)+
                    (' do tipo '+source+' do modelo' if source else ''))
                return
        if text and rule.get('max_length') is not None and len(value)>rule['max_length']:
            add(MAX_LENGTH,prefix+'texto com '+str(len(value))+' caracteres; o campo aceita até '+str(rule['max_length']))
            return
        key=(type(value),value) if integer or text else None
        if rule.get('domain') and rule['domain'] in self.domains:
            if key is None or key not in self._set(name,'domain'):
                add(DOMAIN,prefix+'valor '+shown+' fora do domínio '+rule['domain'])
                return
        if rule.get('allowed') is not None:
            if key is None or key not in self._set(name,'allowed'):
                allowed=rule['allowed']
                listed=[_code_text(code) for code in allowed[:LISTED_CODES]]
                if len(allowed)>LISTED_CODES: listed.append('e mais '+str(len(allowed)-LISTED_CODES))
                add(CHECK,prefix+'valor '+shown+' não é aceito nesta classe'+
                    (' (restrição '+rule['check']+')' if rule.get('check') else '')+'; valores aceitos: '+', '.join(listed))

    def _value(self,name,value):
        """The value as the rules see it: an integer, a text, or neither."""
        kind=self.kinds.get(name)
        if kind=='integer':
            if _is_integer(value): return value
            if isinstance(value,str):
                # A number kept as its lexeme (values.Number).
                try: return int(str(value))
                except ValueError: return None
            return None
        if kind=='text': return str(value) if isinstance(value,str) else None
        return None

    def _list(self,value):
        if isinstance(value,str):
            try: value=json.loads(value)
            except ValueError: return None
        return value if isinstance(value,list) else None

    def check(self,dsg_id,properties):
        """Every rule `properties`, of identity `dsg_id`, breaks: a list of
        `{dataset, id, field, code, detail}`, as the service reports them."""
        out=[]
        def violation(field,code,detail):
            out.append({'dataset':self.dataset,'id':str(dsg_id),'field':field,'code':code,'detail':detail})
        identity=self.identity
        if identity and identity.get('kind')=='uuid' and not is_canonical_uuid(str(dsg_id)):
            violation(None,IDENTITY,'a identidade '+json.dumps(str(dsg_id),ensure_ascii=False)+
                      ' não é um UUID em texto canônico (minúsculas, com hífens), como o modelo exige de '+str(identity.get('field')))
        for name,rule in self.fields.items():
            value=properties.get(name)
            if value is None: continue
            add=lambda code,detail,name=name:violation(name,code,detail)
            element=rule.get('list')
            if element is None:
                scalar=self._value(name,value)
                self._scalar(name,rule,scalar if scalar is not None else object(),'',add)
                continue
            what='inteiros' if element=='integer' else 'textos'
            items=self._list(value)
            if items is None:
                add(LIST,'o campo guarda uma lista JSON de '+what); continue
            for position,item in enumerate(items,start=1):
                prefix='elemento '+str(position)+': '
                fits=_is_integer(item) and INT64_MIN<=item<=INT64_MAX if element=='integer' else isinstance(item,str)
                if fits: self._scalar(name,rule,item,prefix,add)
                else: add(LIST,prefix+'a lista só aceita '+what+', sem nulos')
        return out

    def summary(self):
        """What the model asks of each field, one line per field, for a form."""
        lines=[]
        for name in self.kinds:
            rule=self.rule(name); parts=[]
            codes=self.codes(name)
            if codes is not None:
                shown=[_code_text(code)+' '+label for code,label in codes[:LISTED_CODES]]
                if len(codes)>LISTED_CODES: shown.append('e mais '+str(len(codes)-LISTED_CODES))
                parts.append('valores aceitos: '+'; '.join(shown))
            elif 'min' in rule or 'max' in rule:
                parts.append('faixa '+str(rule.get('min',INT64_MIN))+' a '+str(rule.get('max',INT64_MAX)))
            if rule.get('max_length') is not None: parts.append('até '+str(rule['max_length'])+' caracteres')
            if rule.get('list'): parts.append('lista de '+('inteiros' if rule['list']=='integer' else 'textos'))
            if self.single(name): parts.append('real de 4 bytes')
            found,default=self.default(name)
            if found: parts.append('padrão '+_code_text(default))
            if name in self.required: parts.append('obrigatório')
            if parts: lines.append(name+': '+', '.join(parts)+'.')
        if self.identity and self.identity.get('kind')=='uuid':
            lines.append('Identidade: UUID em texto canônico (minúsculas, com hífens).')
        return lines


def violation_text(violation):
    """One refusal: which feature, which field, why, and the code."""
    where='campo '+str(violation['field']) if violation.get('field') else 'identidade'
    return ('Feição '+str(violation.get('id'))+' (classe '+str(violation.get('dataset'))+'), '+where+': '+
            str(violation.get('detail'))+' ['+str(violation.get('code'))+']')


def report(violations,limit=20):
    """Refusals of one save, one line per feature and field."""
    lines=[violation_text(v)+'.' for v in violations[:limit]]
    if len(violations)>limit: lines.append('E mais '+str(len(violations)-limit)+' recusa(s).')
    return lines


def refusal_text(violations,separator=' ',local=False):
    """A save the repository model refused, by the service or (`local`) before sending."""
    head=('Salvamento recusado antes de enviar, pelo modelo do repositório; nada foi gravado.' if local else
          'Salvamento recusado pelo modelo do repositório; nada foi gravado.')
    return separator.join([head]+report(violations))


class Models:
    """Models of the repositories of one service, one download per digest."""

    def __init__(self):
        self.lock=threading.Lock()
        self.documents={}
        self.last=None
        # Full documents downloaded (the `?known=` answers are not counted).
        self.downloads=0

    def repository(self,client,repo):
        """(model document or None, required fields per class) of `repo`."""
        with self.lock:
            known=self.last if self.last in self.documents else None
            answer=client.request('/repos/'+str(repo)+'/model'+('?known='+quote(known,safe='') if known else ''))
            document=answer.get('model')
            if document is None: return None,{}
            digest=document.get('digest')
            if document.get('unchanged') and digest in self.documents:
                document=self.documents[digest]
            else:
                if document.get('unchanged'):
                    # The digest is not the one asked about: read it whole.
                    document=client.request('/repos/'+str(repo)+'/model').get('model')
                    if document is None: return None,{}
                    digest=document.get('digest')
                if len(self.documents)>=CACHE_MAX: self.documents.clear()
                self.documents[digest]=document; self.downloads+=1
            self.last=digest
            return document,answer.get('required') or {}

    def rules(self,client,repo,spec):
        """ClassRules of the class `spec` (API dataset) in `repo`, or None without model."""
        document,required=self.repository(client,repo)
        if document is None: return None
        return class_rules(document,required,spec)


def class_rules(document,required,spec):
    kinds={field['name']:field['kind'] for field in spec.get('fields') or []}
    return ClassRules(spec['name'],kinds,document,(required or {}).get(spec['name']) or ())
