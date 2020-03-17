import json, requests, socket

from Ferramentas_Gerencia.fme.interfaces.IFmeApi import IFmeApi

class FmeHttp(IFmeApi):
    def __init__(self):
        super(FmeHttp, self).__init__()
        self.server = ''

    def checkConnection(self, server):
        session = requests.Session()
        session.trust_env = False
        session.get(server, timeout=8)

    def checkError(self, response):
        if not response.ok:
            raise Exception(response.json()['message'])

    def httpGet(self, url): 
        self.checkConnection(
            self.getServer()
        )
        headers = {}
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, headers=headers)
        self.checkError(response)
        return response

    def setServer(self, server, port=''):
        port = ':{0}'.format(port) if port else ''
        self.server = "{0}{1}/api".format(server, port)

    def getServer(self):
        return self.server

    def getRoutines(self):
        response = self.httpGet(
            url="{0}/rotinas".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []