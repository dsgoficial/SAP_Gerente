import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
 
class  DeleteProductsWithoutUT(DockWidget):

    def __init__(self, sapCtrl):
        super(DeleteProductsWithoutUT, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Deletar Produtos sem Unidade de Trabalho')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteProductsWithoutUT.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  True

    def runFunction(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            success, message = self.controller.deleteSAPProductsWithoutUT()
            if success:
                self.showInfo('Sucesso', message or 'Produtos sem unidade de trabalho removidos com sucesso!')
            else:
                self.showError('Erro', message or 'Ocorreu um erro ao remover produtos sem unidade de trabalho.')
        except Exception as e:
            self.showError('Erro', f'Ocorreu um erro inesperado: {str(e)}')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        