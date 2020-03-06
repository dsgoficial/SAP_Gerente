import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class  AlterLot(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(AlterLot, self).__init__(sapCtrl=sapCtrl)
        self.lots = self.sapCtrl.getSapLots()
        self.loadLots(self.lots)

    def loadLots(self, lots):
        self.lotsCb.addItem('...')
        for lot in lots:
            self.lotsCb.addItem(lot['nome'], lot['id'])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "alterLot.ui"
        )

    def clearInput(self):
        pass

    def validLot(self):
        return self.lotsCb.currentIndex() != 0

    def validInput(self):
        return  self.workspacesIdsLe.text() and self.validLot()

    def getLotId(self):
        return self.lotsCb.itemData(self.lotsCb.currentIndex())

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdsLe.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.alterLot(
            self.getWorkspacesIds(),
            self.getLotId()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('alterLot', 'workUnit')
        self.workspacesIdsLe.setText(values)