import os, sys, copy, csv, datetime
from qgis.PyQt import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget import DockWidget

class ExportarProducaoDetalhada(DockWidget):

    def __init__(self, sapCtrl, sap):
        super(ExportarProducaoDetalhada, self).__init__(controller=sapCtrl)
        self.sap = sap
        self.setWindowTitle('Exportar Produção Detalhada (PIT)')
        self.loadAnos()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "exportarProducaoDetalhada.ui"
        )

    def getCurrentYear(self):
        return datetime.datetime.now().year

    def loadAnos(self):
        self.anoCb.clear()
        anos = sorted({int(pit['ano']) for pit in self.sap.getPITs()}, reverse=True)
        for ano in anos:
            self.anoCb.addItem(str(ano), ano)
        currentIndex = self.anoCb.findData(self.getCurrentYear())
        if currentIndex != -1:
            self.anoCb.setCurrentIndex(currentIndex)

    def clearInput(self):
        currentIndex = self.anoCb.findData(self.getCurrentYear())
        if currentIndex != -1:
            self.anoCb.setCurrentIndex(currentIndex)

    def validInput(self):
        return self.anoCb.currentData() is not None

    def getAno(self):
        return self.anoCb.currentData()

    def runFunction(self):
        ano = self.getAno()
        if ano is None:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Nenhum ano de PIT disponível para exportação.')
            return

        filePath = QtWidgets.QFileDialog.getSaveFileName(
            self,
            '',
            "producao_Detalhada_{0}.csv".format(ano),
            '*.csv'
        )
        if not filePath[0]:
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            dados = self.sap.getProducaoDetalhada(ano)
            exportar_para_csv(dados, filePath[0])
            QtWidgets.QMessageBox.information(self, 'Sucesso', 'CSV exportado com sucesso.')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao gerar relatório: {str(e)}')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.close()

def formatarEscala(denominador):
    try:
        return "1:{:,}".format(int(denominador)).replace(",", ".")
    except (TypeError, ValueError):
        return ''

def formatarProduto(tipoProduto):
    # tipo_produto.nome traz a especificação após " - " (ex.: "Carta Topográfica - T34-700");
    # o PIT usa apenas o nome curto.
    return str(tipoProduto or '').split(' - ')[0]

def exportar_para_csv(dados, caminho_arquivo):
    cabecalhos = [
        "OMDS", "Demandante", "Meta", "Produto", "MI", "Escala",
        "Projeto (SAP)", "Lote (SAP)", "Bloco (SAP)",
        "Data da Carga (BDGEx)", "ID da Carga (BDGEx)", "Local da Carga",
        "Outra Disponibilização", "Observações"
    ]

    with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        escritor.writerow(cabecalhos)

        for item in dados:
            if not isinstance(item, dict):
                continue
            linha = [
                '',                                        # OMDS (não rastreado no SAP)
                '',                                        # Demandante (não rastreado no SAP)
                item.get('meta', ''),                      # Meta
                formatarProduto(item.get('tipo_produto')), # Produto
                item.get('mi', ''),                        # MI
                formatarEscala(item.get('denominador_escala')),  # Escala
                item.get('projeto', ''),                   # Projeto (SAP)
                item.get('lote', ''),                      # Lote (SAP)
                item.get('bloco') or '',                   # Bloco (SAP)
                '',                                        # Data da Carga (BDGEx)
                '',                                        # ID da Carga (BDGEx)
                '',                                        # Local da Carga
                '',                                        # Outra Disponibilização
                ''                                         # Observações
            ]
            escritor.writerow(linha)
