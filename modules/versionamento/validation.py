"""Topological validation of a merge, as the panel words it (no QGIS imports).

A service started with the validator (capability `topology_validation`)
validates the candidate of a merge by the rules of the DSG Topology core
(constitution 4.3, D018). The validation is a warning: whatever it says, the
merge stays available. A session carries the summary of the receipt recorded
for it; the whole receipt, with the problems, is read on demand
(`GET /repos/{id}/sessions/{sid}/validation`).

A failed validation and an inconclusive one are different things: the first
found problems where the context is complete, the second could not conclude
for lack of context (a layer or attribute the rules require and the
repository lacks, a class the clone left out, the area of the clone, the
window of the evaluation). The texts here keep them apart.

A box asked for on demand is a real frame (D037): its border closes the
faces and every one is judged, and still the result is never an approval.
The windows a merge grows around what it changes are evaluation windows: a
face they cut is not judged.
"""

CAPABILITY='topology_validation'
# Name of a problem of the rules.
KINDS={'face_conflict':'Face com centroides de atributos diferentes','face_without_centroid':'Face sem centroide',
       'centroid_on_edge':'Centroide sobre uma aresta','dangling_delimiter':'Delimitador solto',
       'centroid_without_face':'Centroide fora de face fechada','open_face':'Face aberta',
       'duplicate_geocodigo':'Geocódigo duplicado','source_not_evaluated':'Feição não avaliada pelo motor'}
# Why a result is inconclusive: context the repository does not have.
REASONS={'class_coverage':'contexto das regras ausente ou incompleto neste repositório','coverage_area':'face cortada pela área do clone',
         'evaluation_window':'face cortada pela janela de avaliação','coverage_area_unsupported':'área do clone de forma não suportada',
         'source_rejected':'feição recusada pelo motor'}
LIMITS=dict(REASONS,coverage_area='a área do clone corta faces',evaluation_window='avaliação limitada a uma caixa ou a uma janela',
            mask_context_window='o contexto das classes que mascaram foi suposto dentro da janela de avaliação',
            budget='o orçamento de fontes e vértices foi atingido',
            no_rule_class_in_scope='nenhuma classe das regras topológicas está no escopo')
CHANGES={'introduced':'Introduzido por esta integração','persisting':'Já existia no destino','resolved':'Resolvido por esta integração',
         'became_inconclusive':'Ficou inconclusivo (perda de contexto)','unclassified':'Sem comparação'}
ORIGINS={'preparation':'Validação da preparação, gravada com a sessão.',
         'apply':'Validação do que foi aplicado, com todas as decisões; está no recibo do merge.',
         'refresh':'Validação de agora, com as decisões já tomadas; não fica gravada (a do recibo sai na aplicação).',
         'repository':'Validação do estado atual do repositório, sem comparação.'}
# Why a class of the rules is a dependency this repository cannot satisfy.
DEPENDENCIES={'class_outside_selection':'classes das regras fora da seleção deste clone',
              'layer_absent':'camadas exigidas pelas regras que este repositório não tem',
              'attribute_absent':'atributos exigidos pelas regras ausentes das classes',
              'attribute_filter':'classes com filtro de atributo neste clone',
              'unsupported_srid':'classes em CRS diferente do das regras (EPSG:4674)',
              'source_rejected':'classes com feição recusada pelo motor'}
# Layers named per reason; the rest is counted.
LISTED_LAYERS=6
STATUSES={'approved':'aprovada','failed':'reprovada','incomplete':'inconclusiva','not_evaluated':'não avaliada'}
HEADERS=['Tipo','Classe','Situação','Classificação','Feições']
ADVICE=' O merge continua disponível: a validação avisa e não bloqueia (D018).'


WINDOW='evaluation_window'


def window_faces(receipt):
    """The faces the window of the evaluation cuts (a validation by box):
    not judged, and not errors."""
    return [p for p in (receipt or {}).get('problems') or [] if p.get('status')=='incomplete' and p.get('reason')==WINDOW]


def listed_problems(receipt):
    """The problems shown as a list: every one but the faces the window cuts."""
    cut=window_faces(receipt)
    return [p for p in (receipt or {}).get('problems') or [] if p not in cut]


def window_only(summary, receipt):
    """Whether only the window (with the masks judged inside it) keeps a
    validation from concluding."""
    coverage=(receipt or {}).get('coverage') or {}
    limits=coverage.get('limits') or []
    return (bool(receipt) and WINDOW in limits and all(limit in (WINDOW,'mask_context_window') for limit in limits) and not coverage.get('dependencies')
            and coverage.get('area') in (None,'none') and len(window_faces(receipt))==summary.get('incomplete'))


def window_text(receipt):
    """The group of the faces not judged by the box, collapsed to one text; '' without any."""
    cut=window_faces(receipt)
    if not cut: return ''
    named=[str(f['class'])+' · '+str(f['dsg_id']) for p in cut for f in p.get('features') or []]
    return ('Não julgado pela caixa ('+str(len(cut))+' faces na borda): estas faces encostam na borda da caixa avaliada, não foram '
            'julgadas e não são erros; o veredito conclusivo vem da validação sem caixa, do repositório inteiro.'+
            (' Feições nelas: '+'; '.join(named[:12])+(' e mais '+str(len(named)-12) if len(named)>12 else '')+'.' if named else ''))


def summary_of(receipt):
    """The summary of a whole receipt, in the shape a session carries."""
    return dict(receipt['summary'],unresolved=receipt['candidate']['unresolved'],limits=receipt['coverage']['limits'],
                area=receipt['coverage']['area'],error=receipt.get('error'))


def limit_text(limit):
    code,_,detail=str(limit).partition(':')
    return LIMITS.get(code,code)+(' ('+detail.strip()+')' if detail.strip() else '')


def limits_of(summary, receipt=None):
    """What limits a validation: the area of the clone, the classes it lacks, the window."""
    coverage=(receipt or {}).get('coverage') or {'limits':summary.get('limits') or [],'area':summary.get('area'),'dependencies':[]}
    out=[]
    if coverage.get('area') and coverage['area']!='none':
        out.append('a cobertura deste repositório é limitada pela área do clone')
    out+=[limit_text(limit) for limit in coverage.get('limits') or []]
    grouped={}
    for item in coverage.get('dependencies') or []:
        layers=grouped.setdefault(str(item.get('reason')),[])
        if item.get('layer') not in layers: layers.append(item.get('layer'))
    for reason,layers in grouped.items():
        out.append(DEPENDENCIES.get(reason,reason)+' ('+str(len(layers))+'): '+', '.join(str(layer) for layer in layers[:LISTED_LAYERS])+
                   (' e mais '+str(len(layers)-LISTED_LAYERS) if len(layers)>LISTED_LAYERS else ''))
    return out


def status_text(summary, origin, receipt=None):
    """The status of a validation in words."""
    advice='' if origin=='repository' else ADVICE
    status=summary.get('status')
    if summary.get('error'):
        return 'Validação topológica não avaliada: o validador falhou ('+str(summary['error'])+').'+advice
    if status=='approved':
        return 'Validação topológica aprovada: nada reprovado nem inconclusivo no que foi avaliado.'
    if status=='failed':
        return ('Validação topológica reprovada: '+str(summary['failed'])+' problema(s) em faces e feições com contexto completo'+
                (', e '+str(summary['incomplete'])+' resultado(s) inconclusivo(s)' if summary.get('incomplete') else '')+'.'+advice)
    if status=='incomplete' and window_only(summary,receipt) and not summary.get('incomplete'):
        return ('Validação topológica incompleta: avaliação por caixa. A borda da caixa fecha as faces, todas foram julgadas e nada '
                'foi reprovado; uma caixa nunca aprova. O veredito conclusivo vem da validação sem caixa (o repositório inteiro).'+advice)
    if status=='incomplete' and window_only(summary,receipt):
        return ('Validação topológica incompleta: avaliação por caixa. Nada foi reprovado nas faces que a caixa não corta, e '+
                str(summary['incomplete'])+' face(s) na borda não foram julgadas. O veredito conclusivo vem da validação sem caixa '
                '(o repositório inteiro).'+advice)
    if status=='incomplete':
        missing=any(item.get('reason') in ('layer_absent','attribute_absent') for item in ((receipt or {}).get('coverage') or {}).get('dependencies') or [])
        return ('Validação topológica inconclusiva: falta contexto para concluir '+
                (str(summary['incomplete'])+' resultado(s)' if summary.get('incomplete') else 'as classes que dependem dele')+
                ', e nada foi reprovado onde o contexto é completo. Não é aprovação nem reprovação'+
                ('; faltam camadas ou atributos que as regras exigem, e camada sem classe não é camada vazia.' if missing else
                 '; o veredito é de um repositório com cobertura inteira (o pai).' if origin=='repository' else '.')+advice)
    why=limits_of(summary,receipt)
    nothing=('o repositório não tem dado de nenhuma classe das regras topológicas' if origin=='repository' else
             'a integração não altera nenhuma classe das regras topológicas')
    why=[nothing if text==LIMITS['no_rule_class_in_scope'] else text for text in why]
    return 'Validação topológica não avaliada: '+('; '.join(why) if why else 'nada a avaliar')+'.'


def band_text(summary, origin, receipt=None):
    """The band of a validation: the status, the four counts, the limits, the
    open conflicts and where the receipt comes from, one per line."""
    lines=[status_text(summary,origin,receipt),
           str(summary.get('introduced',0))+' introduzido(s) · '+str(summary.get('resolved',0))+' resolvido(s) · '+
           str(summary.get('persisting',0))+' persistente(s) · '+str(summary.get('incomplete',0))+' inconclusivo(s)']
    limits=limits_of(summary,receipt)
    if limits: lines.append('Limites desta validação: '+'; '.join(limits)+'.')
    unresolved=((receipt or {}).get('candidate') or {}).get('unresolved',summary.get('unresolved') or 0)
    if unresolved:
        lines.append(str(unresolved)+' conflito(s) estava(m) em aberto nesta validação: cada um conta como o estado do destino '
                     'até a decisão. Depois de decidir, valide de novo.')
    if ORIGINS.get(origin): lines.append(ORIGINS[origin])
    cut=window_text(receipt)
    if cut: lines.append(cut)
    return '\n'.join(lines)


def problem_status(problem):
    status=problem.get('status')
    if status=='failed': return 'Reprovado'
    if status=='incomplete': return 'Inconclusivo: '+REASONS.get(problem.get('reason'),problem.get('reason') or 'falta contexto')
    return 'Sem problema agora'


def problem_row(problem):
    """A problem as a row: kind, rule class, status, classification, features."""
    features='; '.join(str(f['class'])+' · '+str(f['dsg_id']) for f in problem.get('features') or []) or 'a face, sem feição própria'
    return (KINDS.get(problem.get('kind'),str(problem.get('kind'))),str(problem.get('rule_class')),problem_status(problem),
            CHANGES.get(problem.get('change'),str(problem.get('change'))),features)


def apply_note(summary):
    """What the apply dialog says of a validation that did not approve, or ''."""
    if not summary or summary.get('status') not in ('failed','incomplete'): return ''
    found=('reprovada ('+str(summary['failed'])+' problema(s))' if summary['status']=='failed' else
           'inconclusiva ('+str(summary['incomplete'])+' resultado(s) sem contexto)')
    return ('A validação topológica deste candidato está '+found+'; o merge pode ser aplicado mesmo assim, '
            'e o recibo guarda o que foi encontrado (D018).')
