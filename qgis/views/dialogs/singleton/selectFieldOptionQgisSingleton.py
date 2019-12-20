from Ferramentas_Gerencia.qgis.views.dialogs.selectFieldOptionQgis import SelectFieldOptionQgis

class SelectFieldOptionQgisSingleton:

    selectFieldDlg = None

    @staticmethod
    def getInstance():
        if not SelectFieldOptionQgisSingleton.selectFieldDlg:
            SelectFieldOptionQgisSingleton.selectFieldDlg = SelectFieldOptionQgis()
        return SelectFieldOptionQgisSingleton.selectFieldDlg