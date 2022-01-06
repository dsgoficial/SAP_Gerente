
from Ferramentas_Gerencia.factories.managementDockBuilder import ManagementDockBuilder
from Ferramentas_Gerencia.factories.dockDirector import DockDirector
from Ferramentas_Gerencia.factories.managementStylesSingleton  import ManagementStylesSingleton
from Ferramentas_Gerencia.factories.managementModelsSingleton  import ManagementModelsSingleton
from Ferramentas_Gerencia.factories.managementFmeServersSingleton  import ManagementFmeServersSingleton
from Ferramentas_Gerencia.factories.managementFmeProfilesSingleton  import ManagementFmeProfilesSingleton
from Ferramentas_Gerencia.factories.managementRulesSingleton  import ManagementRulesSingleton
from Ferramentas_Gerencia.factories.managementRuleSetSingleton  import ManagementRuleSetSingleton
from Ferramentas_Gerencia.factories.managementUsersPrivilegesSingleton  import ManagementUsersPrivilegesSingleton
from Ferramentas_Gerencia.factories.managementEditLayersSingleton  import ManagementEditLayersSingleton
from Ferramentas_Gerencia.factories.managementImportLayersSingleton  import ManagementImportLayersSingleton
from Ferramentas_Gerencia.factories.addStyleFormSingleton  import AddStyleFormSingleton
from Ferramentas_Gerencia.factories.addModelFormSingleton  import AddModelFormSingleton
from Ferramentas_Gerencia.factories.addRuleFormSingleton  import AddRuleFormSingleton
from Ferramentas_Gerencia.factories.addRuleSetFormSingleton  import AddRuleSetFormSingleton
from Ferramentas_Gerencia.factories.addRulesCsvFormSingleton  import AddRulesCsvFormSingleton
from Ferramentas_Gerencia.factories.addFmeServerFormSingleton  import AddFmeServerFormSingleton
from Ferramentas_Gerencia.factories.addFmeProfileFormSingleton  import AddFmeProfileFormSingleton
from Ferramentas_Gerencia.factories.rulesSingleton  import RulesSingleton
from Ferramentas_Gerencia.factories.managementModelProfilesSingleton  import ManagementModelProfilesSingleton
from Ferramentas_Gerencia.factories.addModelProfileFormSingleton  import AddModelProfileFormSingleton
from Ferramentas_Gerencia.factories.managementRuleProfilesSingleton  import ManagementRuleProfilesSingleton
from Ferramentas_Gerencia.factories.addRuleProfileFormSingleton  import AddRuleProfileFormSingleton
from Ferramentas_Gerencia.factories.managementStyleProfilesSingleton  import ManagementStyleProfilesSingleton
from Ferramentas_Gerencia.factories.addStyleProfileFormSingleton  import AddStyleProfileFormSingleton

class WidgetFactory:

    def create(self, widgetName, *args):
        widgets = {
            'DockSap': lambda *args: self.createDockSap(*args),
            'ManagementStyles': lambda *args: ManagementStylesSingleton.getInstance(*args),
            'ManagementModels': lambda *args: ManagementModelsSingleton.getInstance(*args),
            'ManagementFmeServers': lambda *args: ManagementFmeServersSingleton.getInstance(*args),
            'ManagementFmeProfiles': lambda *args: ManagementFmeProfilesSingleton.getInstance(*args),
            'ManagementRules': lambda *args: ManagementRulesSingleton.getInstance(*args),
            'ManagementRuleSet': lambda *args: ManagementRuleSetSingleton.getInstance(*args),
            'ManagementUsersPrivileges': lambda *args: ManagementUsersPrivilegesSingleton.getInstance(*args),
            'ManagementEditLayers': lambda *args: ManagementEditLayersSingleton.getInstance(*args),
            'ManagementImportLayers': lambda *args: ManagementImportLayersSingleton.getInstance(*args),
            'AddStyleForm': lambda *args: AddStyleFormSingleton.getInstance(*args),
            'AddModelForm': lambda *args: AddModelFormSingleton.getInstance(*args),
            'AddRuleForm': lambda *args: AddRuleFormSingleton.getInstance(*args),
            'AddRuleSetForm': lambda *args: AddRuleSetFormSingleton.getInstance(*args),
            'AddRulesCsvForm': lambda *args: AddRulesCsvFormSingleton.getInstance(*args),
            'AddFmeServerForm': lambda *args: AddFmeServerFormSingleton.getInstance(*args),
            'AddFmeProfileForm': lambda *args: AddFmeProfileFormSingleton.getInstance(*args),
            'Rules': lambda *args: RulesSingleton.getInstance(*args),
            'ManagementModelProfiles': lambda *args: ManagementModelProfilesSingleton.getInstance(*args),
            'AddModelProfileForm': lambda *args: AddModelProfileFormSingleton.getInstance(*args),
            'ManagementRuleProfiles': lambda *args: ManagementRuleProfilesSingleton.getInstance(*args),
            'AddRuleProfileForm': lambda *args: AddRuleProfileFormSingleton.getInstance(*args),
            'ManagementStyleProfiles': lambda *args: ManagementStyleProfilesSingleton.getInstance(*args),
            'AddStyleProfileForm': lambda *args: AddStyleProfileFormSingleton.getInstance(*args),
        }
        return widgets[widgetName](*args) if widgetName in widgets else None

    def createDockSap(self, controller):
        dockDirector = DockDirector()
        managementDockBuilder = ManagementDockBuilder()
        dockDirector.constructSapManagementDock(managementDockBuilder, controller)
        return managementDockBuilder.getResult()