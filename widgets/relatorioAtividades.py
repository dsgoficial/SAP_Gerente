import os, sys, copy
import csv
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget import DockWidget

class RelatorioAtividades(DockWidget):

    def __init__(self, sapCtrl, sap):
        super(RelatorioAtividades, self).__init__(controller=sapCtrl)
        self.sap = sap
        self.setWindowTitle('Consultar Atividades por Período')
        self.loadUsers(self.getUsers())

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "addAtividadePeriodo.ui"
        )
    
    def clearInput(self):
        # Reset calendars to current date
        self.dataInicioCal.setSelectedDate(QtCore.QDate.currentDate())
        self.dataFimCal.setSelectedDate(QtCore.QDate.currentDate())
        self.userCb.setCurrentIndex(0) 

    def validInput(self):
        return True
    
    def getDataInicio(self):
        # Format selected date from calendar as YYYY-MM-DD
        return self.dataInicioCal.selectedDate().toString("yyyy-MM-dd")

    def getDataFim(self):
        # Format selected date from calendar as YYYY-MM-DD
        return self.dataFimCal.selectedDate().toString("yyyy-MM-dd")
    
    def getUsers(self):
        return self.sap.getUsers()
    
    def getSelectedUser(self):
        return self.userCb.currentText()
    
    def loadUsers(self, data):
        self.userCb.clear()  
        self.userCb.addItem('Todos', None)
        for user in data:
            self.userCb.addItem(
                f"{user['tipo_posto_grad']} {user['nome_guerra']}",  
                user['id']
            )

    def runFunction(self):
        # Get dates from calendars
        data_inicio = self.getDataInicio()
        data_fim = self.getDataFim()
        
        # Compare dates - using the QDate objects directly for proper comparison
        if self.dataFimCal.selectedDate() < self.dataInicioCal.selectedDate():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'A data de fim não pode ser menor que a data de início.')
            return
            
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            selected_user = self.getSelectedUser()
            if selected_user == 'Todos':
                filePath = QtWidgets.QFileDialog.getSaveFileName(
                    self, 
                    '',
                    "relatorioAtividadesPorPeriodo.csv",
                    '*.csv'
                )
                dados = self.sap.relatorioAtividades(data_inicio, data_fim)
                exportar_para_csv(1, dados, filePath[0])
                QtWidgets.QMessageBox.information(self, 'Sucesso', 'CSV exportado com sucesso.')
            else:
                filePath = QtWidgets.QFileDialog.getSaveFileName(
                    self, 
                    '', 
                    f"relatorioAtividadesPorPeriodo_{selected_user}.csv", 
                    '*.csv'
                )
                user_id = self.userCb.currentData()
                dados = self.sap.relatorioAtividadeByUsers(user_id, data_inicio, data_fim)
                exportar_para_csv(2, dados, filePath[0])
                QtWidgets.QMessageBox.information(self, 'Sucesso', 'CSV exportado com sucesso.')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.close()

# The exportar_para_csv function remains unchanged
def exportar_para_csv(type, dados, caminho_arquivo):
    """
    Exporta os dados para um arquivo CSV.
    
    Args:
        type (int): 1 para relatório de todos os usuários, 2 para relatório de um usuário específico
        dados (list): Lista de dicionários contendo os dados a serem exportados
        caminho_arquivo (str): Caminho completo para o arquivo CSV a ser criado
    """
    if not caminho_arquivo:  # Se o usuário cancelou a escolha do arquivo
        return
    
    try:
        with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
            if type == 1:
                # Definir os campos para relatório de todos os usuários
                campos = ['nome_usuario', 'nome_bloco', 'qtd_ut']
                writer = csv.DictWriter(arquivo_csv, fieldnames=campos, extrasaction='ignore')
                
                # Escrever o cabeçalho com nomes amigáveis
                writer.writerow({
                    'nome_usuario': 'Nome do Usuário',
                    'nome_bloco': 'Nome do Bloco',
                    'qtd_ut': 'Unidades de Trabalho'
                })
                
                # Escrever os dados
                for item in dados:
                    if isinstance(item, dict):
                        writer.writerow(item)
                        
            elif type == 2:
                # Definir os campos para relatório de usuário específico
                campos = ['nome_subfase', 'nome_bloco', 'qtd_ut']
                writer = csv.DictWriter(arquivo_csv, fieldnames=campos, extrasaction='ignore')
                
                # Escrever o cabeçalho com nomes amigáveis
                writer.writerow({
                    'nome_subfase': 'Atividade',
                    'nome_bloco': 'Bloco',
                    'qtd_ut': 'Unidades de Trabalho'
                })
                
                # Escrever os dados
                for item in dados:
                    if isinstance(item, dict):
                        writer.writerow(item)
                        
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, 'Erro ao exportar', f'Ocorreu um erro ao exportar o CSV: {str(e)}')