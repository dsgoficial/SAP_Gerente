from SAP_Gerente.modules.sap.dataModels.sapActivity import SapActivity

class DataModelFactory:

    def createDataModel(self, modelName):
        dataModels = {
            'SapActivity': SapActivity
        }
        return dataModels[modelName]()