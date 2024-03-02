from SAP_Gerente.modules.sap.widgets.login  import Login

class LoginSingleton:

    login = None

    @staticmethod
    def getInstance(loginCtrl):
        if not LoginSingleton.login:
            LoginSingleton.login = Login(loginCtrl)
        return LoginSingleton.login