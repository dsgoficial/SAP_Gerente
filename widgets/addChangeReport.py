import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2
import datetime

class AddChangeReport(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, sap, parent=None):
        super(AddChangeReport, self).__init__(parent=parent)
        self.sap = sap

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addChangeReport.ui'
        )

    def validInput(self):
        return self.descriptionTe.toPlainText()

    def getData(self):
        data = {
            'data' : self.dateDt.dateTime().toUTC().toString(QtCore.Qt.ISODate),
            'descricao' : self.descriptionTe.toPlainText()
        }
        if self.isEditMode():
            data['id'] = int(self.getCurrentId())
        return data

    def setData(self, data):
        epoch = datetime.datetime(1970, 1, 1)
        mydt = datetime.datetime.strptime(data['data'], "%Y-%m-%dT%H:%M:%S.%fZ")
        val = (mydt - epoch).total_seconds()
        self.setCurrentId(data['id'])
        self.dateDt.setDateTime(QtCore.QDateTime.fromSecsSinceEpoch(val))
        self.descriptionTe.setText(data['descricao'])

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        try:
            if not self.validInput():
                self.showError('Aviso', 'Preencha todos os campos!')
                return
            data = self.getData()
            if self.isEditMode():
                message = self.sap.updateChangeReport([data])
            else:
                message = self.sap.createChangeReport([data])
            message and self.showInfo('Aviso', message)
            self.accept()
        except Exception as e:
            self.showError('Aviso', str(e))
