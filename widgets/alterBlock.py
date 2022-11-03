import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class  AlterBlock(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(AlterBlock, self).__init__(controller=sapCtrl)
        self.blocks = self.controller.getSapBlocks()
        self.loadBlocks(self.blocks)

    def loadBlocks(self, blocks):
        self.blocksCb.addItem('...')
        for block in blocks:
            self.blocksCb.addItem(block['nome'], block['id'])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "alterBlock.ui"
        )

    def clearInput(self):
        self.workspacesIdsLe.setText('')
        self.blocksCb.setCurrentIndex(0)

    def validLot(self):
        return self.blocksCb.currentIndex() != 0

    def validInput(self):
        return  self.workspacesIdsLe.text() and self.validLot()

    def getLotId(self):
        return self.blocksCb.itemData(self.blocksCb.currentIndex())

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspacesIdsLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.alterSapBlock(
            self.getWorkspacesIds(),
            self.getLotId()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('alterBlock', 'workUnit')
        self.workspacesIdsLe.setText(values)