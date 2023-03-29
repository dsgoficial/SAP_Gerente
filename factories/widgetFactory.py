
from Ferramentas_Gerencia.factories.mDockBuilder import MDockBuilder
from Ferramentas_Gerencia.factories.dockDirector import DockDirector
from Ferramentas_Gerencia.widgets.associateUserToBlocks  import AssociateUserToBlocks
from Ferramentas_Gerencia.widgets.associateUserToProfiles  import AssociateUserToProfiles
from Ferramentas_Gerencia.widgets.addUserProfileProduction import AddUserProfileProduction
from Ferramentas_Gerencia.widgets.profileProductionSetting import ProfileProductionSetting
from Ferramentas_Gerencia.widgets.addProfileProductionSetting import AddProfileProductionSetting
from Ferramentas_Gerencia.widgets.createProfileProduction import CreateProfileProduction
from Ferramentas_Gerencia.widgets.productionProfileEditor import ProductionProfileEditor
from Ferramentas_Gerencia.widgets.addRuleFormV2  import AddRuleFormV2
from Ferramentas_Gerencia.widgets.importUsersAuthServiceDlg  import ImportUsersAuthServiceDlg
from Ferramentas_Gerencia.widgets.addMenuForm  import AddMenuForm
from Ferramentas_Gerencia.widgets.addMenuProfileForm  import AddMenuProfileForm

class WidgetFactory:

    def create(self, widgetName, *args):
        widgets = {
            'DockSap': lambda *args: self.createDockSap(*args),
            'AssociateUserToBlocks': lambda *args: AssociateUserToBlocks(*args),
            'AssociateUserToProfiles': lambda *args: AssociateUserToProfiles(*args),
            'AddUserProfileProduction': lambda *args: AddUserProfileProduction(*args),
            'ProfileProductionSetting': lambda *args: ProfileProductionSetting(*args),
            'AddProfileProductionSetting': lambda *args: AddProfileProductionSetting(*args),
            'CreateProfileProduction': lambda *args: CreateProfileProduction(*args),
            'ProductionProfileEditor': lambda *args: ProductionProfileEditor(*args),
            'ImportUsersAuthServiceDlg': lambda *args: ImportUsersAuthServiceDlg(*args),
            'AddMenuForm': lambda *args: AddMenuForm(*args),
            'AddMenuProfileForm': lambda *args: AddMenuProfileForm(*args)
        }
        return widgets[widgetName](*args) if widgetName in widgets else None

    def createDockSap(self, *args):
        dockDirector = DockDirector()
        mDockBuilder = MDockBuilder()
        dockDirector.constructSapMDock(mDockBuilder, *args)
        return mDockBuilder.getResult()