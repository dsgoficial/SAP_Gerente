

class IManagementDock:

    def addProjectManagementWidget(self, name, widget):
        raise NotImplementedError('Abstract Method')

    def addProjectCreationWidget(self, name, widget):
        raise NotImplementedError('Abstract Method')

    def addDangerZoneWidget(self, name, widget):
        raise NotImplementedError('Abstract Method')

    def showMessageErro(self, title, text):
        raise NotImplementedError('Abstract Method')

    def showMessageInfo(self, title, text):
        raise NotImplementedError('Abstract Method')