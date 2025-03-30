import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidgetAutoComplete import DockWidgetAutoComplete

class DeleteProducts(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(DeleteProducts, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Deletar Produtos')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "deleteProducts.ui"
        )

    def clearInput(self):
        self.productsIdLe.setText('')

    def validInput(self):
        return self.productsIdLe.text()

    def getProductsIds(self):
        return [ int(d) for d in self.productsIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.deleteSapProducts(
            self.getProductsIds()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('deleteProducts', 'product')
        self.productsIdLe.setText(values)