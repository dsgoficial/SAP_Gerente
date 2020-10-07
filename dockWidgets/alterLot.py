import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class  AlterLot(DockWidgetAutoComplete):

    def __init__(self, controller):
        super(AlterLot, self).__init__(controller)
        self.lots = self.controller.getSapLots()
        self.loadLots(self.lots)

    def loadLots(self, lots):
        self.lotsCb.addItem('...')
        for lot in lots:
            self.lotsCb.addItem(lot['nome'], lot['id'])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "alterLot.ui"
        )

    def clearInput(self):
        self.workspacesIdsLe.setText('')
        self.lotsCb.setCurrentIndex(0)

    def validLot(self):
        return self.lotsCb.currentIndex() != 0

    def validInput(self):
        return  self.workspacesIdsLe.text() and self.validLot()

    def getLotId(self):
        return self.lotsCb.itemData(self.lotsCb.currentIndex())

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdsLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.alterSapLot(
            self.getWorkspacesIds(),
            self.getLotId()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('alterLot', 'workUnit')
        self.workspacesIdsLe.setText(values)