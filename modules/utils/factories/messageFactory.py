from SAP_Gerente.modules.utils.message.htmlMessageDialog  import HtmlMessageDialog
from SAP_Gerente.modules.utils.message.infoMessageBox  import InfoMessageBox
from SAP_Gerente.modules.utils.message.errorMessageBox  import ErrorMessageBox
from SAP_Gerente.modules.utils.message.questionMessageBox  import QuestionMessageBox

class MessageFactory:

    def createMessage(self, messageType):
        messageTypes = {
            'HtmlMessageDialog': HtmlMessageDialog,
            'InfoMessageBox': InfoMessageBox,
            'ErrorMessageBox': ErrorMessageBox,
            'QuestionMessageBox': QuestionMessageBox

        }
        return messageTypes[messageType]()