
import os
from PyQt5 import QtWidgets, uic
from Ferramentas_Gerencia.modules.utils.interfaces.IMessage  import IMessage

class HtmlMessageDialog(QtWidgets.QDialog, IMessage):

    def __init__(self):
        super(HtmlMessageDialog, self).__init__()
        uic.loadUi(self.getUIPath(), self)
        
    def getUIPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'htmlMessageDialog.ui'
        )

    def show(self, parent, title, html):
        self.setWindowTitle(title)
        self.textEdit.setHtml(html)
        self.exec_()