# -*- coding: utf-8 -*-
from PyQt5 import QtCore
import sys, os, pickle
from Ferramentas_Gerencia.SAP.Login.login import Login
from Ferramentas_Gerencia.utils import network
from qgis.utils import plugins
from configparser import ConfigParser

class Management(QtCore.QObject):

    show_tools = QtCore.pyqtSignal(bool)
    close_tools = QtCore.pyqtSignal()
    close_work = QtCore.pyqtSignal()

    def __init__(self, iface):
        super(Management, self).__init__()
        self.iface = iface
        self.login_sap = Login(self.iface)
        self.login_sap.sap.connect(
            self.login
        )
        self.net = network

    def add_action_qgis(self, b):
        if b:
            self.login_sap.action.add_on_qgis()
        else:
            self.login_sap.action.remove_from_qgis()

    def enable_action_qgis(self, b):
        self.login_sap.action.setEnabled(b)
    
    def update_sap_data(self, data, server, user, password, token):
        data['token'] = token
        data['server'] = server
        data['user'] = user
        data['password'] = password

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
        
    def login(self, server, user, password, id_activity):
        sucess = False
        post_data = {
            "usuario" : user,
            "senha" : password,
            'plugins' : self.get_plugins_versions()
        }
        url = u"{0}/login".format(server)
        response = self.net.POST(server, url, post_data)
        if response and response.json()['sucess']:
            if not( 'version' in response.json()['dados'] and int(response.json()['dados']['version']) == 2):
                self.show_message('erro version')
                return
            token = response.json()['dados']['token']
            
            data = self.get_current_works(server, user, password, token, id_activity)
            if data and "dados" in data:
                self.update_sap_data(
                    data, 
                    server, 
                    user, 
                    password, 
                    token
                )
                print(data)
                self.login_sap.dialog.accept()
                self.load_activity(data)

    def get_current_works(self, server, user, password, token, id_activity):
        header = {'authorization' : token}
        url = u"{0}/distribuicao/atividade/{1}".format(server, id_activity)
        response = self.net.GET(server, url, header)
        if response:
            data = response.json()
            return data
        return {}

    def load_activity(self, data):
        prodTools = plugins['Ferramentas_Producao']
        prodTools.sap.load_sap_activity_from_data(data)
    