# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2 import MDialogV2
from .addProdutoCampo import AdicionarProdutoCampo
import json
from collections import defaultdict

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
        
        # Modificar estrutura da tabela para mostrar N produtos por campo
        self.setupTable()
        
        # Carregar lista de campos para o filtro
        self.carregarCampos()
        
        # Conectar eventos
        self.campoCb.currentIndexChanged.connect(self.fetchData)
        
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
        return [2, 3, 4]
    
    def setupTable(self):
        """
        Configura a estrutura da tabela para mostrar N produtos por campo
        """
        # Esconder colunas de ID e dump
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(3, True)
        self.tableWidget.setColumnHidden(6, True)
        
        # Configurar cabeçalhos
        headers = ['ID', 'Opções', 'Campo', 'Lote', 'Produtos', 'Total']
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        
        # Configurar para auto expandir a coluna de produtos
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
    
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
                    self.campoCb.addItem(f"{campo['nome']}", campo['id'])
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
            
            # Buscar produtos associados a campos
            if campo_id:
                data = self.sap.getProdutosByCampoId(campo_id)
            else:
                data = self.sap.getProdutosCampo()
                
            self.processAndDisplayData(data)
            
            QtWidgets.QApplication.restoreOverrideCursor()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.showError('Erro', f'Erro ao buscar produtos: {str(e)}')

    def processAndDisplayData(self, produtos_campos):
        """
        Processa dados agrupando por campo e exibe na tabela
        """
        self.clearAllItems()
        
        # Agrupar por campo
        campos_dict = defaultdict(list)
        
        for produto_campo in produtos_campos:
            campo_id = produto_campo['id']
            campo_nome = produto_campo['nome']
            campos_dict[campo_id].append(produto_campo)
        
        # Adicionar cada campo como uma linha, com seus produtos
        for campo_id, produtos in campos_dict.items():
            # Pegamos o primeiro item para obter informações comuns do campo
            primeiro_produto = produtos[0]
            campo_nome = primeiro_produto['nome']
            lote_nome = primeiro_produto['nome_lote']
            
            # Criar lista de produtos para exibição (separados por vírgula)
            produtos_nomes = []
            for p in produtos:
                if 'produto_nome' in p and p['produto_nome']:
                    produtos_nomes.append(p['produto_nome'])
                elif 'mi' in p:
                    produtos_nomes.append(p['mi'])
                else:
                    produtos_nomes.append("Sem nome")  # Fallback caso nem nome nem mi existam
                    
            produtos_str = ", ".join(produtos_nomes)
            
            # Adicionar linha com o campo e seus produtos
            self.addRow(
                campo_id,
                campo_nome,
                lote_nome,
                produtos_str,
                len(produtos),
                json.dumps(produtos),  # Armazenar todos os dados para uso posterior
                produtos_nomes  # Passar a lista de nomes para calcular altura dinâmica
            )
        
        self.adjustTable()

    def addRow(self, 
            campo_id, 
            campo_nome,
            lote_nome,
            produtos_str,
            total_produtos,
            dump,
            produtos_nomes=None
        ):
        """
        Adiciona uma linha à tabela representando um campo e seus produtos associados
        """
        idx = self.getRowIndex(campo_id)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        
        # Coluna ID (oculta)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(campo_id))
        
        # Coluna de opções (botões)
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
        
        # Colunas de dados
        self.tableWidget.setItem(idx, 2, self.createNotEditableItem(campo_nome))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(lote_nome))
        
        # Coluna de produtos - com quebra de linha automática
        produtos_widget = QtWidgets.QTextEdit()
        produtos_widget.setReadOnly(True)
        produtos_widget.setText(produtos_str)
        produtos_widget.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        
        # Calcular altura dinâmica baseada no número de produtos e comprimento do texto
        # Estimar quantas linhas serão necessárias considerando largura média da tabela
        caracteres_por_linha = 50  # Estimativa de caracteres por linha
        linhas_estimadas = max(1, len(produtos_str) // caracteres_por_linha + 1)
        altura_estimada = max(40, min(150, linhas_estimadas * 20))
        
        produtos_widget.setMinimumHeight(altura_estimada)
        produtos_widget.setMaximumHeight(altura_estimada)
        
        produtos_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        produtos_widget.setStyleSheet("background-color: transparent;")
        self.tableWidget.setCellWidget(idx, 4, produtos_widget)
        
        # Ajustar a altura da linha para acomodar o widget
        self.tableWidget.setRowHeight(idx, altura_estimada + 5)  # 5px extra para margem
        
        # Total de produtos
        self.tableWidget.setItem(idx, 5, self.createNotEditableItemNumber(total_produtos))
        
        # Coluna de dados completos (oculta)
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(dump))

    def handleViewBtn(self, index):
        """
        Manipula o clique no botão de visualização.
        Mostra informações detalhadas do campo e seus produtos.
        
        Args:
            index: Índice da linha na tabela
        """
        # Obtém os dados completos 
        campo = self.tableWidget.model().index(index.row(), 0).data()
        campo_nome = self.tableWidget.model().index(index.row(), 2).data()
        produtos = json.loads(self.tableWidget.model().index(index.row(), 6).data())
        
        if not produtos:
            self.showInfo('Aviso', 'Não há produtos associados a este campo.')
            return
            
        # Mostrar detalhes do campo
        campo_nome = campo_nome
        info = f"Detalhes do Campo: {campo_nome}\n"
        info += f"ID do Campo: {produtos[0]['id']}\n"
        info += f"Lote: {produtos[0]['nome_lote']}\n"
        info += f"\nProdutos Associados ({len(produtos)}):\n"
        
        # Listar todos os produtos
        for i, produto in enumerate(produtos, 1):
            info += f"\n{i}. {produto['produto_nome']}"
            
        # Mostrar em uma caixa de diálogo
        self.showInfo('Detalhes do Campo e Produtos', info)
        
    def handleDeleteBtn(self, index):
        """
        Manipula o clique no botão de exclusão.
        Pergunta se o usuário deseja remover todas as associações do campo.
        
        Args:
            index: Índice da linha na tabela
        """
        campo = self.tableWidget.model().index(index.row(), 0).data()
        campo_nome = self.tableWidget.model().index(index.row(), 2).data()
        
        result = self.showQuestion(
            'Atenção', 
            f'Deseja remover todas as associações do campo "{campo_nome}"?\n\n'
            f'Serão removidos {(self.tableWidget.model().index(index.row(), 5).data())} produtos associados a este campo.'
        )
        
        if not result:
            return
        
        try:
            # Remover todas as associações para este campo
            self.sap.deletaProdutoByCampoId(campo)
            
            self.showInfo('Sucesso', f'Todas as associações do campo "{campo_nome}" foram removidas.')
            self.fetchData()
        except Exception as e:
            self.showError('Erro', f'Erro ao remover associações: {str(e)}')

    def createRowEditWidget(self, parent, row, column, viewFunction, deleteFunction):
        """
        Sobrescreve o método da classe pai para criar um widget apenas com o botão de exclusão
        """
        widget = QtWidgets.QWidget()
        
        # Criando layout horizontal
        horizontalLayout = QtWidgets.QHBoxLayout(widget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        
        # Criando apenas o botão de exclusão
        deleteBtn = QtWidgets.QPushButton(parent)
        deleteBtn.setMaximumSize(QtCore.QSize(30, 30))
        deleteBtn.setText("")
        deleteIcon = QtGui.QIcon()
        deleteIcon.addPixmap(
            QtGui.QPixmap(self.getDeleteIconPath()),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        deleteBtn.setIcon(deleteIcon)
        
        # Adicionando o botão no layout
        horizontalLayout.addWidget(deleteBtn)
        
        # Criando o índice para o botão
        index = QtCore.QPersistentModelIndex(parent.model().index(row, column))
        
        # Configurando o sinal de clique para o botão de exclusão
        deleteBtn.clicked.connect(lambda: deleteFunction(index))
        
        return widget
    
    def getDeleteIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'trash.png'
        )

    def getRowIndex(self, campo_id):
        """
        Encontra o índice da linha para um determinado ID de campo
        """
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    campo_id == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1
    
    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
     # Abre a janela AdicionarProdutoCampo
        self.adicionarProdutoCampoDlg = AdicionarProdutoCampo(self.controller, self.sap, self.qgis)
     # Atualizar tabela após adicionar uma associação
        self.adicionarProdutoCampoDlg.finished.connect(self.fetchData)
        self.adicionarProdutoCampoDlg.show()