import os, sys
from PyQt5 import QtCore, uic, QtWidgets
from Ferramentas_Gerencia.widgets.inputDialogV2  import InputDialogV2

class AddStyleForm(InputDialogV2):

    save = QtCore.pyqtSignal()

    def __init__(self, controller, sap, qgis, parent=None):
        super(AddStyleForm, self).__init__(parent=parent)
        self.controller = controller
        self.sap = sap
        self.qgis = qgis
        self.stylesData = None
        self.layerCb.setAllowEmptyLayer(True)
        self.layerCb.setLayer(None)
        self.setLayerWidgetVisible(False)

    def setLayerWidgetVisible(self, visible):
        self.layerCb.setVisible(visible)
        self.layerLb.setVisible(visible)
        
    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'addStyleForm.ui'
        )
        
    def clearInput(self):
        self.setLayerWidgetVisible(False)

    def validInput(self):
        return self.styleNameLe.text()

    def getData(self):
        data = {
            'grupo_estilo_id': self.groupCb.itemData(self.groupCb.currentIndex()),
        }
        layer = self.layerCb.currentLayer()
        if layer:
            self.setStylesData(
                self.qgis.getQmlStyleFromLayers([layer])
            )
        if self.isEditMode():
            data['id'] = self.getCurrentId()
        return data

    def loadGroupStyles(self, styles):
        self.groupCb.clear()
        self.groupCb.addItem('...', None)
        for style in styles:
            self.groupCb.addItem(style['nome'], style['id'])

    def setData(self, data):
        self.groupCb.setCurrentIndex(self.groupCb.findData(data['grupo_estilo_id']))
        self.setStylesData([data])

    def setStylesData(self, stylesData):
        self.stylesData = stylesData

    def getStylesData(self):
        return self.stylesData

    @QtCore.pyqtSlot(bool)
    def on_okBtn_clicked(self):
        stylesData = self.getStylesData()
        for style in stylesData:
            style['grupo_estilo_id'] = self.getData()['grupo_estilo_id']
        try:
            if self.isEditMode():
                self.sap.updateStyles(stylesData)
            else:
                self.sap.createStyles(stylesData)
            self.save.emit()
            self.accept()
            self.showInfo('Aviso', 'Estilos Salvos!')
        except Exception as e:
            self.showError('Aviso', str(e))