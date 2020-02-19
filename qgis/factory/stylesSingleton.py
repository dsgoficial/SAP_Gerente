from Ferramentas_Gerencia.qgis.styles.styles import Styles

class StylesSingleton:

    styles = None

    @staticmethod
    def getInstance():
        if not StylesSingleton.styles:
            StylesSingleton.styles = Styles()
        return StylesSingleton.styles