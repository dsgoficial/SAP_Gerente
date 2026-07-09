from SAP_Gerente.modules.dsgTools.processingLaunchers.processing import Processing


class GridZoneGenerator(Processing):
    """Gera as molduras do mapeamento sistemático a partir de índices (MI ou INOM).

    O algoritmo aceita vários índices separados por vírgula e devolve uma camada
    de polígonos com os campos `inom` e `mi`.
    """

    def __init__(self):
        super(GridZoneGenerator, self).__init__()
        self.processingId = 'dsgtools:gridzonegenerator'

    def getParameters(self, parameters):
        return {
            'START_SCALE': parameters['scaleIndex'],
            'STOP_SCALE': parameters['scaleIndex'],
            'INDEX_TYPE': parameters.get('indexType', 0),  # 0 = MI/MIR, 1 = INOM
            'INDEX': parameters['index'],
            'CRS': parameters['crs'],
            'XSUBDIVISIONS': None,
            'YSUBDIVISIONS': None,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
