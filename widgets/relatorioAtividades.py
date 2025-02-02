import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from itertools import groupby

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
        self.dataInicioLe.clear()
        self.dataFimLe.clear()
        self.userCb.setCurrentIndex(0) 

    def validInput(self):
        return  True
    
    def getDataInicio(self):
        return self.dataInicioLe.text()

    def getDataFim(self):
        return self.dataFimLe.text()
    
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
        if self.dataFimLe.text() < self.dataFimLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'A data de fim não pode ser menor que a data de início.')
            return
        if not self.dataInicioLe.text() or not self.dataFimLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Preencha os campos de data.')
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            selected_user = self.getSelectedUser()
            if selected_user == 'Todos':
                filePath = QtWidgets.QFileDialog.getSaveFileName(
                    self, 
                    '',
                    "relatorioPorPeriodo.pdf",
                    '*.pdf'
                )
                dados = self.sap.relatorioAtividades(self.getDataInicio(), self.getDataFim())
                exportar_para_pdf(1, dados, filePath[0])
                QtWidgets.QMessageBox.information(self, 'Sucesso', 'PDF baixado com sucesso.')
            else:
                filePath = QtWidgets.QFileDialog.getSaveFileName(
                    self, 
                    '', 
                    f"relatorioPorPeriodo_{selected_user}.pdf", 
                    '*.pdf'
                )
                user_id = self.userCb.currentData()
                dados = self.sap.relatorioAtividadeByUsers(user_id, self.getDataInicio(), self.getDataFim())
                exportar_para_pdf(2, dados, filePath[0])
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.close()

def exportar_para_pdf(type, dados, caminho_arquivo):
    pdf = SimpleDocTemplate(caminho_arquivo, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    elementos = []
    titulo = Paragraph("Relatório de Atividades por Período", styles['Title'])
    elementos.append(titulo)
    estilo_texto = styles['BodyText']
    estilo_texto.alignment = 1  # Alinhamento centralizado
    if type == 1:
        dados_tabela = [["Nome do Usuário", "Nome do Bloco", "Unidades de Trabalho"]]  # Cabeçalho da tabela
        for item in dados:
            if isinstance(item, dict):
                nome_usuario = Paragraph(item.get('nome_usuario', 'N/A'), estilo_texto)
                nome_bloco = Paragraph(item.get('nome_bloco', 'N/A'), estilo_texto)
                qtd_ut = Paragraph(item.get('qtd_ut', 'N/A'), estilo_texto)
                dados_tabela.append([nome_usuario, nome_bloco, qtd_ut])
        tabela = Table(dados_tabela)
    # if type == 2:
    #     dados_tabela = [["Atividade", "Bloco", "Unidades de Trabalho"]]  # Cabeçalho da tabela
    #     for item in dados:
    #         if isinstance(item, dict):
    #             nome_subfase = Paragraph(item.get('nome_subfase', 'N/A'), estilo_texto)
    #             nome_bloco = Paragraph(item.get('nome_bloco', 'N/A'), estilo_texto)
    #             qtd_ut = Paragraph(item.get('qtd_ut', 'N/A'), estilo_texto)
    #             dados_tabela.append([nome_subfase, nome_bloco, qtd_ut])
    #     tabela = Table(dados_tabela)
    # estilo_tabela = TableStyle([
    #     ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Cabeçalho cinza
    #     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto do cabeçalho branco
    #     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinhamento centralizado
    #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fonte do cabeçalho em negrito
    #     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Espaçamento inferior do cabeçalho
    #     ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fundo da tabela bege
    #     ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Linhas da tabela
    # ])
    # tabela.setStyle(estilo_tabela)

    if type == 2:
        dados_agrupados = []

        # Agrupa os itens pelo nome_subfase
        for item in dados:
            if isinstance(item, dict):
                nome_subfase = item.get('nome_subfase', 'N/A')
                nome_bloco = item.get('nome_bloco', 'N/A')
                qtd_ut = item.get('qtd_ut', 'N/A')
                dados_agrupados.append((nome_subfase, nome_bloco, qtd_ut))

        # Ordena os dados pelo nome_subfase para garantir que itens iguais estejam adjacentes
        dados_agrupados.sort(key=lambda x: x[0])

        # Processa os dados para criar a estrutura da tabela
        dados_tabela = [["Atividade", "Bloco", "Unidades de Trabalho"]]  # Cabeçalho

        # Converte os dados para Paragraphs
        for item in dados_agrupados:
            nome_subfase = Paragraph(str(item[0]), estilo_texto)
            nome_bloco = Paragraph(str(item[1]), estilo_texto)
            qtd_ut = Paragraph(str(item[2]), estilo_texto)
            dados_tabela.append([nome_subfase, nome_bloco, qtd_ut])

        tabela = Table(dados_tabela)

        # Cria o estilo base da tabela
        estilo_tabela = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinhamento vertical para todas as células
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        # Adiciona os comandos de merge para células com mesmo nome_subfase
        current_subfase = None
        merge_start = 1  # Começa após o cabeçalho

        for i in range(1, len(dados_tabela)):
            subfase_atual = dados_tabela[i][0].text if isinstance(dados_tabela[i][0], Paragraph) else dados_tabela[i][0]

            if current_subfase != subfase_atual:
                if current_subfase is not None and i - merge_start > 0:
                    # Adiciona o comando para mesclar as células
                    estilo_tabela.add('SPAN', (0, merge_start), (0, i - 1))
                merge_start = i
                current_subfase = subfase_atual

        # Verifica se é necessário mesclar o último grupo
        if merge_start < len(dados_tabela) - 1:
            estilo_tabela.add('SPAN', (0, merge_start), (0, len(dados_tabela) - 1))

        tabela.setStyle(estilo_tabela)


    elementos.append(tabela)
    pdf.build(elementos)