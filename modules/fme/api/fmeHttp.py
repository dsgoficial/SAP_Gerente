import json, requests, socket

from SAP_Gerente.modules.fme.interfaces.IFmeApi import IFmeApi

class FmeHttp(IFmeApi):
    def __init__(self):
        super(FmeHttp, self).__init__()
        self.server = ''

    def checkError(self, response):
        if not response.ok:
            raise Exception(response.json()['message'])

    def httpGet(self, url):
        headers = {}
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, headers=headers, timeout=60)
        self.checkError(response)
        return response

    def setServer(self, server):
        self.server = "{0}/api".format(server)

    def getServer(self):
        return self.server

    def getRoutines(self):
        print()
        response = self.httpGet(
            url="{0}/rotinas".format(self.getServer())
        )
        if response:
            return response.json()['dados']
        return []