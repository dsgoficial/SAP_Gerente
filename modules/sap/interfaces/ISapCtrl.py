from abc import ABC, abstractmethod

class ISapCtrl(ABC):

    @abstractmethod
    def authUser(self, user, password, server):
        pass

    @abstractmethod
    def login(self):
        pass