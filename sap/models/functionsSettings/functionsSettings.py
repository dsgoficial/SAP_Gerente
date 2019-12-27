

class FunctionsSettings:

    def getAddNewRevisionCorrectionSettings(self):
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

    def getAddNewRevisionSettings(self):
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
                    "layerName" : "produto",
                    "fieldName" : "id",
                    "allSelection" : True,
                    "chooseAttribute": False
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
                    "layerName" : "subfase_",
                    "fieldName" : "atividade_id",
                    "allSelection" : True,
                    "chooseAttribute": True
                }
            ]
        }

    def getSettings(self, functionName, fieldName):
        if functionName == 'addNewRevision':
            return self.getAddNewRevisionSettings()[fieldName]
        elif functionName == 'addNewRevisionCorrection':
            return self.getAddNewRevisionCorrectionSettings()[fieldName]
        elif functionName == 'advanceActivityToNextStep':
            return self.getAdvanceActivityToNextStepSettings()[fieldName]
        elif functionName == 'createPriorityGroupActivity':
            return self.getCreatePriorityGroupActivitySettings()[fieldName]
        elif functionName == 'openNextActivityByUserSettings':
            return self.getOpenNextActivityByUserSettings()[fieldName]
        elif functionName == 'fillCommentsSettings':
            return self.getFillCommentsSettings()[fieldName]
        elif functionName == 'openActivitySettings':
            return self.getOpenActivitySettings()[fieldName]
        elif functionName == 'lockWorkspaceSettings':
            return self.getLockWorkspaceSettings()[fieldName]
        elif functionName == 'lockWorkspaceSettings':
            return self.getLockWorkspaceSettings()[fieldName]
        elif functionName == 'pauseActivitySettings':
            return self.getPauseActivitySettings()[fieldName]
        elif functionName == 'unlockWorkspaceSettings':
            return self.getUnlockWorkspaceSettings()[fieldName]
        elif functionName == 'restartActivitySettings':
            return self.getRestartActivitySettings()[fieldName]
        elif functionName == 'setPriorityActivitySettings':
            return self.getSetPriorityActivitySettings()[fieldName]
        elif functionName == 'returnActivityToPreviousStepSettings':
            return self.getReturnActivityToPreviousStepSettings()[fieldName]
        elif functionName == 'createWorkUnit':
            return self.getCreateWorkUnitSettings()[fieldName]