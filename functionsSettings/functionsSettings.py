
class FunctionsSettings:

    def __init__(self):
        super(FunctionsSettings, self).__init__()
    
    def getCreateActivities(self):
        return {
            'activity': [
                {
                    "layerName" : "unidade_trabalho",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getAlterBlock(self):
        return {
            'workUnit': [
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getDeleteActivities(self):
        return {
            'activity': [
                {
                    "layerName" : "subfase_",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": True
                },
                {
                    "layerName" : "atividade",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": True
                }
            ]
        }

    def getCopyWorkUnitSettings(self):
        return {
            'workUnit': [
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "problema_atividade",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "unidade_trabalho",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }
    
    def getLoadWorkUnitSettings(self):
        return {
            'workUnit': [
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "problema_atividade",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getDeleteAssociatedInputsSettings(self):
        return {
            'workUnit': [
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "problema_atividade",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "unidade_trabalho",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getAssociateInputsSettings(self):
        return {
            'workUnit': [
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "problema_atividade",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "unidade_trabalho",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }
    
    def getDeleteWorkUnitsSettings(self):
        return {
            'workUnit': [
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "problema_atividade",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "unidade_trabalho",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getAdvanceActivityToNextStepSettings(self):
        return {
            'activity': [
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "problema_atividade",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": True
                }
            ]
        }
    
    def getCreatePriorityGroupActivitySettings(self):
        return {
            'activity': [
                {
                    "layerName" : "subfase_",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": True
                }
            ]
        }

    def getCreateWorkUnitSettings(self):
        return {
            'product': [
                {
                    "layerName" : "produto",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ],
            'subfase': [
                {
                    "layerName" : "subfase",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getFillCommentsSettings(self):
        return {
            'activity': [
                {
                    "layerName" : "subfase_",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": True
                }
            ]
        }

    def getLockWorkspaceSettings(self):
        return {
            'workUnit': [
                {
                    "layerName" : "problema_atividade",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "ultimas_atividades_finalizadas",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getOpenActivitySettings(self):
        return {
            'activity': [
                {
                    "layerName" : "problema_atividade",
                    "fieldName" : "atividade_id",
                    "allSelection" : False,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "atividade_id",
                    "allSelection" : False,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "ultimas_atividades_finalizadas",
                    "fieldName" : "atividade_id",
                    "allSelection" : False,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "atividade_id",
                    "allSelection" : False,
                    "chooseAttribute": True
                }
            ]
        }

    def getPauseActivitySettings(self):
        return {
            'activity': [
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getRestartActivitySettings(self):
        return {
            'activity': [
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getReturnActivityToPreviousStepSettings(self):
        return {
            'activity': [
                {
                    "layerName" : "ultimas_atividades_finalizadas",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "atividades_finalizadas",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": True
                }
            ]
        }

    def getSetPriorityActivitySettings(self):
        return {
            'activity': [
                {
                    "layerName" : "subfase_",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": True
                }
            ]
        }

    def getUnlockWorkspaceSettings(self):
        return {
            'workUnit': [
                {
                    "layerName" : "problema_atividade",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "atividades_em_execucao",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "ultimas_atividades_finalizadas",
                    "fieldName" : "unidade_trabalho_id",
                    "allSelection" : True,
                    "chooseAttribute": False
                },
                {
                    "layerName" : "subfase_",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
                }
            ]
        }

    def getCreateScreensSettings(self):
        return {
            'primary': [
                {
                    "layerName" : "subfase_"
                },
                {
                    "layerName" : "fase_"
                },
                {
                    "layerName" : "linha_producao_"
                }
            ],
            'secundary': [
                {
                    "layerName" : "*"
                }
            ]
        }

    def getSettings(self, functionName, fieldName):
        functionNames = {
            'advanceActivityToNextStep': self.getAdvanceActivityToNextStepSettings,
            'createPriorityGroupActivity': self.getCreatePriorityGroupActivitySettings,
            #'openNextActivityByUser': self.getOpenNextActivityByUserSettings,
            'fillComments': self.getFillCommentsSettings,
            'openActivity': self.getOpenActivitySettings,
            'lockWorkspace': self.getLockWorkspaceSettings,
            'pauseActivity': self.getPauseActivitySettings,
            'unlockWorkspace': self.getUnlockWorkspaceSettings,
            'restartActivity': self.getRestartActivitySettings,
            'setPriorityActivity': self.getSetPriorityActivitySettings,
            'returnActivityToPreviousStep': self.getReturnActivityToPreviousStepSettings,
            'createWorkUnit': self.getCreateWorkUnitSettings,
            'deleteActivities': self.getDeleteActivities,
            'alterBlock': self.getAlterBlock,
            'createActivities': self.getCreateActivities,
            'deleteWorkUnits': self.getDeleteWorkUnitsSettings,
            'associateInputs': self.getAssociateInputsSettings,
            'loadWorkUnit': self.getLoadWorkUnitSettings,
            'copyWorkUnit': self.getCopyWorkUnitSettings,
            'deleteAssociatedInputs': self.getDeleteAssociatedInputsSettings,
            'createScreens': self.getCreateScreensSettings
        }
        return functionNames[functionName]()[fieldName]