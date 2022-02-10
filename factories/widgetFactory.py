
from Ferramentas_Gerencia.factories.mDockBuilder import MDockBuilder
from Ferramentas_Gerencia.factories.dockDirector import DockDirector
from Ferramentas_Gerencia.factories.mStylesSingleton  import MStylesSingleton
from Ferramentas_Gerencia.factories.mModelsSingleton  import MModelsSingleton
from Ferramentas_Gerencia.factories.mFmeServersSingleton  import MFmeServersSingleton
from Ferramentas_Gerencia.factories.mFmeProfilesSingleton  import MFmeProfilesSingleton
from Ferramentas_Gerencia.factories.mRulesSingleton  import MRulesSingleton
from Ferramentas_Gerencia.factories.mRuleSetSingleton  import MRuleSetSingleton
from Ferramentas_Gerencia.factories.mUsersPrivilegesSingleton  import MUsersPrivilegesSingleton
from Ferramentas_Gerencia.factories.mEditLayersSingleton  import MEditLayersSingleton
from Ferramentas_Gerencia.factories.mImportLayersSingleton  import MImportLayersSingleton
from Ferramentas_Gerencia.factories.addStyleFormSingleton  import AddStyleFormSingleton
from Ferramentas_Gerencia.factories.addModelFormSingleton  import AddModelFormSingleton
from Ferramentas_Gerencia.factories.addRuleFormSingleton  import AddRuleFormSingleton
from Ferramentas_Gerencia.factories.addRuleSetFormSingleton  import AddRuleSetFormSingleton
from Ferramentas_Gerencia.factories.addRulesCsvFormSingleton  import AddRulesCsvFormSingleton
from Ferramentas_Gerencia.factories.addFmeServerFormSingleton  import AddFmeServerFormSingleton
from Ferramentas_Gerencia.factories.addFmeProfileFormSingleton  import AddFmeProfileFormSingleton
from Ferramentas_Gerencia.factories.rulesSingleton  import RulesSingleton
from Ferramentas_Gerencia.factories.mModelProfilesSingleton  import MModelProfilesSingleton
from Ferramentas_Gerencia.factories.addModelProfileFormSingleton  import AddModelProfileFormSingleton
from Ferramentas_Gerencia.factories.mRuleProfilesSingleton  import MRuleProfilesSingleton
from Ferramentas_Gerencia.factories.addRuleProfileFormSingleton  import AddRuleProfileFormSingleton
from Ferramentas_Gerencia.factories.mStyleProfilesSingleton  import MStyleProfilesSingleton
from Ferramentas_Gerencia.factories.addStyleProfileFormSingleton  import AddStyleProfileFormSingleton
from Ferramentas_Gerencia.widgets.associateUserToProjects  import AssociateUserToProjects
from Ferramentas_Gerencia.widgets.addUserProject  import AddUserProject
from Ferramentas_Gerencia.widgets.associateUserToProfiles  import AssociateUserToProfiles
from Ferramentas_Gerencia.widgets.addUserProfileProduction import AddUserProfileProduction
from Ferramentas_Gerencia.widgets.profileProductionSetting import ProfileProductionSetting
from Ferramentas_Gerencia.widgets.addProfileProductionSetting import AddProfileProductionSetting
from Ferramentas_Gerencia.widgets.createProfileProduction import CreateProfileProduction
from Ferramentas_Gerencia.widgets.productionProfileEditor import ProductionProfileEditor

class WidgetFactory:

    def create(self, widgetName, *args):
        widgets = {
            'DockSap': lambda *args: self.createDockSap(*args),
            'MStyles': lambda *args: MStylesSingleton.getInstance(*args),
            'MModels': lambda *args: MModelsSingleton.getInstance(*args),
            'MFmeServers': lambda *args: MFmeServersSingleton.getInstance(*args),
            'MFmeProfiles': lambda *args: MFmeProfilesSingleton.getInstance(*args),
            'MRules': lambda *args: MRulesSingleton.getInstance(*args),
            'MRuleSet': lambda *args: MRuleSetSingleton.getInstance(*args),
            'MUsersPrivileges': lambda *args: MUsersPrivilegesSingleton.getInstance(*args),
            'MEditLayers': lambda *args: MEditLayersSingleton.getInstance(*args),
            'MImportLayers': lambda *args: MImportLayersSingleton.getInstance(*args),
            'AddStyleForm': lambda *args: AddStyleFormSingleton.getInstance(*args),
            'AddModelForm': lambda *args: AddModelFormSingleton.getInstance(*args),
            'AddRuleForm': lambda *args: AddRuleFormSingleton.getInstance(*args),
            'AddRuleSetForm': lambda *args: AddRuleSetFormSingleton.getInstance(*args),
            'AddRulesCsvForm': lambda *args: AddRulesCsvFormSingleton.getInstance(*args),
            'AddFmeServerForm': lambda *args: AddFmeServerFormSingleton.getInstance(*args),
            'AddFmeProfileForm': lambda *args: AddFmeProfileFormSingleton.getInstance(*args),
            'Rules': lambda *args: RulesSingleton.getInstance(*args),
            'MModelProfiles': lambda *args: MModelProfilesSingleton.getInstance(*args),
            'AddModelProfileForm': lambda *args: AddModelProfileFormSingleton.getInstance(*args),
            'MRuleProfiles': lambda *args: MRuleProfilesSingleton.getInstance(*args),
            'AddRuleProfileForm': lambda *args: AddRuleProfileFormSingleton.getInstance(*args),
            'MStyleProfiles': lambda *args: MStyleProfilesSingleton.getInstance(*args),
            'AddStyleProfileForm': lambda *args: AddStyleProfileFormSingleton.getInstance(*args),
            'AssociateUserToProjects': lambda *args: AssociateUserToProjects(*args),
            'AddUserProject': lambda *args: AddUserProject(*args),
            'AssociateUserToProfiles': lambda *args: AssociateUserToProfiles(*args),
            'AddUserProfileProduction': lambda *args: AddUserProfileProduction(*args),
            'ProfileProductionSetting': lambda *args: ProfileProductionSetting(*args),
            'AddProfileProductionSetting': lambda *args: AddProfileProductionSetting(*args),
            'CreateProfileProduction': lambda *args: CreateProfileProduction(*args),
            'ProductionProfileEditor': lambda *args: ProductionProfileEditor(*args),
        }
        return widgets[widgetName](*args) if widgetName in widgets else None

    def createDockSap(self, controller):
        dockDirector = DockDirector()
        mDockBuilder = MDockBuilder()
        dockDirector.constructSapMDock(mDockBuilder, controller)
        return mDockBuilder.getResult()