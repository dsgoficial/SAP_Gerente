import os, sys, json
from qgis.PyQt import QtCore, uic, QtWidgets
from SAP_Gerente.widgets.inputDialogV2  import InputDialogV2

class AddHiddenColumnsForm(InputDialogV2):

    def __init__(self, sap, parent=None):
        super(AddHiddenColumnsForm, self).__init__(parent=parent)
        self.sap = sap
        self.currentId = None
        self.currentMenu = None

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addHiddenColumnsForm.ui'
        )

    def getFileData(self):
        filePath = self.pathFileLe.text()
        if not filePath:
            return self.currentMenu
        data = ''
        with open(filePath, 'r', encoding='utf-8-sig') as f:
            data = f.read()
        return data

    def getValidationError(self):
        """Retorna o motivo da recusa ou None. Formato: {"tabela": ["coluna", ...]}."""
        if not self.nameLe.text().strip():
            return 'Preencha o nome!'
        try:
            content = self.getFileData()
        except (OSError, UnicodeDecodeError) as e:
            return 'Não foi possível ler o arquivo: {}'.format(e)
        if not content:
            return 'Selecione um arquivo JSON de colunas ocultas!'
        try:
            definition = json.loads(content)
        except ValueError as e:
            return 'O arquivo não é um JSON válido: {}'.format(e)
        if not isinstance(definition, dict) or not definition:
            return 'O JSON deve ser um objeto no formato {"tabela": ["coluna", ...]}!'
        for table, columns in definition.items():
            if (
                not str(table).strip()
                or not isinstance(columns, list)
                or not all(isinstance(c, str) and c.strip() for c in columns)
            ):
                return 'A chave "{}" deve associar o nome de uma tabela a uma lista de nomes de colunas!'.format(table)
        return None

    def validInput(self):
        return self.getValidationError() is None

    def getData(self):
        data = {
            'nome' : self.nameLe.text(),
            'definicao_colunas' : self.getFileData()
        }
        if self.currentId:
            data['id'] = self.currentId
        return data

    def setData(self, currentId, name, menu):
        self.currentId = currentId
        self.currentMenu = menu
        self.nameLe.setText(name)

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        error = self.getValidationError()
        if error:
            self.showError('Aviso', error)
            return
        try:
            data = [self.getData()]
            if self.isEditMode():
                message = self.sap.updateHiddenColumns(
                    data
                )
            else:
                message = self.sap.createHiddenColumns(
                    data
                )
            self.accept()
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Erro', str(e))
        

    @QtCore.pyqtSlot(bool)
    def on_fileBtn_clicked(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   '',
                                                   "Desktop",
                                                  '*.json')
        self.pathFileLe.setText(filePath[0])

    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.close()
