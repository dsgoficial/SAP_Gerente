


class IDockWidget:
    
    def runFunction(self, *args):
        raise NotImplementedError('Abstract Method')

    def autoCompleteInput(self, *args):
        raise NotImplementedError('Abstract Method')

    def validInput(self, *args):
        raise NotImplementedError('Abstract Method')

    def showMessageErro(self, *args):
        raise NotImplementedError('Abstract Method')