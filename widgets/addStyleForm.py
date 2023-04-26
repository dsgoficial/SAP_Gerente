import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2
import os

class AddStyleForm(InputDialogV2):

    def __init__(self, sap, parent=None):
        super(AddStyleForm, self).__init__(parent=parent)
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addStyleForm.ui'
        )

    def loadGroupStyles(self, styles):
        self.groupCb.clear()
        self.groupCb.addItem('...', None)
        for style in styles:
            self.groupCb.addItem(style['nome'], style['id'])

    def getFileData(self):
        filePath = self.pathFileLe.text()
        data = ''
        with open(filePath, 'r') as f:
            data = f.read()
        return data

    def clearInput(self):
        pass
    
    def validInput(self):
        return self.schemaLe.text() and self.pathFileLe.text() and self.getFileData() and self.groupCb.itemData(self.groupCb.currentIndex())

    def getData(self):
        return {
            'f_table_schema': self.schemaLe.text(),
            'f_table_name': os.path.basename(self.pathFileLe.text()).split('.')[0],
            'styleqml': self.getFileData(),
            'stylesld': '',
            'ui': '',
            'f_geometry_column': 'geom',
            'grupo_estilo_id': int(self.groupCb.itemData(self.groupCb.currentIndex()))
        }

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        data = [self.getData()]
        try:
            if self.isEditMode():
                self.sap.updateStyles(data)
            else:
                self.sap.createStyles(data)
            self.accept()
            self.showInfo('Aviso', 'Estilos Salvos!')
        except Exception as e:
            self.showError('Aviso', str(e))

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.qml')
        self.pathFileLe.setText(filePath[0])
