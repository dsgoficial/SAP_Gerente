from abc import ABC, abstractmethod

class IApiSap(ABC):

    @abstractmethod
    def loginServer(self, user, password, server):
        pass