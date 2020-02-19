from PyQt5 import QtCore, QtWidgets, QtGui 
from qgis import gui, core
import base64, os
from Ferramentas_Gerencia.qgis.interfaces.IStorages import IStorages

class Storages(IStorages):

    def __init__(self):
        super(Storages, self).__init__()


    def setProjectVariable(self, key, value):
        chiper_text = base64.b64encode(value.encode('utf-8'))
        core.QgsExpressionContextUtils.setProjectVariable(
            core.QgsProject().instance(), 
            key,
            chiper_text.decode('utf-8')
        )

    def getProjectVariable(self, key):
        current_project  = core.QgsProject().instance()
        chiper_text = core.QgsExpressionContextUtils.projectScope(current_project).variable(
            key
        )
        value = base64.b64decode(str.encode(chiper_text)).decode('utf-8') if chiper_text else ''
        return value

    def setSettingsVariable(self, key, value):
        qsettings = QtCore.QSettings()
        qsettings.setValue(key, value)

    def getSettingsVariable(self, key):
        qsettings = QtCore.QSettings()
        return qsettings.value(key)