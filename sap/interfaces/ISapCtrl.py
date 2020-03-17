from abc import ABC, abstractmethod

class ISapCtrl(ABC):

    def __init__(self, gisPlatform, fmeCtrl):
        self.gisPlatform = gisPlatform
        self.fmeCtrl = fmeCtrl

    @abstractmethod
    def authUser(self, user, password, server):
        pass

    @abstractmethod
    def showLoginView(self):
        pass