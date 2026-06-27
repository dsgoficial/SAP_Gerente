# -*- coding: utf-8 -*-
"""Logica pura (sem Qt/qgis) dos widgets de metadado da carta ortoimagem.

Fica separada dos widgets para ser testavel fora do QGIS (os widgets importam
daqui). Cobre: o universo de classes complementares (camadas opcionais), o
casamento de uma lista por conteudo, e a conversao do quadro de fases.

Fonte do universo: doc_ortoimagem/docs/intro.md (Classes Opcionais) e o seed
'Padrao DSG' em sap/er/metadado.sql. Os nomes ja vem com sufixo de geometria
(_p ponto, _l linha, _a area), que e o formato gravado no banco e no JSON de
edicao.
"""

# Conjunto que o seed 'Padrao DSG' traz (fallback caso o backend nao tenha a
# lista; o default real e lido do backend pelo nome 'Padrao DSG').
PADRAO_DSG_FALLBACK = [
    'llp_unidade_federacao_a',
    'elemnat_curva_nivel_l',
    'elemnat_ponto_cotado_p',
    'infra_pista_pouso_p',
    'infra_pista_pouso_l',
    'infra_pista_pouso_a',
    'elemnat_toponimo_fisiografico_natural_p',
    'elemnat_toponimo_fisiografico_natural_l',
    'elemnat_ilha_p',
    'elemnat_ilha_a',
    'llp_aglomerado_rural_p',
    'llp_area_pub_militar_a',
    'infra_elemento_energia_p',
    'infra_elemento_energia_l',
    'infra_elemento_energia_a',
    'constr_extracao_mineral_p',
    'constr_extracao_mineral_a',
    'llp_nome_local_p',
    'infra_elemento_infraestrutura_p',
    'infra_elemento_infraestrutura_l',
    'infra_elemento_infraestrutura_a',
    'elemnat_elemento_hidrografico_p',
    'elemnat_elemento_hidrografico_l',
    'elemnat_elemento_hidrografico_a',
]

# Classes opcionais da doc que NAO estao no Padrao DSG (o editor pode adicionar).
EXTRAS_CLASSES_COMPLEMENTARES = [
    'elemnat_terreno_sujeito_inundacao_a',
    'edicao_limite_legal_l',
    'edicao_area_pub_militar_l',
    'edicao_terra_indigena_l',
    'llp_terra_indigena_a',
    'edicao_unidade_conservacao_l',
    'llp_unidade_conservacao_a',
]

# Universo completo das camadas opcionais (Padrao DSG + extras), ordenado. E a
# base do checklist; em tempo de execucao ainda se une com o que vier do backend
# e com a selecao atual do alvo, para nunca esconder uma classe ja gravada.
UNIVERSO_CLASSES_COMPLEMENTARES = sorted(
    set(PADRAO_DSG_FALLBACK) | set(EXTRAS_CLASSES_COMPLEMENTARES)
)


def universoChecklist(chosen=None, lists=None):
    """Universo a exibir no checklist: uniao do universo conhecido, das classes
    de todas as listas do backend e da selecao atual (nada e escondido)."""
    universo = set(UNIVERSO_CLASSES_COMPLEMENTARES)
    for lst in (lists or []):
        universo.update(lst.get('classes') or [])
    universo.update(chosen or [])
    # descarta None/vazio (um classes[] do backend com elemento NULL faria o
    # sorted() comparar None com str e estourar TypeError, derrubando o dialogo)
    return sorted(c for c in universo if c)


def resolveClassesListaId(chosen, lists):
    """Retorna o id da lista cujo conjunto de classes bate exatamente com
    `chosen`, ou None se nenhuma bate (precisa criar). Havendo varias, devolve
    a de maior id (mais recente) para casar com o fluxo criar-e-rebuscar."""
    alvo = set(chosen or [])
    candidatos = [
        lst.get('id')
        for lst in (lists or [])
        if set(lst.get('classes') or []) == alvo and lst.get('id') is not None
    ]
    return max(candidatos) if candidatos else None


def _strip(valor):
    return str(valor).strip() if valor is not None else ''


def cleanStringList(values):
    """Strip + descarta vazios, preservando a ordem. Usado pelos editores de
    lista (dados_terceiro, observacoes) no lugar do split por linha."""
    saida = []
    for v in (values or []):
        s = _strip(v)
        if s:
            saida.append(s)
    return saida


def quadroFasesFromDict(qf):
    """Normaliza o quadro_fases (dict {'fases':[...]}, lista nua ou None) numa
    lista de fases [{'nome', 'executantes':[{'nome','ano'}]}] para a arvore."""
    if isinstance(qf, dict):
        fases = qf.get('fases') or []
    elif isinstance(qf, list):
        fases = qf
    else:
        fases = []
    saida = []
    for fase in fases:
        if not isinstance(fase, dict):
            continue
        executantes = []
        for ex in (fase.get('executantes') or []):
            if not isinstance(ex, dict):
                continue
            executantes.append({'nome': _strip(ex.get('nome')), 'ano': _strip(ex.get('ano'))})
        saida.append({'nome': _strip(fase.get('nome')), 'executantes': executantes})
    return saida


def quadroFasesToDict(fases):
    """Converte a lista de fases da arvore em {'fases':[...]}, descartando fases
    e executantes vazios (sem nome/ano)."""
    saida = []
    for fase in (fases or []):
        nome = _strip(fase.get('nome'))
        executantes = []
        for ex in (fase.get('executantes') or []):
            exNome = _strip(ex.get('nome'))
            exAno = _strip(ex.get('ano'))
            if exNome or exAno:
                executantes.append({'nome': exNome, 'ano': exAno})
        if nome or executantes:
            saida.append({'nome': nome, 'executantes': executantes})
    return {'fases': saida}
