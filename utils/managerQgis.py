# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui 
from qgis import gui, core
import base64, os

class ManagerQgis(QtCore.QObject):

    path_icon_on_off = os.path.join(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            ".."
        )),
        'icons',
        'on_off.png'
    )

    path_icon_vertex = os.path.join(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            ".."
        )),
        'icons',
        'vertex.png'
    )

    def __init__(self, iface=None):
        super(ManagerQgis, self).__init__()
        self.iface = iface

    def get_loaded_layers(self):
        return core.QgsProject.instance().mapLayers().values()

    def count_modified_layer(self):
        count = 0
        for lyr in self.get_loaded_layers():
            check = (
                lyr.type() == core.QgsMapLayer.VectorLayer
                and
                lyr.isModified()
            )
            if check:
                count+=1
        return count

    def save_project_var(self, key, value):
        chiper_text = base64.b64encode(value.encode('utf-8'))
        core.QgsExpressionContextUtils.setProjectVariable(
            core.QgsProject().instance(), 
            key,
            chiper_text.decode('utf-8')
        )

    def load_project_var(self, key):
        current_project  = core.QgsProject().instance()
        chiper_text = core.QgsExpressionContextUtils.projectScope(current_project).variable(
            key
        )
        value = base64.b64decode(str.encode(chiper_text)).decode('utf-8') if chiper_text else ''
        return value

    def save_qsettings_var(self, key, value):
        qsettings = QtCore.QSettings()
        qsettings.setValue(key, value)

    def load_qsettings_var(self, key):
        qsettings = QtCore.QSettings()
        return qsettings.value(key)

    def load_custom_config(self):
        self.clean_custom_config()
        configs = self.get_custom_config()
        qsettings = QtCore.QSettings()
        for var_qgis in configs:
            qsettings.setValue(var_qgis, configs[var_qgis])
        self.create_shortcut_actions()
        
    def clean_custom_config(self):
        qsettings = QtCore.QSettings()
        for var_qgis in qsettings.allKeys():
            if (u'shortcuts' in var_qgis):
                qsettings.setValue(var_qgis, u'')

    def get_custom_config(self):
        variables = {
            u'qgis/parallel_rendering' : u'true',
            u'qgis/max_threads' : 8,
            u'qgis/simplifyDrawingHints': u'0',            
            u'qgis/digitizing/marker_only_for_selected' : u'false',
            'qgis/digitizing/default_snapping_tolerance' : '10',
            'qgis/digitizing/default_snap_enabled' : 'true', 
            u'qgis/digitizing/default_snap_type' : u'Vertex',
            'Map/scales' : '1:250000,1:100000,1:50000,1:25000,1:10000,1:5000,1:2000,1:1000,1:500,1:250',
            'qgis/digitizing/line_width' : '3',
            'qgis/digitizing/line_color_alpha' : '63',
            'qgis/digitizing/fill_color_alpha' : '40',
            u'qgis/default_selection_color_alpha': u'63',
            u'shortcuts/Sair do QGIS' : u'',
            u'shortcuts/Exit QGIS' : u'',
            u'shortcuts/Mesclar fei\xe7\xf5es selecionadas' : u'M',
            u'shortcuts/Merge Selected Features' : u'M',
            u'shortcuts/Quebrar Fei\xe7\xf5es' : u'C',
            u'shortcuts/Split Features' : u'C',
            u'shortcuts/Identificar fei\xe7\xf5es': u'I',
            u'shortcuts/Identify Features': u'I',
            u'shortcuts/Adicionar fei\xe7\xe3o': u'A',
            u'shortcuts/Add Feature': u'A',
            u'shortcuts/Desfazer sele\xe7\xe3o de fei\xe7\xf5es em todas as camadas': u'D',
            u'shortcuts/Deselect Features from All Layers': u'D',
            u'shortcuts/Ferramenta Vértice (Todas as Camadas)' : u'N',
            u'shortcuts/Vertex Tool (All Layers)' : u'N',
            u'shortcuts/Salvar para todas as camadas' : u'Ctrl+S',
            u'shortcuts/Save for All Layers' : u'Ctrl+S',
            u'shortcuts/Habilitar tra\xe7ar' : u'T',
            u'shortcuts/Enable Tracing' : u'T',
            u'shortcuts/Remodelar fei\xe7\xf5es' : u'R',
            u'shortcuts/Reshape Features' : u'R',
            u'shortcuts/\xc1rea' : u'Z',
            u'shortcuts/Measure Area' : u'Z',
            u'shortcuts/Linha' : u'X',
            u'shortcuts/Measure Line' : u'X',
            u'shortcuts/DSGTools: Generic Selector': u'S',
            u'shortcuts/DSGTools: Seletor Gen\xe9rico': u'S',
            u'shortcuts/DSGTools: Right Degree Angle Digitizing': u'E',
            u'shortcuts/DSGTools: Ferramenta de aquisi\xe7\xe3o com \xe2ngulos retos': u'E',
            'shortcuts/Topological Editing' : 'H',
            u'shortcuts/Salvar' : u'',
            u'shortcuts/Save' : u'',
            u'shortcuts/Select Feature(s)' : u'V',
            u'shortcuts/Fei\xe7\xe3o(s)' : u'V',
            u'shortcuts/DSGTools: Inspecionar anterior': u'Q',
            u'shortcuts/DSGTools: Back Inspect': u'Q',
            u'shortcuts/DSGTools: Inspecionar pr\xf3ximo': u'W',
            u'shortcuts/DSGTools: Next Inspect': u'W',
            u'shortcuts/DSGTools: Desenhar Forma': u'G',
            u'shortcuts/DSGTools: Draw Shape': u'G',
            u'shortcuts/Desfazer' : u'',
            u'shortcuts/Undo' : u'',
            u'shortcuts/Undo' : u'',
            u'shortcuts/Mostrar camadas selecionadas' : u'',
            u'shortcuts/Show Selected Layers' : u'',
            u'shortcuts/Esconder camadas selecionadas' : u'',
            u'shortcuts/Hide Selected Layers' : u'',
            u'shortcuts/Toggle Snapping' : u'',
            'shortcuts/DSGTools: Toggle all labels visibility' : 'L',
            u'shortcuts/DSGTools: Ferramenta de Aquisição à Mão Livre' : 'F',
            'shortcuts/DSGTools: Free Hand Acquisition' : 'F',
            'shortcuts/DSGTools: Free Hand Reshape' : 'Shift+R'

        }
        return variables

    def create_shortcut_actions(self):
        self.action_on_off_lyr = QtWidgets.QAction(
            QtGui.QIcon(self.path_icon_on_off),
            u"Ligar/Desligar camada.",
            self.iface.mainWindow()
        )
        self.action_on_off_lyr.setShortcut(QtCore.Qt.Key_Y)
        self.action_on_off_lyr.setCheckable(True)
        self.action_on_off_lyr.toggled.connect(self.on_off_layers)
        self.iface.digitizeToolBar().addAction(
            self.action_on_off_lyr
        )

        self.action_show_hide_vtx = QtWidgets.QAction(
            QtGui.QIcon(self.path_icon_vertex),
            u"Mostrar/Esconder marcadores para feições selecionadas.",
            self.iface.mainWindow()
        )
        self.action_show_hide_vtx.setShortcut(QtCore.Qt.Key_B)
        self.action_show_hide_vtx.setCheckable(True)
        self.action_show_hide_vtx.toggled.connect(self.show_markers_only_selected_feat)
        self.iface.digitizeToolBar().addAction(
            self.action_show_hide_vtx
        )

    def delete_shortcut_actions(self):
        self.iface.digitizeToolBar().removeAction(
            self.action_show_hide_vtx
        )
        self.iface.digitizeToolBar().removeAction(
            self.action_on_off_lyr
        )
        

    def on_off_layers(self, b):
        if b:
            self.iface.actionHideSelectedLayers().trigger()
        else:
            self.iface.actionShowSelectedLayers().trigger()

    def show_markers_only_selected_feat(self, b):
        qsettings = QtCore.QSettings()
        if b:
            qsettings.setValue(u'qgis/digitizing/marker_only_for_selected', u'true')
        else:
            qsettings.setValue(u'qgis/digitizing/marker_only_for_selected', u'false')
        self.iface.mapCanvas().refresh()
