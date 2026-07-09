# Passos do wizard "Novo Lote", na ordem em que devem ocorrer.
STEP_LOT = 1
STEP_PRODUCTION_DATA = 2
STEP_PROFILES = 3
STEP_DEFAULT_STEPS = 4
STEP_BLOCK = 5
STEP_PRODUCTS = 6
STEP_GENERATE_WORK_UNIT = 7
STEP_LOAD_WORK_UNIT = 8
STEP_ACTIVITIES = 9

STEP_NAMES = {
    STEP_LOT: 'Lote',
    STEP_PRODUCTION_DATA: 'Configuração de conexão',
    STEP_PROFILES: 'Perfis (copiar de lote-modelo)',
    STEP_DEFAULT_STEPS: 'Etapas padrão',
    STEP_BLOCK: 'Bloco',
    STEP_PRODUCTS: 'Produtos',
    STEP_GENERATE_WORK_UNIT: 'Gerar unidades de trabalho',
    STEP_LOAD_WORK_UNIT: 'Carregar unidades de trabalho',
    STEP_ACTIVITIES: 'Atividades'
}

ALL_STEPS = [
    STEP_LOT, STEP_PRODUCTION_DATA, STEP_PROFILES, STEP_DEFAULT_STEPS,
    STEP_BLOCK, STEP_PRODUCTS, STEP_GENERATE_WORK_UNIT,
    STEP_LOAD_WORK_UNIT, STEP_ACTIVITIES
]

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


class NewLotWizardState:
    """Estado e regras do wizard, sem Qt e sem HTTP.

    A camada de interface guarda esta instância e pergunta a ela o que pode
    ser feito. Assim a ordem dos passos e as validações ficam testáveis fora
    do QGIS.
    """

    def __init__(self):
        self.done = set()
        self.lotId = None
        self.productionLineId = None
        self.productionDataId = None
        self.modelLotId = None
        self.profilesSkipped = False
        self.blockId = None
        self.subphaseIds = []
        self.cq = CQ_DEFAULT
        self.generatedLayerName = None
        self.workUnitLayerChecked = False
        self.warnings = []

    # ---- controle de passos -------------------------------------------------

    def isDone(self, step):
        return step in self.done

    def markDone(self, step):
        self.done.add(step)

    def missingRequirements(self, step):
        """Devolve a lista de pendências que impedem entrar no passo."""
        missing = []
        if step == STEP_LOT:
            return missing
        if step == STEP_PRODUCTION_DATA:
            if self.lotId is None:
                missing.append('criar o lote')
            return missing
        if step == STEP_PROFILES:
            if self.lotId is None:
                missing.append('criar o lote')
            return missing
        if step == STEP_DEFAULT_STEPS:
            if self.lotId is None:
                missing.append('criar o lote')
            if not (self.isDone(STEP_PROFILES) or self.profilesSkipped):
                missing.append('copiar os perfis (ou marcar que não há lote-modelo)')
            return missing
        if step == STEP_BLOCK:
            if self.lotId is None:
                missing.append('criar o lote')
            return missing
        if step == STEP_PRODUCTS:
            if self.lotId is None:
                missing.append('criar o lote')
            return missing
        if step == STEP_GENERATE_WORK_UNIT:
            if self.blockId is None:
                missing.append('criar o bloco')
            if self.productionDataId is None:
                missing.append('definir a configuração de conexão')
            return missing
        if step == STEP_LOAD_WORK_UNIT:
            if not self.isDone(STEP_GENERATE_WORK_UNIT):
                missing.append('gerar as unidades de trabalho')
            if not self.workUnitLayerChecked:
                missing.append('conferir a camada de unidades de trabalho')
            # As subfases NÃO entram aqui: quem as escolhe é a própria ferramenta
            # "Carregar Unidades de Trabalho", que só abre depois deste teste.
            # Exigi-las aqui travava o passo (não abria a ferramenta que grava a
            # UT, e sem UT gravada a conferência também não passava).
            return missing
        if step == STEP_ACTIVITIES:
            if not self.isDone(STEP_LOAD_WORK_UNIT):
                missing.append('carregar as unidades de trabalho')
            if not self.isDone(STEP_DEFAULT_STEPS):
                missing.append('criar as etapas padrão')
            return missing
        return missing

    def canEnterStep(self, step):
        return len(self.missingRequirements(step)) == 0

    def nextStep(self):
        for step in ALL_STEPS:
            if not self.isDone(step):
                return step
        return None


# ---- regras que não dependem do estado ------------------------------------

def modelLotCandidates(lots, productionLineId, targetLotId):
    """Lotes que podem servir de modelo: mesma linha de produção e não o próprio.

    Espelha a regra do backend em copiarConfiguracaoLote (mesma
    linha_producao_id e ids distintos).
    """
    candidates = []
    for lot in lots:
        if lot.get('linha_producao_id') != productionLineId:
            continue
        if targetLotId is not None and lot.get('id') == targetLotId:
            continue
        candidates.append(lot)
    return candidates


def existingWorkUnitsBySubphase(workUnits, subphaseIds=None):
    """Conta, por subfase, quantas UTs o lote já tem.

    Alimentado por GET /projeto/unidade_trabalho?lote_id=N. Serve para avisar
    ANTES de carregar: a tabela unidade_trabalho não tem restrição de
    unicidade, então repetir o carregamento duplica em silêncio.

    `subphaseIds` restringe a contagem às subfases que se pretende carregar.
    Passe None (o padrão) para contar todas: é o que o wizard faz, porque a
    escolha das subfases acontece dentro da ferramenta de carregamento, depois
    do aviso.
    """
    counts = {}
    wanted = set(subphaseIds) if subphaseIds is not None else None
    for workUnit in workUnits:
        subphaseId = workUnit.get('subfase_id')
        if wanted is None or subphaseId in wanted:
            counts[subphaseId] = counts.get(subphaseId, 0) + 1
    return counts


def validateWorkUnitLayer(featureCount, geometryTypeName, epsg):
    """Confere a camada de UT antes de carregar. Devolve lista de erros."""
    errors = []
    if not featureCount:
        errors.append('A camada não tem feições.')
    if geometryTypeName != 'Polygon':
        errors.append(
            'A geometria deve ser Polygon (o backend recusa MultiPolygon na unidade de trabalho). '
            'Encontrado: {0}.'.format(geometryTypeName)
        )
    if not epsg:
        errors.append('A camada não tem EPSG definido.')
    return errors
