import uuid

from qgis.PyQt import QtCore, QtWidgets
from qgis import core

from SAP_Gerente.modules.sap.wizard import newLotWizardState as wizardState


class NewLotWizard(QtWidgets.QDockWidget):
    """Cadastro guiado de um lote novo, em cinco telas.

    Não abre as ferramentas de gerência: fala direto com a API do SAP e com o
    controller. Assim o wizard SABE o que criou (não precisa pedir ao gerente
    que reencontre o lote numa lista) e não herda o comportamento das telas de
    catálogo, que são feitas para administrar, não para cadastrar.

    Fica ancorado à direita e não é modal porque, na tela de unidades de
    trabalho, o gerente edita os polígonos no canvas antes de gravá-los.
    """

    # As molduras nascem no CRS geodésico da DSG; o SAP guarda a geometria em 4326.
    FRAME_CRS = 'EPSG:4674'

    def __init__(self, controller, qgis, sap, parent=None):
        super(NewLotWizard, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.state = wizardState.NewLotWizardState()
        self.currentPage = wizardState.PAGE_LOT
        self.generatedLayer = None
        self.uuidWarning = ''

        self.setWindowTitle('Novo Lote (guiado)')
        self.setupUi()
        self.loadDomains()
        self.updateUi()
        self.qgis.addDockWidget(self)

    # ---- construção da interface -------------------------------------------

    def setupUi(self):
        root = QtWidgets.QWidget()
        rootLayout = QtWidgets.QVBoxLayout(root)

        self.titleLb = QtWidgets.QLabel()
        self.titleLb.setStyleSheet('font-weight: bold; font-size: 12px;')
        rootLayout.addWidget(self.titleLb)

        self.stepsLb = QtWidgets.QLabel()
        self.stepsLb.setWordWrap(True)
        self.stepsLb.setStyleSheet('color: #555;')
        rootLayout.addWidget(self.stepsLb)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.buildLotPage())
        self.stack.addWidget(self.buildProfilesPage())
        self.stack.addWidget(self.buildProductsPage())
        self.stack.addWidget(self.buildWorkUnitsPage())
        self.stack.addWidget(self.buildActivitiesPage())
        rootLayout.addWidget(self.stack)

        self.messageLb = QtWidgets.QLabel()
        self.messageLb.setWordWrap(True)
        rootLayout.addWidget(self.messageLb)

        navigation = QtWidgets.QHBoxLayout()
        self.backBtn = QtWidgets.QPushButton('< Voltar')
        self.backBtn.clicked.connect(self.onBack)
        navigation.addWidget(self.backBtn)
        self.nextBtn = QtWidgets.QPushButton('Avançar >')
        self.nextBtn.clicked.connect(self.onNext)
        navigation.addWidget(self.nextBtn)
        rootLayout.addLayout(navigation)

        rootLayout.addStretch()

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(root)
        # Só rola quando o conteúdo não cabe; sem isto o QDockWidget mostra a
        # barra o tempo todo, mesmo em tela curta.
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setWidget(self.scroll)

    def adjustStackHeight(self):
        """O QStackedWidget reserva a altura da MAIOR página, o que deixava sobra
        e uma barra de rolagem em telas curtas. Só a página visível dita a altura."""
        for index in range(self.stack.count()):
            page = self.stack.widget(index)
            policy = page.sizePolicy()
            policy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Ignored)
            page.setSizePolicy(policy)
        current = self.stack.currentWidget()
        if current:
            policy = current.sizePolicy()
            policy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Preferred)
            current.setSizePolicy(policy)
            current.adjustSize()
        self.stack.adjustSize()

    def buildLotPage(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.projectCb = QtWidgets.QComboBox()
        form.addRow('Projeto', self.projectCb)
        self.productionLineCb = QtWidgets.QComboBox()
        form.addRow('Linha de produção', self.productionLineCb)
        self.lotNameLe = QtWidgets.QLineEdit()
        form.addRow('Nome do lote', self.lotNameLe)
        self.lotAliasLe = QtWidgets.QLineEdit()
        form.addRow('Abreviação', self.lotAliasLe)
        self.lotDescriptionLe = QtWidgets.QLineEdit()
        form.addRow('Descrição', self.lotDescriptionLe)
        self.lotScaleLe = QtWidgets.QLineEdit()
        self.lotScaleLe.setPlaceholderText('ex.: 50000')
        form.addRow('Escala 1:', self.lotScaleLe)

        form.addRow(self.separator('Banco de edição (dado de produção)'))
        self.useExistingDbRb = QtWidgets.QRadioButton('Usar conexão já cadastrada')
        self.useExistingDbRb.setChecked(True)
        self.useExistingDbRb.toggled.connect(self.updateDbFields)
        form.addRow(self.useExistingDbRb)
        self.productionDataCb = QtWidgets.QComboBox()
        form.addRow('Conexão', self.productionDataCb)
        self.createDbRb = QtWidgets.QRadioButton('Cadastrar nova conexão')
        form.addRow(self.createDbRb)
        self.dbHostLe = QtWidgets.QLineEdit()
        form.addRow('Endereço', self.dbHostLe)
        self.dbPortLe = QtWidgets.QLineEdit('5432')
        form.addRow('Porta', self.dbPortLe)
        self.dbNameLe = QtWidgets.QLineEdit()
        form.addRow('Nome do banco', self.dbNameLe)
        self.dbTypeCb = QtWidgets.QComboBox()
        form.addRow('Tipo', self.dbTypeCb)

        form.addRow(self.separator('Bloco'))
        self.blockNameLe = QtWidgets.QLineEdit('Bloco 1')
        form.addRow('Nome do bloco', self.blockNameLe)
        self.blockPriorityLe = QtWidgets.QLineEdit('1')
        form.addRow('Prioridade', self.blockPriorityLe)

        self.createLotBtn = QtWidgets.QPushButton('Criar lote, conexão e bloco')
        self.createLotBtn.clicked.connect(self.onCreateLot)
        form.addRow(self.createLotBtn)
        return page

    def buildProfilesPage(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.modelLotCb = QtWidgets.QComboBox()
        form.addRow('Copiar perfis do lote', self.modelLotCb)
        self.noModelLb = QtWidgets.QLabel(
            'Não há outro lote nesta linha de produção. Este é o primeiro: os perfis (estilos, '
            'menus, regras) terão de ser configurados nos gerenciadores, depois.')
        self.noModelLb.setWordWrap(True)
        self.noModelLb.setStyleSheet('color: #a60;')
        form.addRow(self.noModelLb)

        self.cqCb = QtWidgets.QComboBox()
        form.addRow('Controle de qualidade', self.cqCb)

        self.applyProfilesBtn = QtWidgets.QPushButton('Aplicar perfis e criar etapas')
        self.applyProfilesBtn.clicked.connect(self.onApplyProfiles)
        form.addRow(self.applyProfilesBtn)
        return page

    def buildProductsPage(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.fromMiRb = QtWidgets.QRadioButton('Informar a lista de MI')
        self.fromMiRb.setChecked(True)
        self.fromMiRb.toggled.connect(self.updateProductSource)
        form.addRow(self.fromMiRb)
        self.fromLayerRb = QtWidgets.QRadioButton('Usar uma camada de molduras')
        form.addRow(self.fromLayerRb)

        # --- por lista de MI: a escala vem primeiro, porque ela define a moldura
        self.miScaleLb = QtWidgets.QLabel('Escala das folhas')
        self.miScaleCb = QtWidgets.QComboBox()
        for label, denominator, scaleIndex in wizardState.SCALE_OPTIONS:
            self.miScaleCb.addItem(label, (denominator, scaleIndex))
        form.addRow(self.miScaleLb, self.miScaleCb)

        self.miListLb = QtWidgets.QLabel('MI (separados por vírgula)')
        self.miListTe = QtWidgets.QPlainTextEdit()
        self.miListTe.setPlaceholderText('ex.: 2965-1, 2965-2, 2966-3')
        self.miListTe.setMaximumHeight(70)
        form.addRow(self.miListLb, self.miListTe)

        # --- por camada de molduras
        self.productLayerLb = QtWidgets.QLabel('Camada de molduras')
        self.productLayerCb = self.controller.getQgisComboBoxPolygonLayer()
        self.productLayerCb.layerChanged.connect(self.onProductLayerChanged)
        form.addRow(self.productLayerLb, self.productLayerCb)

        self.productFieldCbs = {}
        self.productFieldLbs = {}
        for fieldName in wizardState.PRODUCT_FIELDS:
            combo = QtWidgets.QComboBox()
            label = QtWidgets.QLabel(fieldName)
            self.productFieldCbs[fieldName] = combo
            self.productFieldLbs[fieldName] = label
            form.addRow(label, combo)

        self.productOnlySelectedCkb = QtWidgets.QCheckBox('Apenas feições selecionadas')
        form.addRow(self.productOnlySelectedCkb)

        self.loadProductsBtn = QtWidgets.QPushButton('Carregar produtos')
        self.loadProductsBtn.clicked.connect(self.onLoadProducts)
        form.addRow(self.loadProductsBtn)
        return page

    def updateProductSource(self):
        byMi = self.fromMiRb.isChecked()
        for widget in (self.miScaleLb, self.miScaleCb, self.miListLb, self.miListTe):
            widget.setVisible(byMi)
        for widget in (self.productLayerLb, self.productLayerCb, self.productOnlySelectedCkb):
            widget.setVisible(not byMi)
        for fieldName in wizardState.PRODUCT_FIELDS:
            self.productFieldCbs[fieldName].setVisible(not byMi)
            self.productFieldLbs[fieldName].setVisible(not byMi)

    def buildWorkUnitsPage(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.utSourceLayerCb = self.controller.getQgisComboBoxPolygonLayer()
        form.addRow('Camada de origem', self.utSourceLayerCb)
        self.utProjectionCb = self.controller.getQgisComboBoxProjection()
        form.addRow('Projeção de trabalho', self.utProjectionCb)
        self.utSplitCb = QtWidgets.QComboBox()
        for label, value in [('1/1', 0), ('1/4', 1), ('1/9', 2), ('1/16', 3), ('1/25', 4)]:
            self.utSplitCb.addItem(label, value)
        form.addRow('Divisão da moldura', self.utSplitCb)
        self.utOverlapLe = QtWidgets.QLineEdit('0.0')
        form.addRow('Sobreposição', self.utOverlapLe)
        self.utOnlySelectedCkb = QtWidgets.QCheckBox('Apenas feições selecionadas')
        form.addRow(self.utOnlySelectedCkb)

        self.generateUtBtn = QtWidgets.QPushButton('1. Gerar unidades de trabalho')
        self.generateUtBtn.clicked.connect(self.onGenerateWorkUnits)
        form.addRow(self.generateUtBtn)

        editHint = QtWidgets.QLabel(
            '2. Edite os polígonos no canvas, se precisar. Nada foi gravado no SAP ainda.')
        editHint.setWordWrap(True)
        editHint.setStyleSheet('color: #06c;')
        form.addRow(editHint)

        self.utLayerCb = self.controller.getQgisComboBoxPolygonLayer()
        form.addRow('Camada de UT gerada', self.utLayerCb)

        self.subphaseList = QtWidgets.QListWidget()
        self.subphaseList.setMaximumHeight(120)
        form.addRow('Subfases', self.subphaseList)

        self.loadUtBtn = QtWidgets.QPushButton('3. Carregar unidades de trabalho no SAP')
        self.loadUtBtn.clicked.connect(self.onLoadWorkUnits)
        form.addRow(self.loadUtBtn)
        return page

    def buildActivitiesPage(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.revisionCkb = QtWidgets.QCheckBox('Criar atividades de Revisão')
        self.revisionCorrectionCkb = QtWidgets.QCheckBox('Criar atividades de Revisão/Correção')
        self.revisionFinalCkb = QtWidgets.QCheckBox('Criar atividades de Revisão Final')
        form.addRow(self.revisionCkb)
        form.addRow(self.revisionCorrectionCkb)
        form.addRow(self.revisionFinalCkb)

        self.createActivitiesBtn = QtWidgets.QPushButton('Criar atividades do lote')
        self.createActivitiesBtn.clicked.connect(self.onCreateActivities)
        form.addRow(self.createActivitiesBtn)

        self.summaryLb = QtWidgets.QLabel()
        self.summaryLb.setWordWrap(True)
        form.addRow(self.summaryLb)
        return page

    def separator(self, text):
        label = QtWidgets.QLabel(text)
        label.setStyleSheet('font-weight: bold; margin-top: 8px;')
        return label

    # ---- carga dos domínios -------------------------------------------------

    def loadDomains(self):
        try:
            for project in self.sap.getProjects():
                if project.get('status_id') == wizardState.STATUS_EM_EXECUCAO:
                    self.projectCb.addItem(project['nome'], project['id'])
            for line in self.sap.getActiveProductionLines():
                self.productionLineCb.addItem(line['linha_producao'], line['linha_producao_id'])
            for dataType in self.sap.getProductionDataType():
                self.dbTypeCb.addItem(dataType['nome'], dataType['code'])
            # O banco de edição da produção é PostGIS com controle de permissões.
            defaultType = self.dbTypeCb.findData(wizardState.TIPO_DADO_PRODUCAO_PADRAO)
            if defaultType >= 0:
                self.dbTypeCb.setCurrentIndex(defaultType)
            self.reloadProductionData()
        except Exception as e:
            self.showMessage('Não foi possível carregar as listas do SAP: {0}'.format(e), True)

        for code in (wizardState.CQ_REVISAO_CORRECAO, wizardState.CQ_SEM_REVISAO, wizardState.CQ_REVISAO):
            self.cqCb.addItem(wizardState.CQ_NAMES[code], code)
        self.cqCb.setCurrentIndex(0)  # o sugerido vem primeiro e já marcado
        self.updateDbFields()
        self.updateProductSource()

    def reloadProductionData(self):
        self.productionDataCb.clear()
        for data in self.sap.getProductionData():
            self.productionDataCb.addItem(data['configuracao_producao'], data['id'])

    def updateDbFields(self):
        useExisting = self.useExistingDbRb.isChecked()
        self.productionDataCb.setEnabled(useExisting)
        for widget in (self.dbHostLe, self.dbPortLe, self.dbNameLe, self.dbTypeCb):
            widget.setEnabled(not useExisting)

    # ---- mensagens e navegação ---------------------------------------------

    def showMessage(self, text, isError=False):
        self.messageLb.setStyleSheet('color: {0};'.format('#a00' if isError else '#060'))
        self.messageLb.setText(text)

    def updateUi(self):
        page = self.currentPage
        self.titleLb.setText('Tela {0} de {1}: {2}'.format(
            wizardState.ALL_PAGES.index(page) + 1, len(wizardState.ALL_PAGES),
            wizardState.PAGE_NAMES[page]))
        self.stepsLb.setText(' > '.join(
            ('[x] ' if self.state.isPageDone(p) else '[ ] ') + wizardState.PAGE_NAMES[p]
            for p in wizardState.ALL_PAGES))
        self.stack.setCurrentIndex(wizardState.ALL_PAGES.index(page))
        self.adjustStackHeight()

        self.backBtn.setEnabled(page != wizardState.PAGE_LOT)
        nextPage = self.nextPageAfter(page)
        self.nextBtn.setEnabled(nextPage is not None and self.state.canEnterPage(nextPage))

        if page == wizardState.PAGE_PROFILES:
            self.refreshModelLots()
        if page == wizardState.PAGE_PRODUCTS:
            self.preselectLotScale()
        if page == wizardState.PAGE_WORK_UNITS:
            self.refreshSubphases()

    def preselectLotScale(self):
        """A escala do produto tem de bater com a do lote (trigger chk_scale)."""
        if self.state.lotScale is None:
            return
        for index in range(self.miScaleCb.count()):
            denominator, _ = self.miScaleCb.itemData(index)
            if denominator == self.state.lotScale:
                self.miScaleCb.setCurrentIndex(index)
                return

    def nextPageAfter(self, page):
        index = wizardState.ALL_PAGES.index(page)
        if index + 1 >= len(wizardState.ALL_PAGES):
            return None
        return wizardState.ALL_PAGES[index + 1]

    def goToNextPage(self, keepMessage=True):
        """Avança sozinho quando a ação da tela conclui, sem exigir 'Avançar'."""
        nextPage = self.nextPageAfter(self.currentPage)
        if nextPage is None or not self.state.canEnterPage(nextPage):
            self.updateUi()
            return
        message = self.messageLb.text() if keepMessage else ''
        isError = 'a00' in self.messageLb.styleSheet()
        self.currentPage = nextPage
        self.updateUi()
        if message:
            self.showMessage(message, isError)

    def onNext(self):
        nextPage = self.nextPageAfter(self.currentPage)
        if nextPage is None:
            return
        missing = self.state.missingRequirements(nextPage)
        if missing:
            self.showMessage('Antes de avançar, falta: ' + '; '.join(missing) + '.', True)
            return
        self.currentPage = nextPage
        self.messageLb.setText('')
        self.updateUi()

    def onBack(self):
        index = wizardState.ALL_PAGES.index(self.currentPage)
        if index == 0:
            return
        self.currentPage = wizardState.ALL_PAGES[index - 1]
        self.messageLb.setText('')
        self.updateUi()

    # ---- tela 1: lote, conexão e bloco -------------------------------------

    def onCreateLot(self):
        if self.state.lotId:
            self.showMessage('O lote "{0}" já foi criado nesta sessão.'.format(self.state.lotName), True)
            return
        projectId = self.projectCb.currentData()
        productionLineId = self.productionLineCb.currentData()
        errors = wizardState.validateLotForm(
            self.lotNameLe.text(), self.lotAliasLe.text(), self.lotDescriptionLe.text(),
            self.lotScaleLe.text(), projectId, productionLineId)
        errors += wizardState.validateBlockForm(self.blockNameLe.text(), self.blockPriorityLe.text())
        if self.createDbRb.isChecked():
            errors += wizardState.validateProductionDataForm(
                self.dbHostLe.text(), self.dbPortLe.text(), self.dbNameLe.text())
        elif not self.productionDataCb.currentData():
            errors.append('Escolha a conexão do banco de edição.')
        if errors:
            self.showMessage(' '.join(errors), True)
            return

        try:
            productionDataId = self.resolveProductionData()
            if productionDataId is None:
                return
            lotName = self.lotNameLe.text().strip()
            self.sap.createLots([{
                'nome': lotName,
                'nome_abrev': self.lotAliasLe.text().strip(),
                'descricao': self.lotDescriptionLe.text().strip(),
                'denominador_escala': wizardState.parseInt(self.lotScaleLe.text(), minimum=1),
                'projeto_id': projectId,
                'linha_producao_id': productionLineId,
                'status_id': wizardState.STATUS_EM_EXECUCAO
            }])
            lot = wizardState.findByName(self.sap.getAllLots(), lotName)
            if not lot:
                self.showMessage('O lote foi enviado mas não apareceu na relista. Confira o login e o servidor.', True)
                return
            blockName = self.blockNameLe.text().strip()
            self.sap.createBlocks([{
                'nome': blockName,
                'prioridade': wizardState.parseInt(self.blockPriorityLe.text()),
                'lote_id': lot['id'],
                'status_id': wizardState.STATUS_EM_EXECUCAO
            }])
            blocks = [b for b in self.sap.getAllBlocks() if b.get('lote_id') == lot['id']]
            block = wizardState.findByName(blocks, blockName)
            if not block:
                self.showMessage('O bloco foi enviado mas não apareceu na relista.', True)
                return

            self.state.lotId = lot['id']
            self.state.lotName = lot['nome']
            self.state.lotScale = lot['denominador_escala']
            self.state.productionLineId = lot['linha_producao_id']
            self.state.productionDataId = productionDataId
            self.state.blockId = block['id']
        except Exception as e:
            self.showMessage('Falha ao criar: {0}'.format(e), True)
            return

        self.createLotBtn.setEnabled(False)
        self.showMessage('Lote "{0}" e bloco "{1}" criados.'.format(self.state.lotName, block['nome']))
        self.goToNextPage()

    def resolveProductionData(self):
        """Devolve o id da conexão, criando-a se o gerente pediu."""
        if self.useExistingDbRb.isChecked():
            return self.productionDataCb.currentData()
        configuration = '{0}:{1}/{2}'.format(
            self.dbHostLe.text().strip(), self.dbPortLe.text().strip(), self.dbNameLe.text().strip())
        self.sap.createProductionData([{
            'configuracao_producao': configuration,
            'tipo_dado_producao_id': self.dbTypeCb.currentData()
        }])
        self.reloadProductionData()
        created = wizardState.findByName(
            self.sap.getProductionData(), configuration, key='configuracao_producao')
        if not created:
            self.showMessage('A conexão foi enviada mas não apareceu na relista.', True)
            return None
        return created['id']

    # ---- tela 2: perfis e etapas -------------------------------------------

    def refreshModelLots(self):
        self.modelLotCb.clear()
        try:
            candidates = wizardState.modelLotCandidates(
                self.sap.getAllLots(), self.state.productionLineId, self.state.lotId)
        except Exception as e:
            self.showMessage('Não foi possível listar os lotes-modelo: {0}'.format(e), True)
            candidates = []
        for lot in candidates:
            self.modelLotCb.addItem(lot['nome'], lot['id'])
        hasCandidates = bool(candidates)
        self.modelLotCb.setVisible(hasCandidates)
        self.noModelLb.setVisible(not hasCandidates)

    def onApplyProfiles(self):
        modelLotId = self.modelLotCb.currentData()
        cq = self.cqCb.currentData()
        try:
            if modelLotId:
                self.sap.copySetupLot(self.copyPayload(modelLotId, self.state.lotId))
                self.state.profilesApplied = True
            else:
                self.state.profilesSkipped = True

            phases = [p for p in self.sap.getPhases()
                      if p.get('linha_producao_id') == self.state.productionLineId]
            if not phases:
                self.showMessage('A linha de produção não tem fases cadastradas.', True)
                return
            for phase in phases:
                self.controller.createDefaultStep(cq, phase['fase_id'], self.state.lotId)
        except Exception as e:
            self.showMessage('Falha ao aplicar: {0}'.format(e), True)
            return

        self.applyProfilesBtn.setEnabled(False)
        copied = 'perfis copiados' if modelLotId else 'sem lote-modelo, perfis não copiados'
        self.showMessage('{0}; etapas criadas em {1} fase(s) com "{2}".'.format(
            copied, len(phases), wizardState.CQ_NAMES[cq]))
        self.goToNextPage()

    def copyPayload(self, sourceLotId, targetLotId):
        payload = {'lote_id_origem': sourceLotId, 'lote_id_destino': targetLotId}
        for flag in ('copiar_estilo', 'copiar_menu', 'copiar_regra', 'copiar_modelo',
                     'copiar_workflow', 'copiar_alias', 'copiar_linhagem', 'copiar_finalizacao',
                     'copiar_tema', 'copiar_fme', 'copiar_configuracao_qgis', 'copiar_monitoramento'):
            payload[flag] = True
        return payload

    # ---- tela 3: produtos ---------------------------------------------------

    def onProductLayerChanged(self):
        layer = self.productLayerCb.currentLayer()
        fieldNames = [field.name() for field in layer.fields()] if layer else []
        mapping = wizardState.autoMapFields(fieldNames, wizardState.PRODUCT_FIELDS)
        for wanted, combo in self.productFieldCbs.items():
            combo.clear()
            combo.addItem('...', '')
            for fieldName in fieldNames:
                combo.addItem(fieldName, fieldName)
            if mapping.get(wanted):
                combo.setCurrentIndex(combo.findData(mapping[wanted]))

    def onLoadProducts(self):
        if self.fromMiRb.isChecked():
            done = self.loadProductsFromMiList()
        else:
            done = self.loadProductsFromLayer()
        if not done:
            return
        try:
            products = self.sap.getProductsByLot(self.state.lotId)
        except Exception as e:
            self.showMessage('Produtos enviados, mas não foi possível conferir: {0}'.format(e), True)
            return
        if not products:
            self.showMessage('Nenhum produto apareceu no lote. Confira o login e os dados.', True)
            return
        self.state.productsLoaded = len(products)
        self.loadProductsBtn.setEnabled(False)
        self.showMessage('{0} produto(s) no lote.{1}'.format(len(products), self.uuidWarning))
        self.goToNextPage()

    def loadProductsFromLayer(self):
        layer = self.productLayerCb.currentLayer()
        if not layer:
            self.showMessage('Escolha a camada de molduras.', True)
            return False
        associatedFields = {name: combo.currentData() or '' for name, combo in self.productFieldCbs.items()}
        if not associatedFields['uuid']:
            self.showMessage('Associe o campo do uuid: ele é único no SAP e vem da planilha de produção.', True)
            return False
        uuidField = associatedFields['uuid']
        missing = wizardState.missingUuidCount([{'uuid': f[uuidField]} for f in layer.getFeatures()])
        if missing:
            self.showMessage('{0} feição(ões) sem uuid. Preencha antes de carregar.'.format(missing), True)
            return False
        try:
            self.controller.createSapProducts(
                layer, self.state.lotId, associatedFields, self.productOnlySelectedCkb.isChecked())
        except Exception as e:
            self.showMessage('Falha ao carregar produtos: {0}'.format(e), True)
            return False
        self.uuidWarning = ''
        return True

    def loadProductsFromMiList(self):
        """Gera as molduras das folhas pelo MI e cria os produtos.

        O uuid do produto é canônico e vem da planilha de produção. Aqui não há
        planilha, então é gerado um uuid provisório e o gerente é avisado.
        """
        errors = wizardState.validateMiList(self.miListTe.toPlainText())
        if errors:
            self.showMessage(' '.join(errors), True)
            return False
        miList, _ = wizardState.parseMiList(self.miListTe.toPlainText())
        denominator, scaleIndex = self.miScaleCb.currentData()
        if self.state.lotScale is not None and denominator != self.state.lotScale:
            self.showMessage(
                'A escala das folhas (1:{0}) tem de ser a mesma do lote (1:{1}). O SAP recusa '
                'produto com escala diferente da do lote.'.format(denominator, self.state.lotScale), True)
            return False
        try:
            frames = self.controller.generateFramesFromIndex({
                'scaleIndex': scaleIndex,
                'index': ','.join(miList),
                'crs': self.FRAME_CRS
            })
        except Exception as e:
            self.showMessage('Não foi possível gerar as molduras: {0}'.format(e), True)
            return False

        products = []
        for feature in frames.getFeatures():
            geometry = core.QgsGeometry(feature.geometry())
            # O SAP recusa POLYGON no produto; o gridzonegenerator devolve POLYGON.
            geometry.convertToMultiType()
            products.append({
                'uuid': str(uuid.uuid4()),
                'nome': feature['mi'],
                'mi': feature['mi'],
                'inom': feature['inom'],
                'denominador_escala': str(denominator),
                'edicao': '1',
                'geom': self.qgis.geometryToEwkt(geometry, self.FRAME_CRS, 'EPSG:4326')
            })
        if not products:
            self.showMessage('Nenhuma moldura foi gerada. Confira os MI e a escala.', True)
            return False
        faltando = [mi for mi in miList if mi not in [p['mi'] for p in products]]
        if faltando:
            self.showMessage('Não foi possível gerar a moldura de: {0}.'.format(', '.join(faltando)), True)
            return False
        try:
            self.sap.createProducts(self.state.lotId, products)
        except Exception as e:
            self.showMessage('Falha ao criar os produtos: {0}'.format(e), True)
            return False
        self.uuidWarning = (' Atenção: o uuid foi gerado automaticamente, pois não veio da planilha '
                            'de produção. Reconcilie depois, se for o caso.')
        return True

    # ---- tela 4: unidades de trabalho --------------------------------------

    def refreshSubphases(self):
        if self.subphaseList.count():
            return
        try:
            subphases = [s for s in self.sap.getSubphases()
                         if s.get('linha_producao_id') == self.state.productionLineId]
        except Exception as e:
            self.showMessage('Não foi possível listar as subfases: {0}'.format(e), True)
            return
        seen = set()
        for subphase in subphases:
            subphaseId = subphase['subfase_id']
            if subphaseId in seen:
                continue
            seen.add(subphaseId)
            item = QtWidgets.QListWidgetItem(subphase['subfase'])
            item.setData(QtCore.Qt.ItemDataRole.UserRole, subphaseId)
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.subphaseList.addItem(item)

    def checkedSubphaseIds(self):
        ids = []
        for row in range(self.subphaseList.count()):
            item = self.subphaseList.item(row)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                ids.append(item.data(QtCore.Qt.ItemDataRole.UserRole))
        return ids

    def onGenerateWorkUnits(self):
        layer = self.utSourceLayerCb.currentLayer()
        if not layer:
            self.showMessage('Escolha a camada de origem.', True)
            return
        crs = self.utProjectionCb.crs()
        if not crs or not crs.authid():
            self.showMessage('Escolha a projeção de trabalho (o fuso UTM).', True)
            return
        overlap = self.utOverlapLe.text().strip().replace(',', '.')
        try:
            overlapValue = float(overlap)
        except ValueError:
            self.showMessage('A sobreposição deve ser um número (ex.: 0.0).', True)
            return
        try:
            self.controller.createWorkUnitSimple({
                'layerId': layer.id(),
                'layer': layer,
                'overlap': overlapValue,
                'epsg': crs.authid().split(':')[-1],
                'bloco_id': self.state.blockId,
                'dado_producao_id': self.state.productionDataId,
                'param': self.utSplitCb.currentData(),
                'onlySelected': self.utOnlySelectedCkb.isChecked()
            })
        except Exception as e:
            self.showMessage('Falha ao gerar as unidades de trabalho: {0}'.format(e), True)
            return
        self.showMessage('Unidades de trabalho geradas no QGIS. Edite os polígonos se precisar; '
                         'nada foi gravado no SAP ainda. Depois escolha a camada e carregue.')

    def geometryNameOf(self, layer):
        """Nome da geometria olhando as feições, como o resto do plugin faz."""
        for feature in layer.getFeatures():
            wkbType = feature.geometry().wkbType()
            if wkbType != core.QgsWkbTypes.Polygon:
                return core.QgsWkbTypes.displayString(wkbType)
        return 'Polygon'

    def onLoadWorkUnits(self):
        layer = self.utLayerCb.currentLayer()
        if not layer:
            self.showMessage('Escolha a camada de unidades de trabalho gerada.', True)
            return
        subphaseIds = self.checkedSubphaseIds()
        if not subphaseIds:
            self.showMessage('Marque ao menos uma subfase.', True)
            return
        errors = wizardState.validateWorkUnitLayer(
            layer.featureCount(), self.geometryNameOf(layer), layer.crs().authid())
        if errors:
            self.showMessage(' '.join(errors), True)
            return
        if not self.confirmWorkUnitLoad(subphaseIds):
            return

        fieldNames = [field.name() for field in layer.fields()]
        associatedFields = wizardState.autoMapFields(fieldNames, wizardState.WORK_UNIT_FIELDS)
        missingFields = [name for name, mapped in associatedFields.items() if not mapped]
        if missingFields:
            self.showMessage(
                'A camada não tem os campos {0}. Gere as unidades de trabalho pelo passo 1 desta tela.'.format(
                    ', '.join(missingFields)), True)
            return
        try:
            self.controller.loadSapWorkUnits(
                layer, self.state.lotId, subphaseIds, False, associatedFields)
            workUnits = self.sap.getWorkUnitsByLot(self.state.lotId)
        except Exception as e:
            self.showMessage('Falha ao carregar as unidades de trabalho: {0}'.format(e), True)
            return
        if not workUnits:
            self.showMessage('Nenhuma unidade de trabalho apareceu no lote. Confira o login.', True)
            return
        self.state.workUnitsLoaded = len(workUnits)
        self.loadUtBtn.setEnabled(False)
        self.showMessage('{0} unidade(s) de trabalho no lote.'.format(len(workUnits)))
        self.goToNextPage()

    def confirmWorkUnitLoad(self, subphaseIds):
        """Carregar duas vezes duplica em silêncio: a tabela não tem UNIQUE."""
        try:
            workUnits = self.sap.getWorkUnitsByLot(self.state.lotId)
        except Exception as e:
            self.showMessage('Não foi possível conferir as UTs existentes: {0}'.format(e), True)
            return False
        counts = wizardState.existingWorkUnitsBySubphase(workUnits, subphaseIds)
        if not counts:
            return True
        detail = ', '.join('subfase {0}: {1} UT'.format(k, v) for k, v in sorted(counts.items()))
        answer = QtWidgets.QMessageBox.question(
            self, 'Atenção',
            'Este lote JÁ tem unidades de trabalho nas subfases escolhidas ({0}).\n\n'
            'Carregar de novo vai DUPLICAR as unidades, sem dar erro.\n\nContinuar mesmo assim?'.format(detail),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No)
        return answer == QtWidgets.QMessageBox.StandardButton.Yes

    # ---- tela 5: atividades -------------------------------------------------

    def onCreateActivities(self):
        try:
            self.sap.createAllActivities({
                'lote_id': self.state.lotId,
                'atividades_revisao': self.revisionCkb.isChecked(),
                'atividades_revisao_correcao': self.revisionCorrectionCkb.isChecked(),
                'atividades_revisao_final': self.revisionFinalCkb.isChecked()
            })
        except Exception as e:
            self.showMessage('Falha ao criar as atividades: {0}'.format(e), True)
            return
        self.state.activitiesCreated = True
        self.createActivitiesBtn.setEnabled(False)
        self.summaryLb.setText(
            'Lote "{0}" cadastrado.\n{1} produto(s), {2} unidade(s) de trabalho.\n'
            'Confira no acompanhamento antes de distribuir.'.format(
                self.state.lotName, self.state.productsLoaded, self.state.workUnitsLoaded))
        self.showMessage('Atividades criadas. Cadastro concluído.')
        self.updateUi()

    # ---- ciclo de vida ------------------------------------------------------

    def closeEvent(self, event):
        self.qgis.removeDockWidget(self)
        super(NewLotWizard, self).closeEvent(event)
