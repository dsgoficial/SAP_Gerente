import os, sys, base64, datetime
from PyQt5.QtGui import QPixmap
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
        
        self.caminho_foto = None  # Caminho da foto selecionada
        
        # Conectar sinais
        self.adicionarFotosBtn.clicked.connect(self.selecionarFotos)
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
                data_imagem = data_imagem.replace('Z', '')
                data = datetime.datetime.fromisoformat(data_imagem)
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
        self.previewLabel.setText("A imagem original será mantida")

        # Exibir a imagem original no preview
        self.exibirPreviewBinaria(self.sap.getFotoById(self.foto_data['id'])['imagem_bin']['data'])

        
    
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
                self.campoCb.addItem(f"{campo['nome']}", campo['id'])
                
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao carregar campos: {str(e)}')
    
    def selecionarFotos(self):
        """
        Abre diálogo para selecionar múltiplas fotos
        """
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Selecionar Foto",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif)",
            options=options
        )
        
        if fileName:
            # Adicionar novas fotos à lista
            self.caminho_foto = fileName
            self.exibirPreview(fileName)
    
    def exibirPreview(self, foto_path):
        if not foto_path:
            return
            
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
        if not self.foto_data and not self.caminho_foto:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Adicione uma foto.')
            return False
        
        if not self.dataImagemLe.text():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Informe a data da imagem.')
            return False
            
        if not self.descricaoTe.toPlainText().strip():
            QtWidgets.QMessageBox.critical(self, 'Erro', 'O campo Descrição é obrigatório.')
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
                # Modo de adição
                # Processar imagem
                fotos_processadas = []
                foto_processada = self.processarImagem(self.caminho_foto)
                if foto_processada:
                    # Criar objeto para enviar ao servidor
                    foto_obj = {
                        'descricao': self.descricaoTe.toPlainText(),
                        'data_imagem': self.dataImagemLe.text(),
                        'campo_id': campo_id,
                        'imagem_base64': foto_processada['base64']
                    }
                    fotos_processadas.append(foto_obj)
                    resultado = self.sap.criaFotos({'fotos': fotos_processadas})
                    QtWidgets.QMessageBox.information(self, 'Sucesso', 'Foto adicionada com sucesso!')
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
        self.caminho_foto = None
        self.previewLabel.setText("Pré-visualização")
        self.previewLabel.setPixmap(QtGui.QPixmap())
        
        # Preencher data atual
        now = datetime.datetime.now()
        self.dataImagemLe.setText(now.strftime("%Y-%m-%d %H:%M"))

    def exibirPreviewBinaria(self, imagem_binaria):
        """
        Exibe o preview da imagem binária recebida do backend
        """
        try:
            # Converte o array de bytes em um objeto BytesIO
            imagem_bytes = bytes(imagem_binaria)
            imagem_buffer = BytesIO(imagem_bytes)

            # Abre a imagem com PIL
            img = Image.open(imagem_buffer)

            # Converte para QPixmap
            img = img.convert("RGB")  # Converte para RGB se necessário
            img_qpixmap = self.pilImageToQPixmap(img)
            pixmap_redimensionado = img_qpixmap.scaled(
                self.previewLabel.width(),  # Largura do label de preview
                self.previewLabel.height(),  # Altura do label de preview
                QtCore.Qt.KeepAspectRatio,   # Mantém a proporção da imagem
                QtCore.Qt.SmoothTransformation  # Usa transformação suave
            )

            # Exibe a imagem no label
            self.previewLabel.setPixmap(pixmap_redimensionado)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao exibir o preview da imagem: {str(e)}')

    def pilImageToQPixmap(self, pil_image):
        """
        Converte uma imagem PIL para QPixmap
        """
        img_byte_array = BytesIO()
        pil_image.save(img_byte_array, format="PNG")  # Salva como PNG (você pode escolher o formato que preferir)
        img_byte_array.seek(0)  # Retorna ao início do buffer
        pixmap = QPixmap()
        pixmap.loadFromData(img_byte_array.getvalue())  # Carrega os dados do buffer no QPixmap
        return pixmap