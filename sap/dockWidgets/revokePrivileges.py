import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidget  import DockWidget
 
class  RevokePrivileges(DockWidget):

    def __init__(self, databases, sapCtrl):
        super(RevokePrivileges, self).__init__(sapCtrl=sapCtrl)
        self.databases = databases
        self.loadDatabases(self.databases)
        
    def loadDatabases(self, databases):
        self.databases = databases
        self.databasesCb.clear()
        self.databasesCb.addItems(['...'] + [ d['nome'] for d in self.databases])

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "revokePrivileges.ui"
        )

    def getDatabases(self):
        return self.databases

    def getDatabaseData(self, dbName):
        for dbData in self.getDatabases():
            if not ( dbData['nome'] == dbName ):
                continue
            return dbData

    def getCurrentDatabase(self):
        return self.databasesCb.currentText()

    def clearInput(self):
        pass

    def validDatabase(self):
        return self.databasesCb.currentIndex() != 0

    def validInput(self):
        return  self.validDatabase()

    def runFunction(self):
        dbData = self.getDatabaseData(
            self.getCurrentDatabase()
        )
        if dbData is None:
            return
        self.sapCtrl.revokePrivileges(
            dbData['servidor'],
            dbData['porta'],
            dbData['nome']
        )