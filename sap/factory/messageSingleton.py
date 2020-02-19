from Ferramentas_Gerencia.sap.dialogs.message  import Message

class MessageSingleton:

    message = None

    @staticmethod
    def getInstance():
        if not MessageSingleton.message:
            MessageSingleton.message = Message()
        return MessageSingleton.message