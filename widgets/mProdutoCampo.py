# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2 import MDialogV2
from .addProdutoCampo import AdicionarProdutoCampo
import json

class MProdutoCampo(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap
            ):
        super(MProdutoCampo, self).__init__(controller=controller)
        self.qgis = qgis
        self.sap = sap
        self.adicionarProdutoCampoDlg = None
        self.tableWidget.setColumnHidden(6, True)
        
        # Carregar lista de campos para o filtro
        self.carregarCampos()
        
        # Conectar eventos
        self.campoCb.currentIndexChanged.connect(self.fetchData)
        self.refreshBtn.clicked.connect(self.fetchData)
        
        # Carregar dados iniciais
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mProdutoCampo.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2, 3, 4, 5]
    
    def carregarCampos(self):
        """
        Carrega a lista de campos para o filtro
        """
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            campos = self.sap.getCampos()
            QtWidgets.QApplication.restoreOverrideCursor()
            
            self.campoCb.clear()
            self.campoCb.addItem("Todos", None)
            
            if campos:
                for campo in campos:
                    self.campoCb.addItem(f"{campo['nome']} ({campo['id']})", campo['id'])
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Erro', f'Erro ao carregar campos: {str(e)}')

    def fetchData(self):
        """
        Busca dados de produtos associados a campos com base no filtro selecionado
        """
        campo_id = self.campoCb.currentData()
        
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            
            # Buscar produtos associados a campos (implementar na API)
            if campo_id:
                data = self.sap.getProdutosPorCampo(campo_id)
            else:
                data = self.sap.getProdutosCampo()
                
            self.addRows(data)
            
            QtWidgets.QApplication.restoreOverrideCursor()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Erro', f'Erro ao buscar produtos: {str(e)}')

    def addRows(self, produtos_campos):
        """
        Adiciona linhas à tabela
        """
        self.clearAllItems()
        for produto_campo in produtos_campos:
            print(produto_campo)
            self.addRow(
                produto_campo['id'],
                produto_campo['produto_nome'],
                produto_campo['nome'],
                produto_campo['nome_lote'],
                json.dumps(produto_campo)
            )
        self.adjustTable()

    def addRow(self, 
            primaryKey, 
            produto_nome,
            campo_nome,
            lote_nome,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setCellWidget(idx, 2, self.createLabelV2(produto_nome, idx, 2))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(campo_nome))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(lote_nome))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(dump))
        optionColumn = 1
        self.tableWidget.setCellWidget(
            idx, 
            optionColumn, 
            self.createRowEditWidget(
                self.tableWidget,
                idx,
                optionColumn, 
                self.handleViewBtn, 
                self.handleDeleteBtn
            )
        )

    def handleViewBtn(self, index):
        """
        Manipula o clique no botão de visualização.
        Mostra informações detalhadas da associação produto-campo.
        
        Args:
            index: Índice da linha na tabela
        """
        # Obtém os dados completos 
        dados = self.getRowData(index.row())
        
        # Mostra informações detalhadas
        info = f"ID: {dados.get('id', 'N/A')}\n"
        info += f"Produto: {dados.get('produto_nome', 'N/A')}\n"
        info += f"INOM: {dados.get('inom', 'N/A')}\n"
        info += f"Escala: 1:{dados.get('denominador_escala', 'N/A')}\n"
        info += f"Campo: {dados.get('campo_nome', 'N/A')}\n"
        info += f"Lote: {dados.get('lote_nome', 'N/A')}\n"
        
        self.showInfo('Detalhes da Associação', info)
        
    def handleDeleteBtn(self, index):
        """
        Manipula o clique no botão de exclusão.
        
        Args:
            index: Índice da linha na tabela
        """
        result = self.showQuestion('Atenção', 'Tem certeza que deseja remover esta associação?')
        if not result:
            return
        
        dados = self.getRowData(index.row())
        try:
            # Chamar API para remover a associação
            message = self.sap.deletaProdutoCampo(dados['id'])
            message and self.showInfo('Aviso', message)
            self.fetchData()
        except Exception as e:
            self.showError('Erro', f'Erro ao remover associação: {str(e)}')

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        data = json.loads(self.tableWidget.model().index(rowIndex, 6).data())
        return data

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        # Abre a janela AdicionarProdutoCampo
        self.adicionarProdutoCampoDlg = AdicionarProdutoCampo(self.controller, self.sap, self.qgis)
        # Atualizar tabela após adicionar uma associação
        self.adicionarProdutoCampoDlg.finished.connect(self.fetchData)
        self.adicionarProdutoCampoDlg.show()