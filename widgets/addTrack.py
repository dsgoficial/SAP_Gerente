import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget import DockWidget
from qgis.utils import iface
from qgis import core, gui
import datetime
from qgis.core import QgsMapLayerProxyModel, QgsWkbTypes
from qgis.gui import QgsMapLayerComboBox

class AdicionarTrack(DockWidget):

    def __init__(self, sapCtrl, sap, qgis, track_data=None):
        super(AdicionarTrack, self).__init__(controller=sapCtrl)
        self.sap = sap
        self.qgis = qgis
        self.track_data = track_data  # Armazena os dados do tracker para edição
        
        # Define o título e texto do botão baseado no modo (edição ou adição)
        if self.track_data:
            self.setWindowTitle('Editar Tracker')
            self.okBtn.setText('Atualizar')
        else:
            self.setWindowTitle('Adicionar Tracker')
        
        # Adiciona a seleção de camada após o carregamento da UI
        self.setupLayerSelector()
        
        # Carregar campos disponíveis
        self.carregarCampos()
        
        # Conexões de sinais
        self.layerCb.layerChanged.connect(self.updateLayerFields)
        
        # Se estiver em modo de edição, preencher campos com dados existentes
        if self.track_data:
            self.preencherCamposParaEdicao()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "adicionarTrack.ui"
        )
    
    def setupLayerSelector(self):
        """
        Configura o seletor de camadas para carregar tracks a partir de uma camada do QGIS
        """
        # Adiciona componentes para seleção de camada após o campo de data
        label5Index = self.verticalLayout.indexOf(self.diaLe) + 1
        
        # Adiciona o label e seletor de camada
        self.layerLabel = QtWidgets.QLabel("Camada de Pontos:")
        self.verticalLayout.insertWidget(label5Index, self.layerLabel)
        
        self.layerCb = QgsMapLayerComboBox()
        self.layerCb.setFilters(QgsMapLayerProxyModel.PointLayer)  # Apenas camadas de pontos
        self.verticalLayout.insertWidget(label5Index + 1, self.layerCb)
        
        # Adiciona os controles para mapeamento de campos
        self.fieldMappingWidget = QtWidgets.QWidget()
        self.fieldMappingLayout = QtWidgets.QVBoxLayout(self.fieldMappingWidget)
        
        # Campos para mapeamento
        self.elevFieldLabel = QtWidgets.QLabel("Campo Elevação (opcional):")
        self.elevFieldCb = QtWidgets.QComboBox()
        self.timeFieldLabel = QtWidgets.QLabel("Campo Data/Hora (opcional):")
        self.timeFieldCb = QtWidgets.QComboBox()
        
        # Novos campos requeridos
        self.trackIdGarminFieldLabel = QtWidgets.QLabel("Campo Track ID Garmin:")
        self.trackIdGarminFieldCb = QtWidgets.QComboBox()
        self.trackSegmentFieldLabel = QtWidgets.QLabel("Campo Track Segment:")
        self.trackSegmentFieldCb = QtWidgets.QComboBox()
        self.trackSegmentPointIndexFieldLabel = QtWidgets.QLabel("Campo Track Segment Point Index:")
        self.trackSegmentPointIndexFieldCb = QtWidgets.QComboBox()
        
        # Adiciona campos ao layout
        self.fieldMappingLayout.addWidget(self.elevFieldLabel)
        self.fieldMappingLayout.addWidget(self.elevFieldCb)
        self.fieldMappingLayout.addWidget(self.timeFieldLabel)
        self.fieldMappingLayout.addWidget(self.timeFieldCb)
        self.fieldMappingLayout.addWidget(self.trackIdGarminFieldLabel)
        self.fieldMappingLayout.addWidget(self.trackIdGarminFieldCb)
        self.fieldMappingLayout.addWidget(self.trackSegmentFieldLabel)
        self.fieldMappingLayout.addWidget(self.trackSegmentFieldCb)
        self.fieldMappingLayout.addWidget(self.trackSegmentPointIndexFieldLabel)
        self.fieldMappingLayout.addWidget(self.trackSegmentPointIndexFieldCb)
        
        # Adiciona o widget de mapeamento ao layout principal
        self.verticalLayout.insertWidget(label5Index + 2, self.fieldMappingWidget)
    
    def updateLayerFields(self, layer):
        """
        Atualiza os comboboxes de campos quando a camada selecionada muda
        """
        if not layer:
            return
            
        self.elevFieldCb.clear()
        self.timeFieldCb.clear()
        self.trackIdGarminFieldCb.clear()
        self.trackSegmentFieldCb.clear()
        self.trackSegmentPointIndexFieldCb.clear()
        
        # Adiciona campos disponíveis nos comboboxes
        field_names = [field.name() for field in layer.fields()]
        
        # Adiciona opção vazia para campos opcionais
        self.elevFieldCb.addItem("")
        self.timeFieldCb.addItem("")
        self.trackIdGarminFieldCb.addItem("")
        self.trackSegmentFieldCb.addItem("")
        self.trackSegmentPointIndexFieldCb.addItem("")
        
        # Preenche comboboxes com campos da camada
        for field_name in field_names:
            self.elevFieldCb.addItem(field_name)
            self.timeFieldCb.addItem(field_name)
            self.trackIdGarminFieldCb.addItem(field_name)
            self.trackSegmentFieldCb.addItem(field_name)
            self.trackSegmentPointIndexFieldCb.addItem(field_name)
        
        # Tenta encontrar campo de elevação
        elev_candidates = ['elev', 'ele', 'z', 'altitude', 'height']
        for candidate in elev_candidates:
            index = self.elevFieldCb.findText(candidate, QtCore.Qt.MatchContains)
            if index >= 0:
                self.elevFieldCb.setCurrentIndex(index)
                break
        
        # Tenta encontrar campo de data/hora
        time_candidates = ['time', 'date', 'datetime', 'data', 'hora', 'creation']
        for candidate in time_candidates:
            index = self.timeFieldCb.findText(candidate, QtCore.Qt.MatchContains)
            if index >= 0:
                self.timeFieldCb.setCurrentIndex(index)
                break
        
        # Tenta encontrar campo de track_id_garmin
        track_id_garmin_candidates = ['track_fid']
        for candidate in track_id_garmin_candidates:
            index = self.trackIdGarminFieldCb.findText(candidate, QtCore.Qt.MatchContains)
            if index >= 0:
                self.trackIdGarminFieldCb.setCurrentIndex(index)
                break
        
        # Tenta encontrar campo de track_segment
        track_segment_candidates = ['track_seg_id']
        for candidate in track_segment_candidates:
            index = self.trackSegmentFieldCb.findText(candidate, QtCore.Qt.MatchContains)
            if index >= 0:
                self.trackSegmentFieldCb.setCurrentIndex(index)
                break
        
        # Tenta encontrar campo de track_segment_point_index
        track_segment_point_index_candidates = ['track_seg_point_id']
        for candidate in track_segment_point_index_candidates:
            index = self.trackSegmentPointIndexFieldCb.findText(candidate, QtCore.Qt.MatchContains)
            if index >= 0:
                self.trackSegmentPointIndexFieldCb.setCurrentIndex(index)
                break
    
    def preencherCamposParaEdicao(self):
        """
        Preenche os campos com os dados do tracker existente para edição
        """
        if not self.track_data:
            return
            
        # Preenche os campos com os dados do tracker
        self.chefeVtrLe.setText(self.track_data.get('chefe_vtr', ''))
        self.motoristaLe.setText(self.track_data.get('motorista', ''))
        self.placaVtrLe.setText(self.track_data.get('placa_vtr', ''))
        self.diaLe.setText(self.track_data.get('dia', ''))
        
        # Seleciona o campo correto no ComboBox
        campo_id = self.track_data.get('campo_id')
        if campo_id is not None:
            index = self.campoCb.findData(campo_id)
            if index >= 0:
                self.campoCb.setCurrentIndex(index)
        
    def carregarCampos(self):
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            campos = self.sap.getCampos()
            QtWidgets.QApplication.restoreOverrideCursor()
            if not campos:
                QtWidgets.QMessageBox.warning(self, 'Aviso', 'Não há campos cadastrados.')
                return
            self.campoCb.clear() # Limpar campos
            for campo in campos:
                self.campoCb.addItem(f"{campo['nome']}", campo['id'])
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao carregar campos: {str(e)}')
    
    def clearInput(self):
        self.chefeVtrLe.clear()
        self.motoristaLe.clear()
        self.placaVtrLe.clear()
        self.diaLe.clear()
        self.campoCb.setCurrentIndex(0)
    
    def validInput(self):
        # Validar campos obrigatórios
        if self.campoCb.count() == 0:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Não há campos disponíveis para adicionar tracks.')
            return False
        if not self.chefeVtrLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe o Chefe da VTR.')
            return False
        if not self.motoristaLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe o Motorista.')
            return False
        if not self.placaVtrLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe a Placa da VTR.')
            return False
        if not self.diaLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe a Data.')
            return False
        try:
            datetime.datetime.strptime(self.diaLe.text(), '%Y-%m-%d')
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Formato de data inválido. Use AAAA-MM-DD')
            return False
            
        # Validar camada para pontos do track (opcional)
        if self.layerCb.currentLayer():
            # Verificar se a camada tem features
            if self.layerCb.currentLayer().featureCount() == 0:
                QtWidgets.QMessageBox.critical(self, 'Erro', 'A camada selecionada não contém features.')
                return False
                
        return True
    
    def getTrackData(self):
        """
        Obtém os dados gerais do tracker
        """
        campo_id = self.campoCb.currentData()
        
        track_data = {
            'chefe_vtr': self.chefeVtrLe.text(),
            'motorista': self.motoristaLe.text(),
            'placa_vtr': self.placaVtrLe.text(),
            'dia': self.diaLe.text(),
            'campo_id': campo_id
        }
        
        # Se estivermos em modo de edição, adicione o ID
        if self.track_data:
            track_data['id'] = self.track_data['id']
            
        return track_data
    
    def extractLayerPoints(self, track_id):
        """
        Extrai pontos da camada selecionada e os prepara para envio
        
        Args:
            track_id: ID do tracker ao qual os pontos serão associados
        """
        layer = self.layerCb.currentLayer()
        if not layer:
            return []
            
        # Obter dados gerais para todos os pontos
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Obter índices de campos
        elev_field_idx = -1
        time_field_idx = -1
        track_id_garmin_field_idx = -1
        track_segment_field_idx = -1
        track_segment_point_index_field_idx = -1
        
        if self.elevFieldCb.currentText():
            elev_field_idx = layer.fields().indexFromName(self.elevFieldCb.currentText())
        
        if self.timeFieldCb.currentText():
            time_field_idx = layer.fields().indexFromName(self.timeFieldCb.currentText())
        
        if self.trackIdGarminFieldCb.currentText():
            track_id_garmin_field_idx = layer.fields().indexFromName(self.trackIdGarminFieldCb.currentText())
        
        if self.trackSegmentFieldCb.currentText():
            track_segment_field_idx = layer.fields().indexFromName(self.trackSegmentFieldCb.currentText())
        
        if self.trackSegmentPointIndexFieldCb.currentText():
            track_segment_point_index_field_idx = layer.fields().indexFromName(self.trackSegmentPointIndexFieldCb.currentText())
        
        # Lista para armazenar os track points
        track_points = []
        
        # Processar cada feature da camada
        counter = 0
        
        # Importar o módulo para gerar UUIDs
        import uuid
        
        for feature in layer.getFeatures():
            # Sempre extrair coordenadas da geometria
            point = feature.geometry().asPoint()
            x = point.x()
            y = point.y()
            
            # Extrair elevação se disponível
            elevation = None
            if elev_field_idx >= 0:
                elevation = feature.attribute(elev_field_idx)
            
            # Extrair data/hora se disponível
            creation_time = now
            if time_field_idx >= 0:
                field_time = feature.attribute(time_field_idx)
                if field_time:
                    # Tenta diferentes formatos de data, dependendo do tipo de dado
                    if isinstance(field_time, datetime.datetime):
                        creation_time = field_time.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(field_time, datetime.date):
                        creation_time = datetime.datetime.combine(
                            field_time, datetime.time()).strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(field_time, str):
                        try:
                            # Tenta interpretar a string como data/hora
                            datetime_obj = datetime.datetime.strptime(field_time, '%Y-%m-%d %H:%M:%S')
                            creation_time = field_time
                        except ValueError:
                            try:
                                # Tenta formato só data
                                datetime_obj = datetime.datetime.strptime(field_time, '%Y-%m-%d')
                                creation_time = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                # Mantém datetime atual
                                pass
            
            # Extrair track_id_garmin se disponível
            track_id_garmin = None
            if track_id_garmin_field_idx >= 0:
                track_id_garmin = feature.attribute(track_id_garmin_field_idx)
            
            # Extrair track_segment se disponível
            track_segment = 1  # valor padrão
            if track_segment_field_idx >= 0:
                field_segment = feature.attribute(track_segment_field_idx)
                if field_segment is not None:
                    track_segment = field_segment
            
            # Extrair track_segment_point_index se disponível
            track_segment_point_index = counter  # valor padrão usando contador
            if track_segment_point_index_field_idx >= 0:
                field_index = feature.attribute(track_segment_point_index_field_idx)
                if field_index is not None:
                    track_segment_point_index = field_index
            
            # Criar dicionário com os dados do ponto
            track_point = {
                'id': str(uuid.uuid4()),  # UUID válido para o banco de dados
                'track_id': track_id,     # ID do tracker principal
                'x_ll': x,
                'y_ll': y,
                'track_id_garmin': track_id_garmin,
                'track_segment': track_segment,
                'track_segment_point_index': track_segment_point_index,
                'elevation': elevation if elevation is not None else 0,
                'creation_time': creation_time
            }
            
            track_points.append(track_point)
            counter += 1
        
        return track_points
    
    def runFunction(self):
        if not self.validInput():
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            # Obter dados do formulário
            track_data = self.getTrackData()
            
            # Verificar se estamos em modo de edição
            if self.track_data:
                # Modo de edição - apenas atualiza as informações gerais do tracker
                if hasattr(self.sap, 'atualizaTracker'):
                    resultado = self.sap.atualizaTracker(track_data['id'], track_data)
                    QtWidgets.QMessageBox.information(self, 'Sucesso', f'Tracker atualizado com sucesso!')
                else:
                    QtWidgets.QMessageBox.warning(self, 'Aviso', 'Função de atualização de tracker não implementada.')
                    return
            else:
                # Modo de adição
                # Primeiro cria o tracker principal
                resultado = self.sap.criaTracker(track_data)
                
                # Se uma camada estiver selecionada, processa os pontos
                if self.layerCb.currentLayer():
                    # Usa o ID do tracker recém-criado para os pontos
                    track_points = self.extractLayerPoints(resultado)
                    
                    if track_points:
                        if hasattr(self.sap, 'criaTrackerPonto'):
                            try:
                                # Envia os pontos para o backend - envia diretamente a lista
                                point_result = self.sap.criaTrackerPonto(track_points)
                                QtWidgets.QMessageBox.information(
                                    self, 
                                    'Sucesso', 
                                    f'Tracker criado com sucesso! {len(track_points)} pontos importados.'
                                )
                            except Exception as e:
                                QtWidgets.QMessageBox.warning(
                                    self,
                                    'Aviso',
                                    f'Tracker criado, mas ocorreu um erro ao importar pontos: {str(e)}'
                                )
                        else:
                            QtWidgets.QMessageBox.information(
                                self,
                                'Sucesso',
                                f'Tracker criado com sucesso! Função de importação de pontos não disponível.'
                            )
                    else:
                        QtWidgets.QMessageBox.information(
                            self,
                            'Sucesso',
                            f'Tracker criado com sucesso! Nenhum ponto extraído da camada.'
                        )
                else:
                    QtWidgets.QMessageBox.information(self, 'Sucesso', f'Tracker criado com sucesso!')
                
            self.clearInput()
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao processar tracker: {str(e)}')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()