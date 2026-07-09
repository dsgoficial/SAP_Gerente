from qgis.PyQt import QtWidgets
from qgis import core

from SAP_Gerente.modules.sap.wizard import newLotWizardState as wizardState

from SAP_Gerente.widgets.mLots import MLots
from SAP_Gerente.widgets.mProductionData import MProductionData
from SAP_Gerente.widgets.copySetupLot import CopySetupLot
from SAP_Gerente.widgets.createDefaultSteps import CreateDefaultSteps
from SAP_Gerente.widgets.mBlocks import MBlocks
from SAP_Gerente.widgets.createProduct import CreateProduct
from SAP_Gerente.widgets.generatesWorkUnitSimple import GeneratesWorkUnitSimple
from SAP_Gerente.widgets.loadWorkUnit import LoadWorkUnit
from SAP_Gerente.widgets.createAllActivities import CreateAllActivities


class NewLotWizard(QtWidgets.QDockWidget):
    """Painel guiado para cadastrar um lote do começo ao fim.

    Não reimplementa os widgets do Gerente: abre cada um na ordem certa,
    confere no backend que o passo aconteceu e faz as checagens que o fluxo
    solto não faz. Fica ancorado ao lado do canvas, e não modal, porque entre
    gerar e carregar as unidades de trabalho o gerente EDITA os polígonos.
    """

    # O cliente HTTP devolve lista vazia quando a requisição FALHA (token expirado,
    # erro do servidor), sem levantar exceção. Então "está vazio" e "não consegui
    # perguntar" chegam iguais aqui, e a mensagem não pode afirmar só o primeiro.
    EMPTY_HINT = ('Se você já fez este passo, pode ser falha de conexão ou login expirado '
                  '(nesse caso o SAP mostra um aviso próprio): refaça o login e confira de novo.')

    def __init__(self, controller, qgis, sap, parent=None):
        super(NewLotWizard, self).__init__(parent)
        self.controller = controller
        self.qgis = qgis
        self.sap = sap
        self.state = wizardState.NewLotWizardState()
        self.currentStep = wizardState.STEP_LOT
        self.openedWidget = None
        self.finished = False
        self.pendingMessage = None
        self.pendingMessageIsError = False

        self.setWindowTitle('Novo Lote (guiado)')
        self.setupUi()
        self.updateUi()
        # ancorado à direita: o gerente precisa do canvas livre para editar as UTs
        self.qgis.addDockWidget(self)

    # ---- interface ---------------------------------------------------------

    def setupUi(self):
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)

        self.stepList = QtWidgets.QListWidget()
        self.stepList.setMaximumHeight(220)
        self.stepList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(self.stepList)

        self.titleLb = QtWidgets.QLabel()
        self.titleLb.setStyleSheet('font-weight: bold;')
        layout.addWidget(self.titleLb)

        self.instructionLb = QtWidgets.QLabel()
        self.instructionLb.setWordWrap(True)
        layout.addWidget(self.instructionLb)

        self.lotCb = QtWidgets.QComboBox()
        layout.addWidget(self.lotCb)

        self.productionDataCb = QtWidgets.QComboBox()
        layout.addWidget(self.productionDataCb)

        self.layerCb = self.controller.getQgisComboBoxPolygonLayer()
        layout.addWidget(self.layerCb)

        self.messageLb = QtWidgets.QLabel()
        self.messageLb.setWordWrap(True)
        layout.addWidget(self.messageLb)

        buttons = QtWidgets.QHBoxLayout()
        self.openBtn = QtWidgets.QPushButton('Abrir ferramenta')
        self.openBtn.clicked.connect(self.onOpen)
        buttons.addWidget(self.openBtn)

        self.checkBtn = QtWidgets.QPushButton('Conferir e avançar')
        self.checkBtn.clicked.connect(self.onCheck)
        buttons.addWidget(self.checkBtn)
        layout.addLayout(buttons)

        # As ferramentas (Criar Lote, Configurações de Conexão) criam o registro no
        # SAP, mas o combo do wizard foi carregado antes. Sem isto, o lote recém-criado
        # não aparece na lista e o passo 1 fica impossível de concluir.
        self.refreshBtn = QtWidgets.QPushButton('Atualizar lista')
        self.refreshBtn.clicked.connect(self.onRefresh)
        layout.addWidget(self.refreshBtn)

        self.skipBtn = QtWidgets.QPushButton('Não há lote-modelo, seguir sem copiar perfis')
        self.skipBtn.clicked.connect(self.onSkipProfiles)
        layout.addWidget(self.skipBtn)

        layout.addStretch()
        self.setWidget(content)

    def showMessage(self, text, isError=False):
        color = '#a00' if isError else '#060'
        self.messageLb.setStyleSheet('color: {0};'.format(color))
        self.messageLb.setText(text)

    def updateStepList(self):
        self.stepList.clear()
        for step in wizardState.ALL_STEPS:
            if self.state.isDone(step):
                prefix = '[x] '
            elif step == self.currentStep:
                prefix = '[>] '
            else:
                prefix = '[ ] '
            self.stepList.addItem(prefix + wizardState.STEP_NAMES[step])

    def updateUi(self):
        self.updateStepList()
        step = self.currentStep
        self.titleLb.setText('Passo {0} de {1}: {2}'.format(
            wizardState.ALL_STEPS.index(step) + 1,
            len(wizardState.ALL_STEPS),
            wizardState.STEP_NAMES[step]
        ))
        self.instructionLb.setText(self.instructionFor(step))

        self.lotCb.setVisible(step == wizardState.STEP_LOT)
        self.productionDataCb.setVisible(step == wizardState.STEP_PRODUCTION_DATA)
        self.layerCb.setVisible(step == wizardState.STEP_GENERATE_WORK_UNIT)
        # O botão de pular perfis só aparece quando NÃO há lote-modelo para copiar.
        # Visível sempre, ele convidava a jogar fora os 12 perfis num clique.
        self.skipBtn.setVisible(step == wizardState.STEP_PROFILES and not self.modelLots())
        self.refreshBtn.setVisible(step in (wizardState.STEP_LOT, wizardState.STEP_PRODUCTION_DATA))

        if step == wizardState.STEP_LOT:
            self.reloadLots()
        if step == wizardState.STEP_PRODUCTION_DATA:
            self.reloadProductionData()

        # Concluído: nada mais a abrir nem a conferir (reabrir "Criar Todas as
        # Atividades" duplicaria as atividades do lote).
        self.openBtn.setEnabled(not self.finished)
        self.checkBtn.setEnabled(not self.finished)

        missing = self.state.missingRequirements(step)
        if self.pendingMessage:
            self.showMessage(self.pendingMessage, self.pendingMessageIsError)
            self.pendingMessage = None
        elif missing:
            self.showMessage('Antes deste passo, falta: ' + '; '.join(missing) + '.', True)
        else:
            self.messageLb.setText('')

    def instructionFor(self, step):
        texts = {
            wizardState.STEP_LOT:
                'Crie o lote na ferramenta (o projeto já deve existir). Depois clique em "Atualizar lista" '
                'e selecione abaixo o lote que você acabou de criar.',
            wizardState.STEP_PRODUCTION_DATA:
                'Escolha a configuração de conexão do banco de edição. Se ainda não existir, '
                'crie-a na ferramenta (ela testa a conexão antes de salvar).',
            wizardState.STEP_PROFILES:
                'Copie os perfis (estilos, menus, regras, workflows, FME, monitoramento) de um lote-modelo '
                'da mesma linha de produção. A cópia é atômica: ou vem tudo, ou nada.',
            wizardState.STEP_DEFAULT_STEPS:
                'Crie as etapas padrão por fase. O padrão de controle de qualidade sugerido é "{0}", '
                'mas confirme com a linha de produção.'.format(wizardState.CQ_NAMES[wizardState.CQ_DEFAULT]),
            wizardState.STEP_BLOCK:
                'Crie o bloco do lote (em geral um só, "Bloco 1", prioridade 1).',
            wizardState.STEP_PRODUCTS:
                'Carregue os produtos a partir da camada de molduras. Atenção: o uuid do produto é '
                'CANÔNICO e vem da planilha de produção. Se a camada não trouxer uuid, o produto nasce '
                'com identificador diferente do oficial e será preciso reconciliar depois.',
            wizardState.STEP_GENERATE_WORK_UNIT:
                'Gere as unidades de trabalho. Isto NÃO grava nada no SAP: cria uma camada no QGIS para '
                'você editar os polígonos. Terminada a edição, escolha a camada acima e clique em '
                '"Conferir e avançar".',
            wizardState.STEP_LOAD_WORK_UNIT:
                'Agora sim, grave as unidades de trabalho no SAP. Faça isto UMA vez só: carregar de novo '
                'cria unidades duplicadas, sem dar erro. O wizard confere antes e avisa se já existirem.',
            wizardState.STEP_ACTIVITIES:
                'Crie as atividades de todo o lote de uma vez.'
        }
        return texts.get(step, '')

    # ---- combos ------------------------------------------------------------

    def onRefresh(self):
        if self.currentStep == wizardState.STEP_LOT:
            self.reloadLots()
            self.showMessage('Lista de lotes atualizada.')
        elif self.currentStep == wizardState.STEP_PRODUCTION_DATA:
            self.reloadProductionData()
            self.showMessage('Lista de conexões atualizada.')

    def reloadLots(self):
        self.lotCb.clear()
        self.lotCb.addItem('Selecione o lote criado...', None)
        try:
            for lot in self.sap.getAllLots():
                self.lotCb.addItem(lot['nome'], lot)
        except Exception as e:
            self.showMessage('Não foi possível listar os lotes: {0}'.format(e), True)

    def reloadProductionData(self):
        self.productionDataCb.clear()
        self.productionDataCb.addItem('Selecione a configuração de conexão...', None)
        try:
            for data in self.sap.getProductionData():
                self.productionDataCb.addItem(data['configuracao_producao'], data['id'])
        except Exception as e:
            self.showMessage('Não foi possível listar as conexões: {0}'.format(e), True)

    # ---- abrir a ferramenta do passo ---------------------------------------

    def widgetForStep(self, step):
        if step == wizardState.STEP_LOT:
            return MLots(self.controller, self.qgis, self.sap)
        if step == wizardState.STEP_PRODUCTION_DATA:
            return MProductionData(self.controller, self.qgis, self.sap)
        if step == wizardState.STEP_PROFILES:
            return CopySetupLot(self.sap)
        if step == wizardState.STEP_DEFAULT_STEPS:
            return CreateDefaultSteps(self.controller)
        if step == wizardState.STEP_BLOCK:
            return MBlocks(self.controller, self.qgis, self.sap)
        if step == wizardState.STEP_PRODUCTS:
            return CreateProduct(
                self.controller.getQgisComboBoxPolygonLayer(),
                self.controller.getQgisComboBoxPolygonLayer(),
                self.controller,
                self.qgis
            )
        if step == wizardState.STEP_GENERATE_WORK_UNIT:
            return GeneratesWorkUnitSimple(
                self.controller.getQgisComboBoxPolygonLayer(),
                self.controller.getQgisComboBoxProjection(),
                self.controller,
                self.sap,
                self.qgis
            )
        if step == wizardState.STEP_LOAD_WORK_UNIT:
            return LoadWorkUnit(self.controller.getQgisComboBoxPolygonLayer(), self.controller)
        if step == wizardState.STEP_ACTIVITIES:
            return CreateAllActivities(self.controller, self.sap)
        return None

    def onOpen(self):
        step = self.currentStep
        if not self.state.canEnterStep(step):
            self.showMessage('Falta: ' + '; '.join(self.state.missingRequirements(step)) + '.', True)
            return
        if step == wizardState.STEP_PROFILES and not self.modelLots():
            self.showMessage(
                'Nenhum lote-modelo desta linha de produção. Este é o primeiro lote da linha: '
                'configure os perfis nos gerenciadores e depois clique no botão abaixo para seguir.', True)
            return
        if step == wizardState.STEP_LOAD_WORK_UNIT and not self.confirmWorkUnitLoad():
            return
        try:
            self.openedWidget = self.widgetForStep(step)
            if self.openedWidget:
                self.openedWidget.show()
        except Exception as e:
            self.showMessage('Não foi possível abrir a ferramenta: {0}'.format(e), True)

    def modelLots(self):
        try:
            lots = self.sap.getAllLots()
        except Exception:
            return []
        return wizardState.modelLotCandidates(lots, self.state.productionLineId, self.state.lotId)

    def confirmLotIsNew(self, lot):
        """Barra o uso acidental de um lote que já produz.

        O combo lista TODOS os lotes. Escolher um lote antigo faria o wizard
        carregar UT e criar atividades em cima de produção em andamento.
        """
        try:
            products = self.sap.getProductsByLot(lot['id'])
            workUnits = self.sap.getWorkUnitsByLot(lot['id'])
        except Exception as e:
            self.showMessage('Não foi possível conferir o lote: {0}'.format(e), True)
            return False
        if not products and not workUnits:
            return True
        answer = QtWidgets.QMessageBox.question(
            self,
            'Atenção',
            'O lote "{0}" JÁ tem {1} produto(s) e {2} unidade(s) de trabalho.\n\n'
            'Este wizard é para lote NOVO. Seguir com um lote que já produz pode duplicar '
            'unidades de trabalho e atividades.\n\nDeseja mesmo continuar?'.format(
                lot['nome'], len(products), len(workUnits)),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        return answer == QtWidgets.QMessageBox.StandardButton.Yes

    def confirmWorkUnitLoad(self):
        """Avisa se o lote já tem UT. Carregar de novo duplica em silêncio."""
        try:
            workUnits = self.sap.getWorkUnitsByLot(self.state.lotId)
        except Exception as e:
            self.showMessage('Não foi possível conferir as UTs existentes: {0}'.format(e), True)
            return False
        if not workUnits:
            return True
        counts = wizardState.existingWorkUnitsBySubphase(workUnits)
        detail = ', '.join('subfase {0}: {1} UT'.format(k, v) for k, v in sorted(counts.items()))
        answer = QtWidgets.QMessageBox.question(
            self,
            'Atenção',
            'Este lote JÁ tem unidades de trabalho ({0}).\n\n'
            'A tabela não tem restrição de unicidade: carregar de novo vai DUPLICAR as UTs, '
            'sem erro nenhum.\n\nDeseja mesmo continuar?'.format(detail),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        return answer == QtWidgets.QMessageBox.StandardButton.Yes

    # ---- conferir o passo no backend ---------------------------------------

    def onSkipProfiles(self):
        self.state.profilesSkipped = True
        # Sem o markDone, nextStep() devolvia o passo 3 de novo e o botão não saía do lugar.
        self.state.markDone(wizardState.STEP_PROFILES)
        self.advance('Perfis não copiados (primeiro lote da linha). Configure-os nos gerenciadores.')

    def onCheck(self):
        step = self.currentStep
        try:
            ok, message = self.verifyStep(step)
            if not ok:
                self.showMessage(message, True)
                return
            self.state.markDone(step)
            self.advance(message)
        except Exception as e:
            self.showMessage('Falha ao conferir: {0}'.format(e), True)

    def advance(self, message=None):
        """Vai ao próximo passo pendente, levando a mensagem para depois do redesenho.

        `updateUi` limpa o rótulo de mensagem, então quem chama `advance` guarda
        o texto em `pendingMessage` para ele sobreviver à troca de passo.
        """
        self.pendingMessage = message
        self.pendingMessageIsError = False
        nextStep = self.state.nextStep()
        if nextStep is None:
            self.finished = True
            self.currentStep = wizardState.STEP_ACTIVITIES
            self.pendingMessage = 'Lote cadastrado. Confira no acompanhamento.'
        else:
            self.currentStep = nextStep
        self.updateUi()

    def geometryNameOf(self, layer):
        """Nome da geometria olhando as feições, como o resto do plugin faz.

        A UT exige Polygon; MultiPolygon é recusado pelo backend. O tipo da
        camada mente quando ela é genérica, por isso a checagem é por feição.
        """
        for feature in layer.getFeatures():
            wkbType = feature.geometry().wkbType()
            if wkbType != core.QgsWkbTypes.Polygon:
                return core.QgsWkbTypes.displayString(wkbType)
        return 'Polygon'

    def verifyStep(self, step):
        if step == wizardState.STEP_LOT:
            lot = self.lotCb.currentData()
            if not lot:
                return False, 'Selecione o lote criado na lista.'
            if not self.confirmLotIsNew(lot):
                return False, 'Escolha outro lote, ou crie um novo.'
            self.state.lotId = lot['id']
            self.state.productionLineId = lot['linha_producao_id']
            return True, 'Lote "{0}" reconhecido.'.format(lot['nome'])

        if step == wizardState.STEP_PRODUCTION_DATA:
            productionDataId = self.productionDataCb.currentData()
            if not productionDataId:
                return False, 'Selecione a configuração de conexão.'
            self.state.productionDataId = productionDataId
            return True, 'Conexão definida.'

        if step == wizardState.STEP_PROFILES:
            if self.state.profilesSkipped:
                return True, 'Perfis não copiados (primeiro lote da linha).'
            profiles = [p for p in self.sap.getStyleProfiles() if p.get('lote_id') == self.state.lotId]
            if not profiles:
                return False, (
                    'O lote ainda não tem perfis de estilo. Abra a ferramenta e copie a configuração '
                    'de um lote-modelo. (Se a lista veio vazia por erro de conexão ou login expirado, '
                    'o SAP mostra um aviso próprio.)')
            return True, '{0} perfil(is) de estilo no lote.'.format(len(profiles))

        if step == wizardState.STEP_DEFAULT_STEPS:
            steps = [s for s in self.sap.getSteps() if s.get('lote_id') == self.state.lotId]
            if not steps:
                return False, 'O lote ainda não tem etapas. ' + self.EMPTY_HINT
            return True, '{0} etapa(s) encontradas no lote.'.format(len(steps))

        if step == wizardState.STEP_BLOCK:
            blocks = [b for b in self.sap.getAllBlocks() if b.get('lote_id') == self.state.lotId]
            if not blocks:
                return False, 'O lote ainda não tem bloco. ' + self.EMPTY_HINT
            self.state.blockId = blocks[0]['id']
            return True, 'Bloco "{0}" encontrado.'.format(blocks[0]['nome'])

        if step == wizardState.STEP_PRODUCTS:
            products = self.sap.getProductsByLot(self.state.lotId)
            if not products:
                return False, 'O lote ainda não tem produtos. ' + self.EMPTY_HINT
            return True, '{0} produto(s) no lote.'.format(len(products))

        if step == wizardState.STEP_GENERATE_WORK_UNIT:
            layer = self.layerCb.currentLayer()
            if not layer:
                return False, 'Selecione a camada de unidades de trabalho gerada.'
            errors = wizardState.validateWorkUnitLayer(
                layer.featureCount(),
                self.geometryNameOf(layer),
                layer.crs().authid()
            )
            if errors:
                return False, ' '.join(errors)
            self.state.workUnitLayerChecked = True
            return True, 'Camada com {0} feição(ões) conferida.'.format(layer.featureCount())

        if step == wizardState.STEP_LOAD_WORK_UNIT:
            workUnits = self.sap.getWorkUnitsByLot(self.state.lotId)
            if not workUnits:
                return False, 'O lote ainda não tem unidades de trabalho no SAP. ' + self.EMPTY_HINT
            self.state.subphaseIds = sorted(set(w['subfase_id'] for w in workUnits))
            return True, '{0} unidade(s) de trabalho no lote.'.format(len(workUnits))

        if step == wizardState.STEP_ACTIVITIES:
            # Não há rota de leitura de atividade por lote, então não dá para
            # conferir por GET. Em vez de afirmar "atividades criadas" sem saber,
            # pergunta ao gerente.
            answer = QtWidgets.QMessageBox.question(
                self,
                'Confirmar',
                'O SAP não oferece uma consulta de atividades por lote, então o wizard não '
                'consegue conferir este passo sozinho.\n\n'
                'As atividades do lote foram criadas na ferramenta?',
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            if answer != QtWidgets.QMessageBox.StandardButton.Yes:
                return False, 'Abra a ferramenta e crie as atividades do lote.'
            return True, 'Atividades confirmadas pelo gerente.'

        return False, 'Passo desconhecido.'

    def closeEvent(self, event):
        if self.openedWidget:
            self.openedWidget.close()
        self.qgis.removeDockWidget(self)
        super(NewLotWizard, self).closeEvent(event)
