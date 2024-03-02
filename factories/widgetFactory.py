
from SAP_Gerente.factories.mDockBuilder import MDockBuilder
from SAP_Gerente.factories.dockDirector import DockDirector
from SAP_Gerente.widgets.associateUserToBlocks  import AssociateUserToBlocks
from SAP_Gerente.widgets.associateUserToProfiles  import AssociateUserToProfiles
from SAP_Gerente.widgets.addUserProfileProduction import AddUserProfileProduction
from SAP_Gerente.widgets.profileProductionSetting import ProfileProductionSetting
from SAP_Gerente.widgets.addProfileProductionSetting import AddProfileProductionSetting
from SAP_Gerente.widgets.createProfileProduction import CreateProfileProduction
from SAP_Gerente.widgets.productionProfileEditor import ProductionProfileEditor
from SAP_Gerente.widgets.addRuleFormV2  import AddRuleFormV2
from SAP_Gerente.widgets.importUsersAuthServiceDlg  import ImportUsersAuthServiceDlg
from SAP_Gerente.widgets.addMenuForm  import AddMenuForm
from SAP_Gerente.widgets.addMenuProfileForm  import AddMenuProfileForm

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