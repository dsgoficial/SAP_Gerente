import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class CreateWorkUnit(QtWidgets.QWidget):

    def __init__(self, sapCtrl):
        super(CreateWorkUnit, self).__init__()
        self.sapCtrl = sapCtrl
        uic.loadUi(self.getUiPath(), self)
        self.extractProductBtn.setIcon(QtGui.QIcon(self.getIconPath()))
        self.extractProductBtn.setIconSize(QtCore.QSize(24,24))
        self.extractProductBtn.setToolTip('Extrair valores mediante seleções')
        self.extractSubfaseBtn.setIcon(QtGui.QIcon(self.getIconPath()))
        self.extractSubfaseBtn.setIconSize(QtCore.QSize(24,24))
        self.extractSubfaseBtn.setToolTip('Extrair valores mediante seleções')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createWorkUnit.ui"
        )

    def getIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'extract.png'
        )
        
    def showMessageErro(self, title, text):
        QtWidgets.QMessageBox.critical(
            self,
            title, 
            text
        )

    def clearInput(self):
        self.productIdLe.setText('')
        self.divisionLe.setText('')
        self.overlapLe.setText('')
        self.shiftLe.setText('')
        self.subfaseLe.setText('')

    def validInput(self):
        return  (
            self.productIdLe.text()
            and
            self.divisionLe.text()
            and
            self.overlapLe.text()
            and
            self.shiftLe.text()
            and
            self.subfaseLe.text()
        )

    def getInputData(self):
        return {
            'productsIds' : [ int(d) for d in self.productIdLe.text().split(',') ],
            'subfasesIds' : [ int(d) for d in self.subfaseLe.text().split(',') ],
            'division' : self.divisionLe.text(),
            'overlap' : self.overlapLe.text(),
            'shift' : self.shiftLe.text(),
        }

    def runFunction(self):
        self.sapCtrl.createWorkUnit(
            self.getInputData()
        )
    
    def autoCompleteProductInput(self):
        values = self.sapCtrl.getValuesFromLayer('createWorkUnit', 'product')
        self.productIdLe.setText(values)
    
    def autoCompleteSubfaseInput(self):
        values = self.sapCtrl.getValuesFromLayer('createWorkUnit', 'subfase')
        self.subfaseLe.setText(values)

    @QtCore.pyqtSlot(bool)
    def on_extractProductBtn_clicked(self):
        self.autoCompleteProductInput()
    
    @QtCore.pyqtSlot(bool)
    def on_extractSubfaseBtn_clicked(self):
        self.autoCompleteSubfaseInput()

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        if not self.validInput():
            self.showMessageErro('Aviso', "<p>Preencha todos os campos!</p>")
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.runFunction()
        QtWidgets.QApplication.restoreOverrideCursor()
