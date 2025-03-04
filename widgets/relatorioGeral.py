import os, sys, copy, csv
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
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
        self.dataInicioLe.clear()
        self.dataFimLe.clear()

    def validInput(self):
        return True
    
    def getDataInicio(self):
        return self.dataInicioLe.text()

    def getDataFim(self):
        return self.dataFimLe.text()

    def runFunction(self):
        if self.dataFimLe.text() < self.dataInicioLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'A data de fim não pode ser menor que a data de início.')
            return
        if not self.dataInicioLe.text() or not self.dataFimLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Preencha os campos de data.')
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            filePath = QtWidgets.QFileDialog.getSaveFileName(
                self, 
                '',
                "relatorioPorPeriodo.csv",
                '*.csv'
            )
            dados = self.sap.relatorioByLots(self.getDataInicio(), self.getDataFim())
            exportar_para_csv(dados, filePath[0])
            QtWidgets.QMessageBox.information(self, 'Sucesso', 'CSV baixado com sucesso.')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.close()

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