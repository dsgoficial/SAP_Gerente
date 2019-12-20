
class ILogin(object):

    def __init__(self, loginCtrl):
        self.loginCtrl = loginCtrl

    def loadData(self, user, server):
        raise NotImplementedError('Abstract Method')

    def showView(self):
        raise NotImplementedError('Abstract Method')

    def closeView(self):
        raise NotImplementedError('Abstract Method')

    def showErroMessage(self, title, text):
        raise NotImplementedError('Abstract Method')

    def login(self):
        raise NotImplementedError('Abstract Method')
    
    

    