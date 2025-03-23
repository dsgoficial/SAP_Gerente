import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget import DockWidget
from qgis.utils import iface
from qgis import core, gui
import datetime

class AdicionarTrack(DockWidget):

    def __init__(self, sapCtrl, sap, qgis):
        super(AdicionarTrack, self).__init__(controller=sapCtrl)
        self.sap = sap
        self.qgis = qgis
        self.setWindowTitle('Adicionar Tracker')
        self.carregarCampos()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "adicionarTrack.ui"
        )
    
    def carregarCampos(self):
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            campos = self.sap.getCampos()
            QtWidgets.QApplication.restoreOverrideCursor()
            if not campos:
                QtWidgets.QMessageBox.warning(self, 'Aviso', 'Não há campos cadastrados.')
                return
            self.campoCb.clear() # Limpar campos
            for campo in campos:
                self.campoCb.addItem(f"{campo['nome']}", campo['id'])
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao carregar campos: {str(e)}')
    
    def clearInput(self):
        self.chefeVtrLe.clear()
        self.motoristaLe.clear()
        self.placaVtrLe.clear()
        self.diaLe.clear()
        self.inicioLe.clear()
        self.fimLe.clear()
        self.campoCb.setCurrentIndex(0)
    
    def validInput(self):
        if self.campoCb.count() == 0:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Não há campos disponíveis para adicionar tracks.')
            return False
        if not self.chefeVtrLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe o Chefe da VTR.')
            return False
        if not self.motoristaLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe o Motorista.')
            return False
        if not self.placaVtrLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe a Placa da VTR.')
            return False
        if not self.diaLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe a Data.')
            return False
        if not self.inicioLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe a Hora de Início.')
            return False
        if not self.fimLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe a Hora de Fim.')
            return False
        try:
            datetime.datetime.strptime(self.diaLe.text(), '%Y-%m-%d')
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Formato de data inválido. Use AAAA-MM-DD')
            return False
        try:
            datetime.datetime.strptime(self.inicioLe.text(), '%H:%M')
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Formato de hora de início inválido. Use HH:MM')
            return False
        try:
            datetime.datetime.strptime(self.fimLe.text(), '%H:%M')
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Formato de hora de fim inválido. Use HH:MM')
            return False
        inicio = datetime.datetime.strptime(self.inicioLe.text(), '%H:%M')
        fim = datetime.datetime.strptime(self.fimLe.text(), '%H:%M')
        if fim <= inicio:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'A hora de fim deve ser posterior à hora de início.')
            return False
        return True
    
    def getTrackData(self):
        campo_id = self.campoCb.currentData()
        
        return {
            'chefe_vtr': self.chefeVtrLe.text(),
            'motorista': self.motoristaLe.text(),
            'placa_vtr': self.placaVtrLe.text(),
            'dia': self.diaLe.text(),
            'inicio': self.inicioLe.text(),
            'fim': self.fimLe.text(),
            'campo_id': campo_id
        }
    
    def runFunction(self):
        if not self.validInput():
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            track_data = self.getTrackData()
            resultado = self.sap.criaTracker(track_data)
            QtWidgets.QMessageBox.information(self, 'Sucesso', f'Tracker criado com sucesso!')
            self.clearInput()
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao criar tracker: {str(e)}')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()