import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
 
class  CopySetupToLocalMode(DockWidget):

    def __init__(self, databases, sapCtrl):
        super(CopySetupToLocalMode, self).__init__(controller=sapCtrl)
        self.setWindowTitle('Copiar Configurações para Modo Local')
        self.databases = databases
        self.loadDatabases(self.databases)
        
    def loadDatabases(self, databases):
        self.databases = databases
        self.databasesCb.clear()
        self.databasesCb.addItems(['...'] + [ d['nome'] for d in self.databases])

    def getDatabases(self):
        return self.databases

    def getDatabaseData(self, dbName):
        for dbData in self.getDatabases():
            if not ( dbData['nome'] == dbName ):
                continue
            return dbData

    def getCurrentDatabase(self):
        return self.databasesCb.currentText()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "copySetupToLocalMode.ui"
        )

    def copyStyles(self):
        return self.stylesCkb.isChecked()

    def copyModels(self):
        return self.modelsCkb.isChecked()

    def copyRules(self):
        return self.rulesCkb.isChecked()

    def copyMenus(self):
        return self.menusCkb.isChecked() 

    def clearInput(self):
        self.stylesCkb.setChecked(False)
        self.modelsCkb.setChecked(False)
        self.rulesCkb.setChecked(False)
        self.menusCkb.setChecked(False)
        self.databasesCb.setCurrentIndex(0)

    def validDatabase(self):
        return self.databasesCb.currentIndex() != 0

    def validOptions(self):
        return (
            self.copyStyles() or
            self.copyModels() or
            self.copyRules() or
            self.copyMenus()
        )

    def validInput(self):
        return  self.validDatabase() and self.validOptions()

    def runFunction(self):
        dbData = self.getDatabaseData(
            self.getCurrentDatabase()
        )
        if dbData is None:
            return
        self.controller.copySapSettingsToLocalMode(
            dbData['servidor'],
            dbData['porta'],
            dbData['nome'],
            self.copyStyles(),
            self.copyModels(),
            self.copyRules(),
            self.copyMenus()
        )