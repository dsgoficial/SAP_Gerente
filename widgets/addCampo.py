import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget import DockWidget
from qgis.utils import iface
from qgis import core, gui

class AdicionarCampo(DockWidget):

    def __init__(self, sapCtrl, sap, qgis):
        super(AdicionarCampo, self).__init__(controller=sapCtrl)
        self.sap = sap
        self.qgis = qgis
        self.setWindowTitle('Adicionar Campo')
        self.loadSituacoes()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "adicionarCampo.ui"
        )

    @QtCore.pyqtSlot(bool)
    def on_extractEWKTBtn_clicked(self):
        layer = iface.activeLayer()
        selectedFeatures = layer.selectedFeatures()
        if len(selectedFeatures) != 1:
            self.showError('Aviso', "Selecione apenas uma feição de campo")
            return
        feat = selectedFeatures[0]
        ewkt = self.qgis.geometryToEwkt( feat.geometry(), layer.crs().authid(), 'EPSG:4326' )
        self.geomLe.setText(ewkt)

    def isValidEWKT(self):
        ewkt = self.ewktLe.text()
        if not ewkt:
            return False
        geom = core.QgsGeometry().fromWkt(ewkt.split(';')[1])
        return geom.isGeosValid()
    
    def clearInput(self):
        self.nomeLe.clear()
        self.descricaoTe.clear()
        self.orgaoLe.clear()
        self.pitLe.clear()
        self.militaresLe.clear()
        self.placasVtrLe.clear()
        self.dataInicioLe.clear()
        self.dataFimLe.clear()
        self.geomLe.clear()
        self.situacaoCb.setCurrentIndex(0)  # Reseta para "Previsto"

    def validInput(self):
        # Verifica se os campos obrigatórios estão preenchidos
        if not self.nomeLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'O campo Nome é obrigatório.')
            return False
        
        if not self.orgaoLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'O campo Órgão é obrigatório.')
            return False
        
        if not self.dataInicioLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'O campo Data Início é obrigatório.')
            return False
        
        if not self.dataFimLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'O campo Data Fim é obrigatório.')
            return False
        
        if self.dataFimLe.text() < self.dataInicioLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'A data de fim não pode ser menor que a data de início.')
            return False
        
        self.isValidEWKT()
        
        return True
    
    def loadSituacoes(self):
        situacoes = self.sap.getSituacoes()
        self.situacaoCb.clear()
        for situacao in situacoes:
            self.situacaoCb.addItem(situacao['nome'], situacao)
    
    # def loadCategorias(self):
    #     try:
    #         categorias = self.sap.getCategorias()  # Método que faz a chamada à API
    #         self.categoriaCb.clear()
    #         
    #         # Verifica se categorias é uma lista de dicionários ou uma lista simples
    #         if categorias and isinstance(categorias[0], dict):
    #             # Se for lista de dicionários, assume que cada dict tem uma chave 'nome' ou 'categoria'
    #             for categoria in categorias:
    #                 if 'nome' in categoria:
    #                     self.categoriaCb.addItem(categoria['nome'], categoria.get('code'))
    #                 elif 'categoria' in categoria:
    #                     self.categoriaCb.addItem(categoria['categoria'], categoria.get('id'))
    #                 else:
    #                     # Primeira chave encontrada
    #                     key = list(categoria.keys())[0]
    #                     self.categoriaCb.addItem(str(categoria[key]))
    #         else:
    #             # Se for lista de strings
    #             for categoria in categorias:
    #                 self.categoriaCb.addItem(str(categoria))
    #                 
    #     except Exception as e:
    #         QtWidgets.QMessageBox.warning(self, 'Aviso', f'Erro ao carregar categorias: {str(e)}')
    #         print(f"Erro detalhado ao carregar categorias: {str(e)}")
    #         # Mostre o tipo de dados que está causando o erro
    #         if categorias:
    #             print(f"Tipo da primeira categoria: {type(categorias[0])}")
    #             print(f"Conteúdo da primeira categoria: {categorias[0]}")


    def getCampoData(self):
        pit_value = None
        if self.pitLe.text():
            pit_value = int(self.pitLe.text())
        # Retorna os dados do campo no formato esperado pelo controlador
        return {
            'nome': self.nomeLe.text(),
            'descricao': self.descricaoTe.toPlainText(),
            'orgao': self.orgaoLe.text(),
            'pit': pit_value,
            'militares': self.militaresLe.text(),
            'placas_vtr': self.placasVtrLe.text(),
            'inicio': self.dataInicioLe.text(),
            'fim': self.dataFimLe.text(),
            'categorias': ['Reambulação', 'Pontos de Controle'],
            'situacao_id': self.situacaoCb.currentData()['code'],
            'geom': self.geomLe.text()
        }
    
    def runFunction(self):
        if not self.validInput():
            return
            
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            campo_data = self.getCampoData()
            resultado = self.sap.criaCampo(campo_data)
            QtWidgets.QMessageBox.information(self, 'Sucesso', f'Campo criado com sucesso! ID: {resultado["id"]}')
            self.clearInput()
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao criar campo: {str(e)}')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()