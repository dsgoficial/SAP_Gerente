import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget  import DockWidget
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
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
        return  True
    
    def getDataInicio(self):
        return self.dataInicioLe.text()

    def getDataFim(self):
        return self.dataFimLe.text()

    def runFunction(self):
        if self.dataFimLe.text() < self.dataFimLe.text():
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
                "relatorioPorPeriodo.pdf",
                '*.pdf'
            )
            dados = self.sap.relatorioByLots(self.getDataInicio(), self.getDataFim())
            exportar_para_pdf(1, dados, filePath[0])
            QtWidgets.QMessageBox.information(self, 'Sucesso', 'PDF baixado com sucesso.')
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
    dados_tabela = [["Nome Lote", "Total Atividades", "Total Finalizadas", "Finalizadas no mês", "Percentual concluído", "Qtd Operadores"]]  # Cabeçalho da tabela
    for item in dados:
        if isinstance(item, dict):
            lote_nome = Paragraph(item.get('nome', 'N/A'), estilo_texto)
            total_atividades = Paragraph(item.get('numero_total', 'N/A'), estilo_texto)
            total_finalizadas = Paragraph(item.get('finalizadas_total', 'N/A'), estilo_texto)
            exec_periodo = Paragraph(item.get('finalizadas_mes', 'N/A'), estilo_texto)
            percent_conclu = Paragraph(item.get('percentual_concluido', 'N/A'), estilo_texto)
            operadores = Paragraph(item.get('total_usuarios', 'N/A'), estilo_texto)
            dados_tabela.append([lote_nome, total_atividades, total_finalizadas, exec_periodo, percent_conclu, operadores])
    tabela = Table(dados_tabela)

    estilo_tabela = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Cabeçalho cinza
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto do cabeçalho branco
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinhamento centralizado
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fonte do cabeçalho em negrito
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Espaçamento inferior do cabeçalho
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fundo da tabela bege
        ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Linhas da tabela
    ])
    tabela.setStyle(estilo_tabela)
    elementos.append(tabela)
    pdf.build(elementos)