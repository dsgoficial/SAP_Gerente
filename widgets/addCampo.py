import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget import DockWidget
from qgis.utils import iface
from qgis import core, gui
from datetime import datetime
from qgis.core import QgsWkbTypes, QgsCoordinateReferenceSystem, QgsGeometry, QgsCoordinateTransform, QgsProject

class AdicionarCampo(DockWidget):

    def __init__(self, sapCtrl, sap, qgis, campo_data=None):
        super(AdicionarCampo, self).__init__(controller=sapCtrl)
        self.sap = sap
        self.qgis = qgis
        self.checkbox_dict = {}  # Dicionário para armazenar os checkboxes
        self.modo_edicao = campo_data is not None
        self.campo_id = campo_data['id'] if self.modo_edicao else None
        
        # Atualiza o título conforme o modo
        if self.modo_edicao:
            self.setWindowTitle('Editar Campo')
        else:
            self.setWindowTitle('Adicionar Campo')
        
        # Garantir que a UI está completamente inicializada antes de manipular
        QtCore.QTimer.singleShot(300, lambda: self.setupUI(campo_data))

    def setupUI(self, campo_data=None):
        # Inicializa os componentes após a UI estar pronta
        self.loadSituacoes()
        self.setupCategoriasUI()
        
        # Se estiver no modo de edição, preenche os campos com os dados existentes
        if self.modo_edicao and campo_data:
            self.preencherCampos(campo_data)
            
            # Muda o texto do botão OK para "Atualizar"
            self.okBtn.setText("Atualizar")

    def preencherCampos(self, campo_data):
        """Preenche os campos do formulário com os dados do campo existente"""
        try:
            # Preenche os campos de texto
            self.nomeLe.setText(campo_data.get('nome', ''))
            self.descricaoTe.setPlainText(campo_data.get('descricao', ''))
            self.orgaoLe.setText(campo_data.get('orgao', ''))
            
            if campo_data.get('pit') is not None:
                self.pitLe.setText(str(campo_data.get('pit')))
                
            self.militaresLe.setText(campo_data.get('militares', ''))
            self.placasVtrLe.setText(campo_data.get('placas_vtr', ''))
            self.dataInicioLe.setText(self.formatar_data(campo_data.get('inicio', '')))
            self.dataFimLe.setText(self.formatar_data(campo_data.get('fim', '')))
            self.geomLe.setText(campo_data.get('geom', ''))
            
            # Seleciona a situação correta no combobox
            situacao_id = campo_data.get('situacao_id')
            if situacao_id:
                for i in range(self.situacaoCb.count()):
                    item_data = self.situacaoCb.itemData(i)
                    if item_data and item_data.get('code') == situacao_id:
                        self.situacaoCb.setCurrentIndex(i)
                        break
            
            # Marca os checkboxes das categorias
            categorias = campo_data.get('categorias', [])
            
            # Verifica se os checkboxes foram criados
            QtCore.QTimer.singleShot(500, lambda: self.marcarCategorias(categorias))
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Aviso', f'Erro ao carregar categorias: {str(e)}')
    
    def marcarCategorias(self, categorias):
        """Marca os checkboxes correspondentes às categorias do campo"""
        if not categorias:
            return
            
        if isinstance(categorias, set):
            categorias = list(categorias)
        
        for categoria in categorias:
            if categoria in self.checkbox_dict:
                self.checkbox_dict[categoria].setChecked(True)
                
    def setupCategoriasUI(self):
        try:
            # Busca categorias da API
            categorias_result = self.sap.getCategorias()
            
            # Processa os dados retornados pela API
            categorias = []
            if categorias_result:
                if isinstance(categorias_result[0], dict) and 'categoria' in categorias_result[0]:
                    # Formato: [{'categoria': 'Nome1'}, {'categoria': 'Nome2'}, ...]
                    categorias = [item['categoria'] for item in categorias_result]
                else:
                    # Outro formato, tenta processar
                    for item in categorias_result:
                        if isinstance(item, dict):
                            # Pega o primeiro valor do dicionário
                            categorias.append(list(item.values())[0])
                        else:
                            # Se for string direta
                            categorias.append(str(item))
            
            # Abordagem alternativa: remover o grupo existente e criar um novo
            old_group = self.findChild(QtWidgets.QGroupBox, 'categoriasGroup')
            if old_group:
                # Encontre o pai do grupo (o layout principal)
                parent_layout = old_group.parent().layout()
                # Encontre o índice do grupo no layout
                index = parent_layout.indexOf(old_group)
                # Remova o grupo existente
                parent_layout.removeWidget(old_group)
                old_group.deleteLater()
                
                # Crie um novo grupo e layout
                new_group = QtWidgets.QGroupBox("Selecione as categorias:")
                new_group.setObjectName("categoriasGroup")
                new_layout = QtWidgets.QVBoxLayout(new_group)
                
                # Adicione os checkboxes
                for categoria_nome in categorias:
                    checkbox = QtWidgets.QCheckBox(categoria_nome)
                    new_layout.addWidget(checkbox)
                    self.checkbox_dict[categoria_nome] = checkbox
                
                # Adicione o novo grupo ao layout principal no mesmo índice
                if index >= 0:
                    parent_layout.insertWidget(index, new_group)
                else:
                    # Se não conseguir determinar o índice, adiciona no final
                    parent_layout.addWidget(new_group)
                    
            else:
                # Se o grupo não existir, tente adicionar ao layout principal
                main_layout = self.findChild(QtWidgets.QVBoxLayout, "verticalLayout")
                if main_layout:
                    # Crie o label e o grupo
                    label = QtWidgets.QLabel("Categorias:")
                    grupo = QtWidgets.QGroupBox("Selecione as categorias:")
                    layout_grupo = QtWidgets.QVBoxLayout(grupo)
                    
                    # Adicione antes da Situação, se possível
                    situacao_label = self.findChild(QtWidgets.QLabel, "labelSituacao")
                    if situacao_label:
                        idx = main_layout.indexOf(situacao_label)
                        main_layout.insertWidget(idx-1 if idx > 0 else 0, label)
                        main_layout.insertWidget(idx, grupo)
                    else:
                        # Se não encontrar, adiciona ao final
                        main_layout.addWidget(label)
                        main_layout.addWidget(grupo)
                    
                    # Adicione os checkboxes
                    for categoria_nome in categorias:
                        checkbox = QtWidgets.QCheckBox(categoria_nome)
                        layout_grupo.addWidget(checkbox)
                        self.checkbox_dict[categoria_nome] = checkbox
            
            # Força atualização da interface
            self.update()
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Aviso', f'Erro ao carregar categorias: {str(e)}')

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "adicionarCampo.ui"
        )

    @QtCore.pyqtSlot(bool)
    def on_extractEWKTBtn_clicked(self):
        layer = iface.activeLayer()
        selectedFeatures = layer.selectedFeatures()
        if len(selectedFeatures) != 1:
            self.showError('Aviso', "Selecione apenas uma feição de campo")
            return

        feat = selectedFeatures[0]
        geom = feat.geometry()

        # Verifica o tipo de geometria e aplica buffer se for ponto ou linha
        if geom.type() == QgsWkbTypes.PointGeometry or geom.type() == QgsWkbTypes.LineGeometry:
            # Obtém o CRS original da camada
            source_crs = layer.crs()

            # Define o CRS Web Mercator (EPSG:3857) para aplicar buffer em metros
            mercator_crs = QgsCoordinateReferenceSystem('EPSG:3857')

            # Cria uma cópia da geometria
            geom_copy = QgsGeometry(geom)

            # Transforma a geometria para Web Mercator
            transform_to_mercator = QgsCoordinateTransform(source_crs, mercator_crs, QgsProject.instance())
            geom_copy.transform(transform_to_mercator)

            # Aplica o buffer de 1 metro no sistema Web Mercator
            geom_buffered = geom_copy.buffer(100, 4)  # 1 metro de buffer, 10 segmentos

            # Transforma de volta para o CRS original
            transform_to_source = QgsCoordinateTransform(mercator_crs, source_crs, QgsProject.instance())
            geom_buffered.transform(transform_to_source)

            # Substitui a geometria original pela geometria com buffer
            geom = geom_buffered

        # Converte para EWKT como antes
        ewkt = self.qgis.geometryToEwkt(geom, layer.crs().authid(), 'EPSG:4326')
        self.geomLe.setText(ewkt)

    @QtCore.pyqtSlot(bool)
    def on_cancelarBtn_clicked(self):
        self.close()        

    def isValidEWKT(self):
        ewkt = self.ewktLe.text()
        if not ewkt:
            return False
        geom = core.QgsGeometry().fromWkt(ewkt.split(';')[1])
        return geom.isGeosValid()
    
    def clearInput(self):
        self.nomeLe.clear()
        self.descricaoTe.clear()
        self.orgaoLe.clear()
        self.pitLe.clear()
        self.militaresLe.clear()
        self.placasVtrLe.clear()
        self.dataInicioLe.clear()
        self.dataFimLe.clear()
        self.geomLe.clear()
        self.situacaoCb.setCurrentIndex(0)  # Reseta para "Previsto"
        
        # Desmarcar todos os checkboxes de categoria
        for checkbox in self.checkbox_dict.values():
            checkbox.setChecked(False)

    def validInput(self):
        # Verifica se os campos obrigatórios estão preenchidos
        if not self.nomeLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'O campo Nome é obrigatório.')
            return False
        
        if not self.orgaoLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'O campo Órgão é obrigatório.')
            return False
        
        if not self.dataInicioLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'O campo Data Início é obrigatório.')
            return False
        
        if not self.dataFimLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'O campo Data Fim é obrigatório.')
            return False
        
        if self.dataFimLe.text() < self.dataInicioLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'A data de fim não pode ser menor que a data de início.')
            return False
        
        # Verifica se pelo menos uma categoria foi selecionada
        if not self.getSelectedCategorias():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Selecione pelo menos uma categoria.')
            return False
        
        self.isValidEWKT()
        
        return True
    
    def loadSituacoes(self):
        situacoes = self.sap.getSituacoes()
        self.situacaoCb.clear()
        if situacoes:  # Check if situacoes is not None and not empty
            for situacao in situacoes:
                if isinstance(situacao, dict) and 'nome' in situacao and 'code' in situacao:
                    self.situacaoCb.addItem(situacao['nome'], situacao)
        else:
            # Add a default option if no situacoes are available
            self.situacaoCb.addItem("Sem situações disponíveis")
    
    def getSelectedCategorias(self):
        # Retorna uma lista das categorias selecionadas nos checkboxes
        selected = []
        for categoria_nome, checkbox in self.checkbox_dict.items():
            if checkbox.isChecked():
                selected.append(categoria_nome)
        return selected
    
    def formatar_data(self, data_iso):
        """Formata a data no formato desejado (DD/MM/YYYY)"""
        try:
            data = datetime.fromisoformat(data_iso)
            return data.strftime("%Y-%m-%d")
        except ValueError:
            return data_iso

    def getCampoData(self):
        pit_value = None
        if self.pitLe.text():
            try:
                pit_value = int(self.pitLe.text())
            except ValueError:
                pass

        # Handle potential None from currentData()
        current_data = self.situacaoCb.currentData()
        situacao_id = None
        if current_data is not None:
            situacao_id = current_data.get('code')

        return {
            'nome': self.nomeLe.text(),
            'descricao': self.descricaoTe.toPlainText(),
            'orgao': self.orgaoLe.text(),
            'pit': pit_value,
            'militares': self.militaresLe.text(),
            'placas_vtr': self.placasVtrLe.text(),
            'inicio': self.dataInicioLe.text(),
            'fim': self.dataFimLe.text(),
            'categorias': self.getSelectedCategorias(),
            'situacao_id': situacao_id,
            'geom': self.geomLe.text()
        }
    
    def runFunction(self):
        if not self.validInput():
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            campo_data = self.getCampoData()

            if self.modo_edicao:
                # Atualiza o campo existente
                resultado = self.sap.atualizaCampo(self.campo_id, campo_data)
                if resultado is not None:
                    QtWidgets.QMessageBox.information(self, 'Sucesso', f'Campo atualizado com sucesso!')
                else:
                    QtWidgets.QMessageBox.warning(self, 'Aviso', 'Campo atualizado, mas não foi retornado um resultado.')
            else:
                # Cria um novo campo
                resultado = self.sap.criaCampo(campo_data)
                if resultado is not None and 'id' in resultado:
                    QtWidgets.QMessageBox.information(self, 'Sucesso', f'Campo criado com sucesso! ID: {resultado["id"]}')
                else:
                    QtWidgets.QMessageBox.information(self, 'Sucesso', 'Campo criado com sucesso!')

            self.clearInput()
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao {"atualizar" if self.modo_edicao else "criar"} campo: {str(e)}')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()