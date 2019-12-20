from Ferramentas_Gerencia.qgis.models.styles.stylesQgis import StylesQgis

class StylesQgisSingleton:

    stylesQgis = None

    @staticmethod
    def getInstance():
        if not StylesQgisSingleton.stylesQgis:
            StylesQgisSingleton.stylesQgis = StylesQgis()
        return StylesQgisSingleton.stylesQgis