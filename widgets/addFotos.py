import os, sys, base64, datetime
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.widgets.dockWidget import DockWidget
from PIL import Image  # Usando PIL já que está disponível no QGIS
from io import BytesIO  # Parte da biblioteca padrão do Python


class AdicionarFotos(DockWidget):

    def __init__(self, sapCtrl, sap, foto_data=None):
        super(AdicionarFotos, self).__init__(controller=sapCtrl)
        self.sap = sap
        self.foto_data = foto_data  # Armazena os dados da foto para edição
        
        # Define o título baseado no modo (edição ou adição)
        if self.foto_data:
            self.setWindowTitle('Editar Foto')
            self.adicionarBtn.setText('Atualizar')
        else:
            self.setWindowTitle('Adicionar Fotos')
        
        self.fotos = []  # Lista para armazenar as fotos (caminhos)
        
        # Conectar sinais
        self.adicionarFotosBtn.clicked.connect(self.selecionarFotos)
        self.fotosLw.itemClicked.connect(self.exibirPreview)
        self.adicionarBtn.clicked.connect(self.adicionarFotos)
        self.cancelarBtn.clicked.connect(self.close)
        
        # Carregar campos disponíveis
        self.carregarCampos()
        
        # Se estiver em modo de edição, preencher campos com dados existentes
        if self.foto_data:
            self.preencherCamposParaEdicao()
        else:
            # Preencher data atual para novos registros
            now = datetime.datetime.now()
            self.dataImagemLe.setText(now.strftime("%Y-%m-%d %H:%M"))
        
    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            "adicionarFotos.ui"
        )
    
    def preencherCamposParaEdicao(self):
        """
        Preenche os campos com os dados da foto existente para edição
        """
        if not self.foto_data:
            return
            
        # Preenche a descrição
        self.descricaoTe.setPlainText(self.foto_data.get('descricao', ''))
        
        # Preenche a data da imagem (convertendo formato se necessário)
        data_imagem = self.foto_data.get('data_imagem', '')
        if data_imagem:
            try:
                # Tenta converter para o formato de exibição
                data = datetime.datetime.strptime(data_imagem, '%Y-%m-%d %H:%M:%S')
                self.dataImagemLe.setText(data.strftime("%Y-%m-%d %H:%M"))
            except:
                # Se falhar, usa o valor original
                self.dataImagemLe.setText(data_imagem)
        
        # Seleciona o campo correto no ComboBox
        campo_id = self.foto_data.get('campo_id')
        if campo_id is not None:
            index = self.campoCb.findData(campo_id)
            if index >= 0:
                self.campoCb.setCurrentIndex(index)
        
        # Desabilita seleção de novas fotos em modo de edição
        # (Optamos por não permitir alteração da imagem, apenas dos metadados)
        self.adicionarFotosBtn.setEnabled(False)
        self.fotosLw.setVisible(False)
        self.previewLabel.setText("A imagem original será mantida")
    
    def carregarCampos(self):
        """
        Carrega a lista de campos disponíveis no ComboBox
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
    
    def selecionarFotos(self):
        """
        Abre diálogo para selecionar múltiplas fotos
        """
        options = QtWidgets.QFileDialog.Options()
        fileNames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, 
            "Selecionar Fotos",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif)",
            options=options
        )
        
        if fileNames:
            # Adicionar novas fotos à lista
            self.fotosLw.clear()
            self.fotos = fileNames
            
            # Mostrar nomes de arquivos na lista
            for foto in self.fotos:
                item = QtWidgets.QListWidgetItem(os.path.basename(foto))
                self.fotosLw.addItem(item)
            
            # Mostrar preview da primeira foto
            if self.fotos:
                self.exibirPreview(self.fotosLw.item(0))
    
    def exibirPreview(self, item):
        """
        Exibe a pré-visualização da foto selecionada
        """
        if not item:
            return
            
        index = self.fotosLw.row(item)
        if index >= 0 and index < len(self.fotos):
            foto_path = self.fotos[index]
            pixmap = QtGui.QPixmap(foto_path)
            
            # Redimensionar para caber na área de preview mantendo proporção
            pixmap = pixmap.scaled(
                self.previewLabel.width(), 
                self.previewLabel.height(),
                QtCore.Qt.KeepAspectRatio, 
                QtCore.Qt.SmoothTransformation
            )
            
            self.previewLabel.setPixmap(pixmap)
    
    def processarImagem(self, caminho_imagem):
        """
        Processa a imagem para redimensioná-la para no máximo 1000 pixels no lado maior
        e converte para base64 usando PIL
        """
        try:
            # Abrir a imagem com PIL
            img = Image.open(caminho_imagem)
            
            # Obter dimensões originais
            largura, altura = img.size
            
            # Calcular novas dimensões para manter proporção e máximo de 1000px
            if largura > altura and largura > 1000:
                nova_largura = 1000
                nova_altura = int(altura * (1000 / largura))
            elif altura > largura and altura > 1000:
                nova_altura = 1000
                nova_largura = int(largura * (1000 / altura))
            elif largura == altura and largura > 1000:
                nova_largura = 1000
                nova_altura = 1000
            else:
                # A imagem já é menor que 1000px no lado maior
                nova_largura = largura
                nova_altura = altura
            
            # Redimensionar a imagem
            img_redimensionada = img.resize((nova_largura, nova_altura), Image.LANCZOS)
            
            # Determinar o formato baseado na extensão
            nome_arquivo = os.path.basename(caminho_imagem)
            extensao = os.path.splitext(nome_arquivo)[1].lower()
            
            if extensao in ['.jpg', '.jpeg']:
                formato = 'jpeg'
            elif extensao == '.png':
                formato = 'png'
            else:
                # Usar jpg como padrão para outros formatos
                formato = 'jpeg'
            
            # Salvar em buffer de memória
            buffer = BytesIO()
            img_redimensionada.save(buffer, format=formato.upper())
            buffer.seek(0)
            
            # Converter para base64
            img_bytes = buffer.read()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            return {
                'base64': img_base64,
                'formato': formato,
                'largura': nova_largura,
                'altura': nova_altura,
                'nome_arquivo': nome_arquivo
            }
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao processar imagem {os.path.basename(caminho_imagem)}: {str(e)}')
            return None
    
    def validInput(self):
        """
        Valida os inputs antes de enviar
        """
        if self.campoCb.count() == 0:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Não há campos disponíveis para adicionar fotos.')
            return False
            
        # Verifica se tem fotos selecionadas (apenas para modo de adição)
        if not self.foto_data and not self.fotos:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Adicione pelo menos uma foto.')
            return False
            
        if not self.dataImagemLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe a data das imagens.')
            return False
            
        # Verificar formato da data
        try:
            datetime.datetime.strptime(self.dataImagemLe.text(), '%Y-%m-%d %H:%M')
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Formato de data inválido. Use AAAA-MM-DD HH:MM')
            return False
            
        return True
    
    def adicionarFotos(self):
        """
        Processa as fotos e envia para o servidor.
        Se estiver em modo de edição, atualiza os dados da foto.
        """
        if not self.validInput():
            return
        
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            # Obter ID do campo selecionado
            campo_id = self.campoCb.currentData()
            
            # Verificar se estamos em modo de edição
            if self.foto_data:
                # Criar objeto para atualizar no servidor
                foto_obj = {
                    'id': self.foto_data['id'],
                    'descricao': self.descricaoTe.toPlainText(),
                    'data_imagem': self.dataImagemLe.text(),
                    'campo_id': campo_id
                }
                
                # Enviar para o servidor
                resultado = self.sap.atualizaFoto(self.foto_data['id'], foto_obj)
                QtWidgets.QMessageBox.information(self, 'Sucesso', 'Foto atualizada com sucesso!')
                self.close()
            else:
                # Modo de adição - processar todas as imagens
                progresso = QtWidgets.QProgressDialog("Processando imagens...", "Cancelar", 0, len(self.fotos), self)
                progresso.setWindowModality(QtCore.Qt.WindowModal)
                
                fotos_processadas = []
                for i, foto_path in enumerate(self.fotos):
                    progresso.setValue(i)
                    progresso.setLabelText(f"Processando {os.path.basename(foto_path)}...")
                    
                    if progresso.wasCanceled():
                        break
                        
                    # Processar imagem
                    foto_processada = self.processarImagem(foto_path)
                    if foto_processada:
                        # Criar objeto para enviar ao servidor
                        foto_obj = {
                            'descricao': self.descricaoTe.toPlainText(),
                            'data_imagem': self.dataImagemLe.text(),
                            'campo_id': campo_id,
                            'imagem_base64': foto_processada['base64']
                        }
                        fotos_processadas.append(foto_obj)
                
                progresso.setValue(len(self.fotos))
                
                # Enviar para o servidor
                if fotos_processadas:
                    resultado = self.sap.criaFotos({'fotos': fotos_processadas})
                    QtWidgets.QMessageBox.information(self, 'Sucesso', f'{len(fotos_processadas)} foto(s) adicionada(s) com sucesso!')
                    self.clearInput()
                    self.close()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao processar foto: {str(e)}')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
    
    def clearInput(self):
        """
        Limpa os campos de entrada
        """
        self.descricaoTe.clear()
        self.fotos = []
        self.fotosLw.clear()
        self.previewLabel.setText("Pré-visualização")
        self.previewLabel.setPixmap(QtGui.QPixmap())
        
        # Preencher data atual
        now = datetime.datetime.now()
        self.dataImagemLe.setText(now.strftime("%Y-%m-%d %H:%M"))