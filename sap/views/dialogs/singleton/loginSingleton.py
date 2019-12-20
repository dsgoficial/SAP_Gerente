from Ferramentas_Gerencia.sap.views.dialogs.login  import Login

class LoginSingleton:

    login = None

    @staticmethod
    def getInstance(loginCtrl):
        if not LoginSingleton.login:
            LoginSingleton.login = Login(loginCtrl)
        return LoginSingleton.login