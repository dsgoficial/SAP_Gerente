# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from Ferramentas_Gerencia.SAP.Login.Views.loginDialog import LoginDialog
from Ferramentas_Gerencia.utils.network import Network
from Ferramentas_Gerencia.utils import msgBox


import sys, os
from qgis.utils import plugins
from configparser import ConfigParser
from Ferramentas_Gerencia.utils.managerQgis import ManagerQgis

class Login(QtCore.QObject):

    open_sap_management = QtCore.pyqtSignal()

    def __init__(self, iface):
        super(Login, self).__init__()
        self.iface = iface
        self.dialog = LoginDialog(self.iface)
        self.dialog.login_remote.connect(
            self.login_remote
        )
        self.network = Network(self.dialog)

    def show_login_dialog(self):
        m_qgis = ManagerQgis(self.iface)
        server = m_qgis.load_qsettings_var('login/server')
        user = m_qgis.load_project_var('user')
        password = m_qgis.load_project_var('password')
        self.dialog.load_login_data(server, user, password)
        self.dialog.show_()
       
    def login_remote(self, login_data):
        server = login_data['server']
        user = login_data['user']
        password = login_data['password']
        m_qgis = ManagerQgis(self.iface)
        m_qgis.save_qsettings_var('login/server', server)
        m_qgis.save_project_var('user', user)
        m_qgis.save_project_var('password', password)
        self.login(server, user, password)

    def login(self, server, user, password):
        sucess = False
        post_data = {
            "usuario" : user,
            "senha" : password,
            'plugins' : self.get_plugins_versions()
        }
        url = u"{0}/login".format(server)
        response = self.network.POST(server, url, post_data)
        response_data = response.json()
        if not(response_data and 'sucess' in response_data and response_data['sucess']):
            return
        if not( 'version' in response_data['dados'] and int(response_data['dados']['version']) == 2):
            self.show_message('erro version')
            return
        if not( 'administrador' in response_data['dados'] and response_data['dados']['administrador']):
            html = "<p>Usuário sem permissão de administrador.</p>"
            msgBox.show(text=html, title=u"Aviso") 
            return
        m_qgis = ManagerQgis(self.iface)
        m_qgis.save_qsettings_var('token', response.json()['dados']['token'])
        self.dialog.accept()
        self.open_sap_management.emit()         

    def get_current_works(self, server, user, password, token):
        header = {'authorization' : token}
        url = u"{0}/distribuicao/verifica".format(server)
        response = self.network.GET(server, url, header)
        if response:
            data = response.json()
            return data
        return {}

    def get_plugins_versions(self):
        plugins_versions = []
        for name, plugin in plugins.items():
            try:
                metadata_path = os.path.join(
                    plugin.plugin_dir,
                    'metadata.txt'
                )
                with open(metadata_path) as mf:
                    cp = ConfigParser()
                    cp.readfp(mf)
                    plugins_versions.append(
                        {
                            'nome' : name,
                            'versao' : cp.get('general', 'version').split('-')[0]
                        }
                    )
            except:
                pass
        return plugins_versions

        
        