


class IDockWidget:
    
    def runFunction(self):
        raise NotImplementedError('Abstract Method')

    def autoCompleteInput(self):
        raise NotImplementedError('Abstract Method')

    def validInput(self):
        raise NotImplementedError('Abstract Method')

    def showMessageErro(self):
        raise NotImplementedError('Abstract Method')