import os, io, json, zipfile, datetime
from qgis.PyQt import QtCore, QtWidgets
from SAP_Gerente.widgets.dockWidget import DockWidget

# dominio.tipo_produto (ver er/dominio.sql no repo sap)
_TIPO_PRODUTO_CT = 2          # Carta Topográfica - T34-700
_TIPO_PRODUTO_CO = 3          # Carta Ortoimagem
_TIPO_PRODUTO_MGCP = 8        # Conjunto de dados geoespaciais vetoriais - MGCP
_TIPOS_PRODUTO_VETOR_TOPO = (1, 7)   # EDGV 2.1.3 / EDGV 3.0
_TIPO_PRODUTO_VETOR_ORTO = 22        # EDGV 3.0 para Ortoimagem

_CRS_CRS84 = {
    "type": "name",
    "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
}


def _escalaLabel(denominador):
    try:
        denominador = int(denominador)
    except (TypeError, ValueError):
        return 'sem_escala'
    if denominador % 1000 == 0:
        return '{0}k'.format(denominador // 1000)
    return str(denominador)


def _classificarLote(lote):
    """Retorna (categoria, papel) do lote, onde papel é 'vetor' (produto
    intermediário, ex.: CDGV) ou 'final' (produto de disseminação, ex.: CT/CO).
    Lotes vetoriais são combinados com o produto final correspondente na
    mesma categoria (mesma escala): a feição do produto final prevalece,
    exceto quando ainda está 'Previsto' e o vetor já tem situação real."""
    tipoProdutoId = lote.get('tipo_produto_id')
    escala = _escalaLabel(lote.get('denominador_escala'))

    if tipoProdutoId == _TIPO_PRODUTO_CT:
        return 'ct_{0}'.format(escala), 'final'
    if tipoProdutoId == _TIPO_PRODUTO_CO:
        return 'co_{0}'.format(escala), 'final'
    if tipoProdutoId in _TIPOS_PRODUTO_VETOR_TOPO:
        return 'ct_{0}'.format(escala), 'vetor'
    if tipoProdutoId == _TIPO_PRODUTO_VETOR_ORTO:
        return 'co_{0}'.format(escala), 'vetor'
    if tipoProdutoId == _TIPO_PRODUTO_MGCP:
        return 'mgcp_{0}'.format(escala), 'final'
    return None, None


def _escolherFeicao(candidatos):
    finaisComSituacao = [
        f for f in candidatos
        if f['_papel'] == 'final' and f['properties'].get('situacao') != 'Previsto'
    ]
    if finaisComSituacao:
        return finaisComSituacao[0]
    vetoresComSituacao = [
        f for f in candidatos
        if f['_papel'] == 'vetor' and f['properties'].get('situacao') != 'Previsto'
    ]
    if vetoresComSituacao:
        return vetoresComSituacao[0]
    finais = [f for f in candidatos if f['_papel'] == 'final']
    if finais:
        return finais[0]
    return candidatos[0]


class ExportarProdutosGeoJson(DockWidget):

    def __init__(self, sapCtrl, sap):
        super(ExportarProdutosGeoJson, self).__init__(controller=sapCtrl)
        self.sap = sap
        self._pits = self.sap.getPITs() or []
        self.setWindowTitle('Exportar Produtos (GeoJSON)')
        self._loadAnos()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "exportarProdutosGeoJson.ui"
        )

    def getCurrentYear(self):
        return datetime.datetime.now().year

    def _loadAnos(self):
        self.anoCb.clear()
        self.anoCb.addItem('Todos', None)
        anos = sorted({int(pit['ano']) for pit in self._pits if pit.get('ano') is not None}, reverse=True)
        for ano in anos:
            self.anoCb.addItem(str(ano), ano)
        currentIndex = self.anoCb.findData(self.getCurrentYear())
        if currentIndex != -1:
            self.anoCb.setCurrentIndex(currentIndex)

    def clearInput(self):
        pass

    def validInput(self):
        return True

    def runFunction(self):
        ano = self.anoCb.itemData(self.anoCb.currentIndex())

        destDir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Selecione a pasta de destino')
        if not destDir:
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            zipBytes = self.sap.getDadosSiteAcompanhamentoZip()
            if not zipBytes:
                QtWidgets.QMessageBox.critical(self, 'Erro', 'Não foi possível obter os dados do servidor.')
                return

            loteIdsDoAno = None
            if ano is not None:
                loteIdsDoAno = {
                    pit.get('lote_id') for pit in self._pits
                    if pit.get('ano') is not None and int(pit['ano']) == ano
                }

            lotes = self.sap.getAllLots() or []
            if loteIdsDoAno is not None:
                lotes = [lote for lote in lotes if lote.get('id') in loteIdsDoAno]

            categorias = {}  # categoria -> lista de feicoes (com _papel anotado)
            with zipfile.ZipFile(io.BytesIO(zipBytes)) as arquivoZip:
                nomesNoZip = set(arquivoZip.namelist())
                for lote in lotes:
                    categoria, papel = _classificarLote(lote)
                    if categoria is None:
                        continue
                    nomeArquivo = '{0}.geojson'.format(lote.get('id'))
                    if nomeArquivo not in nomesNoZip:
                        continue
                    geojson = json.loads(arquivoZip.read(nomeArquivo))
                    for feicao in geojson.get('features', []):
                        feicao['_papel'] = papel
                        categorias.setdefault(categoria, []).append(feicao)

            if not categorias:
                QtWidgets.QMessageBox.warning(self, 'Aviso', 'Nenhum produto encontrado para o ano selecionado.')
                return

            for categoria, feicoes in categorias.items():
                porIdentificador = {}
                for feicao in feicoes:
                    identificador = feicao['properties'].get('identificador')
                    porIdentificador.setdefault(identificador, []).append(feicao)

                feicoesFinais = []
                for identificador, candidatos in porIdentificador.items():
                    escolhida = _escolherFeicao(candidatos)
                    feicoesFinais.append({
                        'type': 'Feature',
                        'geometry': escolhida['geometry'],
                        'properties': {
                            'situacao': escolhida['properties'].get('situacao'),
                            'identificador': identificador,
                            'id': len(feicoesFinais) + 1
                        }
                    })

                saida = {
                    'type': 'FeatureCollection',
                    'name': categoria,
                    'crs': _CRS_CRS84,
                    'features': feicoesFinais
                }
                with open(os.path.join(destDir, '{0}.geojson'.format(categoria)), 'w', encoding='utf-8') as f:
                    json.dump(saida, f, ensure_ascii=False)

            QtWidgets.QMessageBox.information(
                self, 'Sucesso',
                '{0} arquivo(s) GeoJSON exportado(s) com sucesso.'.format(len(categorias))
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao exportar produtos: {str(e)}')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.close()
