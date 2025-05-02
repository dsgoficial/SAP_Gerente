import os, sys, copy, csv
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget import DockWidget
from itertools import groupby

class RelatorioGeral(DockWidget):

    def __init__(self, sapCtrl, sap):
        super(RelatorioGeral, self).__init__(controller=sapCtrl)
        self.sap = sap
        self.setWindowTitle('Relatório Geral')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "addAtividadeGeral.ui"
        )
    
    def clearInput(self):
        # Reset calendars to current date
        self.dataInicioCal.setSelectedDate(QtCore.QDate.currentDate())
        self.dataFimCal.setSelectedDate(QtCore.QDate.currentDate())

    def validInput(self):
        return True
    
    def getDataInicio(self):
        # Format selected date from calendar as YYYY-MM-DD
        return self.dataInicioCal.selectedDate().toString("yyyy-MM-dd")

    def getDataFim(self):
        # Format selected date from calendar as YYYY-MM-DD
        return self.dataFimCal.selectedDate().toString("yyyy-MM-dd")

    def runFunction(self):
        # Compare dates using QDate objects directly for proper comparison
        if self.dataFimCal.selectedDate() < self.dataInicioCal.selectedDate():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'A data de fim não pode ser menor que a data de início.')
            return
            
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            filePath = QtWidgets.QFileDialog.getSaveFileName(
                self, 
                '',
                "relatorioPorPeriodo.csv",
                '*.csv'
            )
            # Get dates in string format for the database query
            data_inicio = self.getDataInicio()
            data_fim = self.getDataFim()
            
            dados = self.sap.relatorioByLots(data_inicio, data_fim)
            exportar_para_csv(dados, filePath[0])
            QtWidgets.QMessageBox.information(self, 'Sucesso', 'CSV baixado com sucesso.')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.close()

# The exportar_para_csv function remains unchanged
def exportar_para_csv(dados, caminho_arquivo):
    # Definir os cabeçalhos do CSV baseados nos campos recebidos da consulta SQL
    cabecalhos = ["ID Lote", "Nome Lote", "Total Atividades", "Percentual Executado", 
                 "Executadas no Período", "Tempo Médio (horas)", "Desvio Padrão (horas)"]
    
    with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        
        # Escrever o cabeçalho
        escritor.writerow(cabecalhos)
        
        # Escrever os dados com as chaves corretas
        for item in dados:
            if isinstance(item, dict):
                # Formatação dos números para melhor legibilidade
                percent_exec = float(item.get('percent_exec', 0)) * 100  # Converter para porcentagem
                tempo_medio = float(item.get('tempo_medio_horas', 0))
                desvio_padrao = float(item.get('desvio_padrao_tempo', 0))
                
                linha = [
                    item.get('lote_id', 'N/A'),
                    item.get('lote_nome', 'N/A'),
                    item.get('total_atividades', 'N/A'),
                    f"{percent_exec:.2f}%",  # Formatado como porcentagem com 2 casas decimais
                    item.get('exec_no_periodo', 'N/A'),
                    f"{tempo_medio:.2f}",  # Formatado com 2 casas decimais
                    f"{desvio_padrao:.2f}"  # Formatado com 2 casas decimais
                ]
                escritor.writerow(linha)