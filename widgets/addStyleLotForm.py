import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2
import os

class AddStyleLotForm(InputDialogV2):

    def __init__(self, sap, parent=None):
        super(AddStyleLotForm, self).__init__(parent=parent)
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addStyleLotForm.ui'
        )

    def loadGroupStyles(self, styles):
        self.groupCb.clear()
        self.groupCb.addItem('...', None)
        for style in styles:
            self.groupCb.addItem(style['nome'], style['id'])

    def getFileData(self, filePath):
        data = ''
        with open(filePath, 'r') as f:
            data = f.read()
        return data

    def clearInput(self):
        pass
    
    def validInput(self):
        return self.schemaLe.text() and self.pathFolderLe.text() and self.getFileData() and self.groupCb.itemData(self.groupCb.currentIndex())

    def getData(self):
        folderPath = self.pathFolderLe.text()
        return [
            {
                'f_table_schema': self.schemaLe.text(),
                'f_table_name': os.path.basename(filePath).split('.')[0],
                'styleqml': self.getFileData(filePath),
                'stylesld': '',
                'ui': '',
                'f_geometry_column': 'geom',
                'grupo_estilo_id': int(self.groupCb.itemData(self.groupCb.currentIndex()))
            }
            for filePath in [ os.path.join(folderPath, f) for f in os.listdir(folderPath) ]
        ]

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        data = self.getData()
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
        folderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Selection pasta com estilos', '.')
        self.pathFolderLe.setText(folderPath)
