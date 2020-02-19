from abc import ABC, abstractmethod

class ISapCtrl(ABC):

    def __init__(self, gisPlatform):
        self.gisPlatform = gisPlatform

    @abstractmethod
    def authUser(self, user, password, server):
        pass

    @abstractmethod
    def loadLoginView(self):
        pass

    @abstractmethod
    def showLoginView(self):
        pass
        
    @abstractmethod
    def saveLoginData(self, user, server):
        pass