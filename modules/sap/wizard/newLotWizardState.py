# Núcleo do wizard "Novo Lote": estado, ordem e regras.
# Sem Qt e sem HTTP de propósito, para poder ser exercitado fora do QGIS.

PAGE_LOT = 1
PAGE_PROFILES = 2
PAGE_PRODUCTS = 3
PAGE_WORK_UNITS = 4
PAGE_ACTIVITIES = 5

ALL_PAGES = [PAGE_LOT, PAGE_PROFILES, PAGE_PRODUCTS, PAGE_WORK_UNITS, PAGE_ACTIVITIES]

PAGE_NAMES = {
    PAGE_LOT: 'Lote, banco e bloco',
    PAGE_PROFILES: 'Perfis e etapas',
    PAGE_PRODUCTS: 'Produtos',
    PAGE_WORK_UNITS: 'Unidades de trabalho',
    PAGE_ACTIVITIES: 'Atividades'
}

# Padrão de CQ, como o backend entende (POST /projeto/etapas/padrao).
CQ_SEM_REVISAO = 1
CQ_REVISAO_CORRECAO = 2
CQ_REVISAO = 3

CQ_NAMES = {
    CQ_SEM_REVISAO: 'Sem controle de qualidade',
    CQ_REVISAO_CORRECAO: 'Uma Revisão e uma Correção',
    CQ_REVISAO: 'Uma Revisão'
}

CQ_DEFAULT = CQ_REVISAO_CORRECAO

# Campos que a camada de produtos precisa mapear.
PRODUCT_FIELDS = ['uuid', 'nome', 'mi', 'inom', 'denominador_escala', 'edicao']

# Campos da camada de UT gerada pelo plugin: os nomes já são os do payload,
# então o mapeamento é identidade e o gerente não precisa casar campo a campo.
WORK_UNIT_FIELDS = [
    'nome', 'epsg', 'observacao', 'dado_producao_id', 'bloco_id',
    'disponivel', 'prioridade', 'dificuldade', 'tempo_estimado_minutos'
]

STATUS_EM_EXECUCAO = 1

# Banco de dados PostGIS com controle de permissões (dominio.tipo_dado_producao).
# É o tipo do banco de edição da produção, e o default ao cadastrar uma conexão.
TIPO_DADO_PRODUCAO_PADRAO = 2

# Escalas do mapeamento sistemático. O índice é a posição no enum do algoritmo
# dsgtools:gridzonegenerator (START_SCALE/STOP_SCALE).
SCALE_OPTIONS = [
    ('1:250.000', 250000, 2),
    ('1:100.000', 100000, 3),
    ('1:50.000', 50000, 4),
    ('1:25.000', 25000, 5),
    ('1:10.000', 10000, 6),
    ('1:5.000', 5000, 7),
    ('1:2.000', 2000, 8),
    ('1:1.000', 1000, 9),
]

# Como a tela de produtos obtém as folhas.
PRODUCT_SOURCE_LAYER = 'layer'
PRODUCT_SOURCE_MI = 'mi'


class NewLotWizardState:
    """O que já foi criado no SAP, e o que isso libera."""

    def __init__(self):
        self.lotId = None
        self.lotName = None
        self.lotScale = None
        self.productionLineId = None
        self.productionDataId = None
        self.blockId = None
        self.profilesApplied = False
        self.profilesSkipped = False
        self.productsLoaded = 0
        self.workUnitsLoaded = 0
        self.activitiesCreated = False

    def isPageDone(self, page):
        if page == PAGE_LOT:
            return bool(self.lotId and self.blockId and self.productionDataId)
        if page == PAGE_PROFILES:
            return bool(self.profilesApplied or self.profilesSkipped)
        if page == PAGE_PRODUCTS:
            return self.productsLoaded > 0
        if page == PAGE_WORK_UNITS:
            return self.workUnitsLoaded > 0
        if page == PAGE_ACTIVITIES:
            return self.activitiesCreated
        return False

    def missingRequirements(self, page):
        """O que falta para ENTRAR na página. Nunca depende do que a própria
        página vai produzir: essa confusão travou a versão anterior do wizard."""
        missing = []
        if page == PAGE_LOT:
            return missing
        if not self.isPageDone(PAGE_LOT):
            missing.append('criar o lote, o banco e o bloco')
            return missing
        if page == PAGE_PROFILES:
            return missing
        if not self.isPageDone(PAGE_PROFILES):
            missing.append('aplicar os perfis e as etapas')
            return missing
        if page == PAGE_PRODUCTS:
            return missing
        if not self.isPageDone(PAGE_PRODUCTS):
            missing.append('carregar os produtos')
            return missing
        if page == PAGE_WORK_UNITS:
            return missing
        if not self.isPageDone(PAGE_WORK_UNITS):
            missing.append('carregar as unidades de trabalho')
        return missing

    def canEnterPage(self, page):
        return len(self.missingRequirements(page)) == 0

    def nextPage(self):
        for page in ALL_PAGES:
            if not self.isPageDone(page):
                return page
        return None

    def isComplete(self):
        return all(self.isPageDone(p) for p in ALL_PAGES)


# ---- regras puras ---------------------------------------------------------

def parseInt(text, minimum=None):
    """Inteiro, ou None se inválido. `minimum` recusa valores abaixo do limite."""
    try:
        value = int(str(text).strip())
    except (AttributeError, TypeError, ValueError):
        return None
    if minimum is not None and value < minimum:
        return None
    return value


def validateLotForm(name, alias, description, scaleText, projectId, productionLineId):
    """Erros do formulário do lote, em linguagem de quem preenche."""
    errors = []
    if not (name or '').strip():
        errors.append('Informe o nome do lote.')
    if not (alias or '').strip():
        errors.append('Informe a abreviação do lote.')
    if not (description or '').strip():
        errors.append('Informe a descrição do lote.')
    if parseInt(scaleText, minimum=1) is None:
        errors.append('A escala deve ser um número inteiro positivo, sem pontos (ex.: 50000).')
    if not projectId:
        errors.append('Escolha o projeto.')
    if not productionLineId:
        errors.append('Escolha a linha de produção.')
    return errors


def validateBlockForm(name, priorityText):
    errors = []
    if not (name or '').strip():
        errors.append('Informe o nome do bloco.')
    if parseInt(priorityText) is None:
        errors.append('A prioridade do bloco deve ser um número inteiro.')
    return errors


def validateProductionDataForm(ip, port, dbName):
    errors = []
    if not (ip or '').strip():
        errors.append('Informe o endereço do banco.')
    if parseInt(port, minimum=1) is None:
        errors.append('A porta do banco deve ser um número inteiro.')
    name = (dbName or '').strip()
    if not name:
        errors.append('Informe o nome do banco.')
    elif name[0].isdigit() or name != name.lower() or not name.replace('_', '').isalnum():
        errors.append('O nome do banco deve ser minúsculo, sem acento, sem espaço e não pode começar com número.')
    return errors


def modelLotCandidates(lots, productionLineId, targetLotId):
    """Lotes que podem servir de modelo: mesma linha de produção e não o próprio.

    Espelha a regra do backend em copiarConfiguracaoLote.
    """
    candidates = []
    for lot in lots:
        if lot.get('linha_producao_id') != productionLineId:
            continue
        if targetLotId is not None and lot.get('id') == targetLotId:
            continue
        candidates.append(lot)
    return candidates


def autoMapFields(layerFieldNames, wantedFields):
    """Casa os campos da camada com os que o SAP espera, pelo nome.

    Compara sem diferenciar maiúsculas nem espaços. O que não casar volta
    vazio, para o gerente escolher.
    """
    normalized = {}
    for fieldName in layerFieldNames:
        normalized[str(fieldName).strip().lower()] = fieldName
    mapping = {}
    for wanted in wantedFields:
        mapping[wanted] = normalized.get(wanted, '')
    return mapping


def missingUuidCount(features):
    """Feições sem o uuid canônico do produto (que vem da planilha de produção)."""
    return len([f for f in features if not str(f.get('uuid') or '').strip()])


def existingWorkUnitsBySubphase(workUnits, subphaseIds=None):
    """Quantas UTs o lote já tem, por subfase.

    A tabela unidade_trabalho não tem restrição de unicidade: repetir o
    carregamento duplica em silêncio. Passe `subphaseIds` para restringir às
    subfases que se pretende carregar.
    """
    counts = {}
    wanted = set(subphaseIds) if subphaseIds is not None else None
    for workUnit in workUnits:
        subphaseId = workUnit.get('subfase_id')
        if wanted is None or subphaseId in wanted:
            counts[subphaseId] = counts.get(subphaseId, 0) + 1
    return counts


def validateWorkUnitLayer(featureCount, geometryTypeName, epsg):
    """Confere a camada de UT antes de gravar."""
    errors = []
    if not featureCount:
        errors.append('A camada não tem feições.')
    if geometryTypeName != 'Polygon':
        errors.append(
            'A geometria deve ser Polygon (o SAP recusa MultiPolygon na unidade de trabalho). '
            'Encontrado: {0}.'.format(geometryTypeName))
    if not epsg:
        errors.append('A camada não tem EPSG definido.')
    return errors


def parseMiList(text):
    """Lê a lista de MI separada por vírgula (aceita ponto e vírgula e quebra de linha).

    Devolve (lista sem repetição e na ordem digitada, lista de repetidos).
    """
    if not text:
        return [], []
    raw = text.replace(';', ',').replace('\n', ',').replace('\t', ',')
    seen = []
    duplicated = []
    for part in raw.split(','):
        mi = part.strip()
        if not mi:
            continue
        if mi in seen:
            if mi not in duplicated:
                duplicated.append(mi)
            continue
        seen.append(mi)
    return seen, duplicated


def validateMiList(text):
    """Erros da lista de MI, em linguagem de quem preenche."""
    miList, duplicated = parseMiList(text)
    errors = []
    if not miList:
        errors.append('Informe ao menos um MI, separado por vírgula (ex.: 2965-1, 2965-2).')
    if duplicated:
        errors.append('MI repetido na lista: {0}.'.format(', '.join(duplicated)))
    return errors


def findByName(records, name, key='nome'):
    """Acha o registro recém-criado na relista (o POST não devolve o id)."""
    for record in records or []:
        if record.get(key) == name:
            return record
    return None
