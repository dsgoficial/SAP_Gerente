from qgis.gui import QgsExpressionLineEdit

class LineEditExpression(QgsExpressionLineEdit):
    
    def __init__(self):
        super(LineEditExpression, self).__init__()