import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
from qgis import core
from functools import cmp_to_key

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
        self.setWindowTitle('Carregar Metadado dos Insumos')

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
                    'fields': [''] + fields,
                    'default': 'nome'
                },
                {
                    'combo': self.pathFieldCb,
                    'fields': [''] + fields,
                    'default': 'caminho'
                },
                {
                    'combo': self.epsgFieldCb,
                    'fields': [''] + fields,
                    'default': 'epsg'
                }
            ]:
            combo = setting['combo']
            combo.clear()
            fieldSorted = sorted(setting['fields'], key=cmp_to_key(lambda a, b: 1 if b == setting['default'] else -1))
            if fieldSorted[0] != setting['default']:
                fieldSorted = sorted(setting['fields'], key=cmp_to_key(lambda a, b: 1 if b == '' else -1))
            combo.addItems(fieldSorted)

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

                if data[field] == '' and field in ['nome', 'caminho']:
                    self.showError('Aviso', 'Os campos "Nome" e "Caminho" da camada deve ser preenchido!')
                    return
            data['geom'] = self.qgis.geometryToEwkt( feat['geometry'], layer.crs().authid(), 'EPSG:4326' )
            inputs.append(data)
        try:
            message = self.sap.createInputs(
                self.getInputTypeCode(), 
                self.getInputGroupId(),
                inputs
            )
            message and self.showInfo('Aviso', message)
        except Exception as e:
            self.showError('Aviso', str(e))

    @QtCore.pyqtSlot(bool)
    def on_templateLayerBtn_clicked(self):
        self.qgis.generateMetadataLayer()