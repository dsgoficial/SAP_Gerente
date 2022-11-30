import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.widgets.dockWidget  import DockWidget
from qgis import core

class CreateInputs(DockWidget):

    def __init__(self, controller, qgis, sap):
        super(CreateInputs, self).__init__(controller=controller)
        self.sap = sap
        self.qgis = qgis
        self.comboBoxPolygonLayer = controller.getQgisComboBoxPolygonLayer()
        self.comboBoxPolygonLayer.currentIndexChanged.connect(self.updateAssociatedFields)
        self.mapLayerLayout.addWidget(self.comboBoxPolygonLayer)
        self.loadInputTypes(self.sap.getInputTypes())
        self.loadInputGroups(self.sap.getInputGroups())
        self.updateAssociatedFields(self.comboBoxPolygonLayer.currentIndex())
        self.setWindowTitle('Criar Insumo')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "createInputs.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return (
            self.comboBoxPolygonLayer.currentLayer()
            and
            self.getBlockId()
        )

    def updateAssociatedFields(self, currentIndex):
        if currentIndex < 0:
            return
        fields = self.comboBoxPolygonLayer.getCurrentLayerFields()
        for setting in [
                {
                    'combo': self.nameFieldCb,
                    'fields': fields
                },
                {
                    'combo': self.pathFieldCb,
                    'fields': fields
                },
                {
                    'combo': self.epsgFieldCb,
                    'fields': [''] + fields
                }
            ]:
            combo = setting['combo']
            combo.clear()
            combo.addItems(setting['fields'])

    def getAssociatedFields(self):
        return {
            'nome': self.nameFieldCb.currentText(),
            'caminho': self.pathFieldCb.currentText(),
            'epsg': self.epsgFieldCb.currentText()
        }

    def loadInputTypes(self, data):
        self.inputTypeCb.clear()
        self.inputTypeCb.addItem('...', None)
        for item in data:
            self.inputTypeCb.addItem(
                item['nome'], 
                item['code']
            )

    def loadInputGroups(self, data):
        self.inputGroupCb.clear()
        self.inputGroupCb.addItem('...', None)
        for item in data:
            self.inputGroupCb.addItem(
                item['nome'], 
                item['id']
            )

    def getInputTypeCode(self):
        return self.inputTypeCb.itemData(self.inputTypeCb.currentIndex())

    def getInputGroupId(self):
        return self.inputGroupCb.itemData(self.inputGroupCb.currentIndex())

    def runFunction(self):
        layer = self.comboBoxPolygonLayer.currentLayer()
        if len([ f for f in layer.getFeatures() if f.geometry().wkbType() != core.QgsWkbTypes.Polygon ]) != 0:
            self.showError('Aviso', 'A camada deve ser do tipo "Polygon"!')
            return
        
        associatedFields = self.getAssociatedFields()
        features = self.qgis.dumpFeatures(
            self.comboBoxPolygonLayer.currentLayer(), 
            self.onlySelectedCkb.isChecked()
        )
        inputs = []
        for feat in features:
            data = {}
            for field in associatedFields:
                if associatedFields[field] == '':
                    data[field] = ''
                    continue
                data[field] = str(feat[ associatedFields[field] ])
            data['geom'] = self.qgis.geometryToEwkt( feat['geometry'], layer.crs().authid(), 'EPSG:4326' )
            inputs.append(data)
        try:
            message = self.sap.createInputs(
                self.getInputTypeCode(), 
                self.getInputGroupId(),
                inputs
            )
            self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))