from SAP_Gerente.modules.qgis.widgets.selectFieldOption import SelectFieldOption

class SelectFieldOptionSingleton:

    selectFieldDlg = None

    @staticmethod
    def getInstance():
        if not SelectFieldOptionSingleton.selectFieldDlg:
            SelectFieldOptionSingleton.selectFieldDlg = SelectFieldOption()
        return SelectFieldOptionSingleton.selectFieldDlg