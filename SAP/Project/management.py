# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.utils import msgBox

from qgis.utils import plugins

from Ferramentas_Gerencia.SAP.Project.Views.openActivity import OpenActivity
from Ferramentas_Gerencia.SAP.Project.Views.openNextActivityByUser import OpenNextActivityByUser
from Ferramentas_Gerencia.SAP.Project.Views.lockWorkspace import LockWorkspace
from Ferramentas_Gerencia.SAP.Project.Views.unlockWorkspace import UnlockWorkspace
from Ferramentas_Gerencia.SAP.Project.Views.pauseActivity import PauseActivity
from Ferramentas_Gerencia.SAP.Project.Views.restartActivity import RestartActivity
from Ferramentas_Gerencia.SAP.Project.Views.setPriorityActivity import SetPriorityActivity
from Ferramentas_Gerencia.SAP.Project.Views.createPriorityGroupActivity import CreatePriorityGroupActivity
from Ferramentas_Gerencia.SAP.Project.Views.returnActivityToPreviousStep import ReturnActivityToPreviousStep
from Ferramentas_Gerencia.SAP.Project.Views.advanceActivityToNextStep import AdvanceActivityToNextStep
from Ferramentas_Gerencia.SAP.Project.Views.fillComments import FillComments
from Ferramentas_Gerencia.SAP.Project.Views.addNewRevision import AddNewRevision
from Ferramentas_Gerencia.SAP.Project.Views.addNewRevisionCorrection import AddNewRevisionCorrection

from Ferramentas_Gerencia.utils.network import Network
from Ferramentas_Gerencia.utils.managerQgis import ManagerQgis



class Management(QtCore.QObject):

    icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        '..',
        'icons',
        'config.png'
    )

    def __init__(self, iface):
        super(Management, self).__init__()
        self.iface = iface
        self.network = None
        self.treeWidget = None

    def get_tree_widget(self):
        self.treeWidget = QtWidgets.QTreeWidget()
        self.network = Network(self.treeWidget)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.header().hide()
        self.views = [
            {
                "name" : 'Abrir atividade',
                "widget" : OpenActivity(self.iface)
            },
            {
                "name" : 'Abrir próxima atividade do usuário',
                "widget" : OpenNextActivityByUser(self.iface, self.get_users_names())
            },
            {
                "name" : 'Bloquear unidades de trabalho',
                "widget" : LockWorkspace(self.iface)
            },
            {
                "name" : 'Desbloquear unidades de trabalho',
                "widget" : UnlockWorkspace(self.iface)
            },
            {
                "name" : 'Pausar atividade',
                "widget" : PauseActivity(self.iface)
            },
            {
                "name" : 'Reiniciar atividade',
                "widget" : RestartActivity(self.iface)
            },
            {
                "name" : 'Definir atividade prioritária',
                "widget" : SetPriorityActivity(self.iface, self.get_users_names())
            },
            {
                "name" : 'Definir atividade prioritária de grupo',
                "widget" : CreatePriorityGroupActivity(self.iface, self.get_profiles_names())
            },
            {
                "name" : 'Retornar atividade para etapa anterior',
                "widget" : ReturnActivityToPreviousStep(self.iface)
            },
            {
                "name" : 'Avançar atividade para próxima etapa',
                "widget" : AdvanceActivityToNextStep(self.iface)
            },
            {
                "name" : 'Preencher observações',
                "widget" : FillComments(self.iface)
            },
            {
                "name" : 'Adicionar nova revisão',
                "widget" : AddNewRevision(self.iface)
            },
            {
                "name" : 'Adicionar nova revisão/correção',
                "widget" : AddNewRevisionCorrection(self.iface)
            }
            
        ]
        for view in self.views:
            self.load_view(view)
        return self.treeWidget

    def get_users_names(self):
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.GET(
            host=host,
            url="{0}/gerencia/usuario".format(host),
            header=header
        )
        if response:
            users = response.json()['dados']
            return users
        return [{'nome': 'Sem usuários', 'id': False}]

    def get_profiles_names(self):
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.GET(
            host=host,
            url="{0}/gerencia/perfil_producao".format(host),
            header=header
        )
        if response:
            profiles = response.json()['dados']
            return profiles
        return [{'nome': 'Sem perfis de produção', 'id': False}]

    def load_view(self, view):
        topLevelItem = QtWidgets.QTreeWidgetItem([view['name']])
        topLevelItem.setIcon(0, QtGui.QIcon(self.icon_path))
        childItem = QtWidgets.QTreeWidgetItem()
        topLevelItem.addChild(childItem)
        self.treeWidget.addTopLevelItem(topLevelItem)
        widget = view['widget']
        widget.run.connect( self.run_function )
        self.treeWidget.setItemWidget(childItem, 0, widget)
    
    def run_function(self):
        input_data = self.sender().get_input_data()
        getattr(self, input_data['function_name'])(input_data['param'])

    
    def open_activity(self, input_data):
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        user = m_qgis.load_project_var('user')
        password = m_qgis.load_project_var('password')
        response = self.network.GET(
            host=host,
            url="{0}/gerencia/atividade/{1}".format(host, input_data["atividade_id"]),
            header=header
        )
        if response:
            activity_data = response.json()
            activity_data['token'] = token
            activity_data['server'] = host
            activity_data['user'] = user
            activity_data['password'] = password
            prodTools = plugins['Ferramentas_Producao']
            prodTools.sap.load_sap_activity_from_data(activity_data)

    def open_next_activity(self, input_data):
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        user = m_qgis.load_project_var('user')
        password = m_qgis.load_project_var('password')
        response = self.network.GET(
            host=host,
            url="{0}/gerencia/atividade/{1}".format(host, input_data["user_id"]),
            header=header
        )
        if response:
            activity_data = response.json()
            activity_data['token'] = token
            activity_data['server'] = host
            activity_data['user'] = user
            activity_data['password'] = password
            prodTools = plugins['Ferramentas_Producao']
            prodTools.sap.load_sap_activity_from_data(activity_data)

    def lock_workspace(self, input_data):
        post_data = input_data
        post_data['disponivel'] = False
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/unidade_trabalho/disponivel".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def unlock_workspace(self, input_data):
        post_data = input_data
        post_data['disponivel'] = True
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/unidade_trabalho/disponivel".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def pause_activity(self, input_data):
        post_data = input_data
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/atividade/pausar".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def restart_activity(self, input_data):
        post_data = input_data
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/atividade/reiniciar".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def set_priority_activity(self, input_data):
        post_data = input_data
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/fila_prioritaria".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def create_priority_group_activity(self, input_data):
        post_data = input_data
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/fila_prioritaria_grupo".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def return_activity_to_previous_step(self, input_data):
        post_data = input_data
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/atividade/voltar".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def advance_activity_to_previous_step(self, input_data):
        post_data = input_data
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/atividade/avancar".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def fill_comment_activity(self, input_data):
        post_data = input_data
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/observacao".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def add_new_revision(self, input_data):
        post_data = input_data
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/atividade/criar_revisao".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)

    def add_new_revision_correction(self, input_data):
        post_data = input_data
        m_qgis = ManagerQgis(self.iface)
        host = m_qgis.load_qsettings_var('login/server')
        token = m_qgis.load_qsettings_var('token')
        header = {'authorization' : token}
        response = self.network.POST(
            host=host,
            url="{0}/gerencia/atividade/criar_revcorr".format(host),
            post_data=post_data,
            header=header
        )
        if response:
            html = "<p>{0}</p>".format(response.json()['message'])
            msgBox.show(text=html, title=u"Aviso", parent=self.treeWidget)
            