import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget import DockWidget
import json

class AdicionarProdutoCampo(DockWidget):

    def __init__(self, sapCtrl, sap, qgis):
        super(AdicionarProdutoCampo, self).__init__(controller=sapCtrl)
        self.sap = sap
        self.qgis = qgis
        self.produtos_carregados = []
        self.loteId = None
        self.setWindowTitle('Associar Produtos a Campo')
        
        # Oculta a coluna dump
        self.produtosTable.setColumnHidden(5, True)
        
        # Configuração da tabela de produtos
        self.produtosTable.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.produtosTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        # Conectar sinais
        self.produtosTable.itemSelectionChanged.connect(self.atualizarQuantidadeSelecionada)
        self.carregarProdutosBtn.clicked.connect(self.carregarProdutosPorLote)
        self.filtrarBtn.clicked.connect(self.filtrarProdutos)
        self.filtroLe.returnPressed.connect(self.filtrarProdutos)
        self.cancelBtn.clicked.connect(self.close)
        
        # Carregar dados iniciais
        self.carregarCampos()
        self.carregarLotes()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "adicionarProdutoCampo.ui"
        )
    
    def carregarCampos(self):
        """
        Carrega a lista de campos no ComboBox
        """
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            campos = self.sap.getCampos()
            QtWidgets.QApplication.restoreOverrideCursor()
            
            if not campos:
                QtWidgets.QMessageBox.warning(self, 'Aviso', 'Não há campos cadastrados.')
                return
            
            self.campoCb.clear()
            for campo in campos:
                self.campoCb.addItem(f"{campo['nome']} ({campo['id']})", campo['id'])
                
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao carregar campos: {str(e)}')
    
    def carregarLotes(self):
        """
        Carrega a lista de lotes no ComboBox
        """
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            lotes = self.sap.getLots()
            QtWidgets.QApplication.restoreOverrideCursor()
            
            if not lotes:
                QtWidgets.QMessageBox.warning(self, 'Aviso', 'Não há lotes cadastrados.')
                return
            
            self.loteCb.clear()
            for lote in lotes:
                self.loteCb.addItem(f"{lote['nome']} ({lote['id']})", lote['id'])
                
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao carregar lotes: {str(e)}')
    
    def carregarProdutosPorLote(self):
        """
        Carrega produtos associados ao lote selecionado
        """
        # Obter ID do lote selecionado
        self.loteId = self.loteCb.currentData()
        if not self.loteId:
            QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um lote válido.')
            return
        
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            
            # Buscar produtos do lote selecionado
            produtos = self.sap.getProdutosByLot(self.loteId)
            self.produtos_carregados = produtos
            
            # Exibir produtos na tabela
            self.exibirProdutos(produtos)
            
            QtWidgets.QApplication.restoreOverrideCursor()
            
            if not produtos:
                QtWidgets.QMessageBox.information(self, 'Informação', 'Não foram encontrados produtos para este lote.')
            else:
                # Atualizar informações
                self.infoLabel.setText(f"Foram carregados {len(produtos)} produto(s) do lote selecionado.")
                
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao carregar produtos: {str(e)}')
    
    def exibirProdutos(self, produtos):
        """
        Exibe os produtos na tabela
        """
        self.produtosTable.setRowCount(0)
        
        for produto in produtos:
            row = self.produtosTable.rowCount()
            self.produtosTable.insertRow(row)
            
            # ID
            item = QtWidgets.QTableWidgetItem(str(produto['id']))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.produtosTable.setItem(row, 0, item)
            
            # Nome
            item = QtWidgets.QTableWidgetItem(produto.get('nome', 'N/A'))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.produtosTable.setItem(row, 1, item)
            
            # MI
            item = QtWidgets.QTableWidgetItem(produto.get('mi', 'N/A'))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.produtosTable.setItem(row, 2, item)
            
            # INOM
            item = QtWidgets.QTableWidgetItem(produto.get('inom', 'N/A'))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.produtosTable.setItem(row, 3, item)
            
            # Escala
            escala = produto.get('denominador_escala', 'N/A')
            item = QtWidgets.QTableWidgetItem(f"1:{escala}" if escala and escala != 'N/A' else 'N/A')
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.produtosTable.setItem(row, 4, item)
            
            # Dump (oculto)
            item = QtWidgets.QTableWidgetItem(json.dumps(produto))
            self.produtosTable.setItem(row, 5, item)
        
        # Ajustar colunas
        self.produtosTable.resizeColumnsToContents()
    
    def filtrarProdutos(self):
        """
        Filtra os produtos na tabela pelo texto inserido
        """
        texto_filtro = self.filtroLe.text().lower()
        
        if not texto_filtro:
            # Se não houver filtro, mostrar todos os produtos carregados
            self.exibirProdutos(self.produtos_carregados)
            return
        
        # Filtrar produtos pelos campos nome, MI e INOM
        produtos_filtrados = []
        for produto in self.produtos_carregados:
            if (texto_filtro in str(produto.get('nome', '')).lower() or
                texto_filtro in str(produto.get('mi', '')).lower() or
                texto_filtro in str(produto.get('inom', '')).lower()):
                produtos_filtrados.append(produto)
        
        # Exibir produtos filtrados
        self.exibirProdutos(produtos_filtrados)
        
        # Atualizar informações
        self.infoLabel.setText(f"Encontrado(s) {len(produtos_filtrados)} produto(s) com o filtro '{texto_filtro}'.")
    
    def atualizarQuantidadeSelecionada(self):
        """
        Atualiza a contagem de produtos selecionados
        """
        selecionados = len(self.produtosTable.selectedItems()) // self.produtosTable.columnCount()
        self.quantidadeLabel.setText(f"{selecionados} produto(s) selecionado(s)")
    
    def getProdutosSelecionados(self):
        """
        Retorna a lista de produtos selecionados
        """
        rows = set()
        for item in self.produtosTable.selectedItems():
            rows.add(item.row())
        
        produtos = []
        for row in rows:
            dump_item = self.produtosTable.item(row, 5)
            if dump_item:
                produto = json.loads(dump_item.text())
                produtos.append(produto)
        
        return produtos
    
    def validInput(self):
        """
        Valida os inputs antes de enviar
        """
        # Verificar se há campo selecionado
        if self.campoCb.count() == 0:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Não há campos disponíveis para associação.')
            return False
        
        # Verificar se há produtos selecionados
        produtos = self.getProdutosSelecionados()
        if not produtos:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Selecione pelo menos um produto para associar.')
            return False
        
        return True
    
    def runFunction(self):
        """
        Função principal que é executada quando o usuário clica em Associar
        """
        if not self.validInput():
            return
        
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            
            # Obter ID do campo selecionado
            campo_id = self.campoCb.currentData()
            
            # Obter produtos selecionados
            produtos = self.getProdutosSelecionados()
            
            # Criar lista de associações produto-campo
            associacoes = []
            for produto in produtos:
                associacoes.append({
                    'produto_id': produto['id'],
                    'campo_id': campo_id
                })
            
            # Chamar API para criar as associações
            resultado = self.sap.criaProdutosCampo(associacoes)
            
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.information(
                self, 
                'Sucesso', 
                f'Associações criadas com sucesso! {len(associacoes)} produto(s) associado(s) ao campo.'
            )
            
            self.close()
            
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao criar associações: {str(e)}')