# -*- coding: utf-8 -*-
# Fumaça do SAP Gerente com o versionamento: o QGIS 4 real, sem interface,
# monta o painel (`factories/dockDirector.py`) contra o servidor FALSO
# (`servidor_falso.py`), abre CADA ação registrando exceção, e roda os cenários
# da integração do versionamento. Grava um JSON com o resultado e o registro de
# todas as chamadas HTTP, que o `conferir_chamadas.py` confere contra o
# roteador do servidor Node.
#
# Uso (QGIS 4, sem interface):
#   QT_QPA_PLATFORM=offscreen <python-qgis do QGIS 4> fumaca_painel.py \
#       --saida <arquivo.json> [--plugin <pasta SAP_Gerente a testar>]
#
# `--plugin` aponta OUTRA cópia do plugin (um worktree do HEAD, por exemplo)
# para provar que os cenários REPROVAM o estado anterior. A pasta tem de se
# chamar `SAP_Gerente`, porque o plugin se importa pelo nome do pacote.
#
# Nada aqui toca sistema real: o servidor é local e fictício, o perfil do QGIS é
# uma pasta temporária e as caixas de mensagem são interceptadas.

import argparse
import json
import os
import sys
import tempfile
import time
import traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
PLUGIN_PADRAO = os.path.abspath(os.path.join(AQUI, '..', '..'))


def argumentos():
    p = argparse.ArgumentParser()
    p.add_argument('--saida', required=True)
    p.add_argument('--plugin', default=PLUGIN_PADRAO)
    return p.parse_args()


ARGS = argumentos()
PLUGIN = os.path.abspath(ARGS.plugin)
if os.path.basename(PLUGIN) != 'SAP_Gerente':
    sys.exit('--plugin tem de ser uma pasta chamada SAP_Gerente')

# Perfil do QGIS descartável: a fumaça não escreve no perfil de quem a roda.
PERFIL = tempfile.mkdtemp(prefix='fumaca_sap_gerente_')
os.environ['QGIS_CUSTOM_CONFIG_PATH'] = PERFIL
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.dirname(PLUGIN))

from qgis.core import QgsApplication  # noqa: E402

APP = QgsApplication([], False)
APP.initQgis()
# `processing` mora nos plugins de núcleo do QGIS.
sys.path.append(os.path.join(QgsApplication.pkgDataPath(), 'python', 'plugins'))

from unittest import mock  # noqa: E402
from qgis.PyQt import QtCore, QtWidgets  # noqa: E402
from qgis import gui  # noqa: E402
import qgis.utils  # noqa: E402

import servidor_falso  # noqa: E402


class IfaceFalso:
    # O bastante do `iface` para o plugin montar o painel sem a janela do QGIS.
    def __init__(self):
        self._janela = QtWidgets.QMainWindow()
        self._canvas = gui.QgsMapCanvas()

    def mainWindow(self):
        return self._janela

    def mapCanvas(self):
        return self._canvas

    def firstRightStandardMenu(self):
        if '_menuAjuda' not in self.__dict__:
            self._menuAjuda = self._janela.menuBar().addMenu('Ajuda')
        return self._menuAjuda

    def __getattr__(self, nome):
        return mock.MagicMock(name='iface.' + nome)


qgis.utils.iface = IfaceFalso()

# Caixas de mensagem e diálogos modais: registrados, nunca bloqueiam.
MENSAGENS = []


def _caixa(tipo):
    def mostrar(parent, title, text, *args, **kwargs):
        MENSAGENS.append({'tipo': tipo, 'titulo': title, 'texto': text})
        if tipo == 'question':
            return QtWidgets.QMessageBox.StandardButton.Yes
        return QtWidgets.QMessageBox.StandardButton.Ok
    return staticmethod(mostrar)


for _tipo in ('critical', 'information', 'warning', 'question'):
    setattr(QtWidgets.QMessageBox, _tipo, _caixa(_tipo))

RESPOSTA_INPUT = {'texto': 'Motivo de teste: clone criado por engano', 'ok': True}
QtWidgets.QInputDialog.getMultiLineText = staticmethod(
    lambda *a, **k: (RESPOSTA_INPUT['texto'], RESPOSTA_INPUT['ok'])
)
QtWidgets.QInputDialog.getText = staticmethod(
    lambda *a, **k: (RESPOSTA_INPUT['texto'], RESPOSTA_INPUT['ok'])
)

from SAP_Gerente.modules.qgis.qgisCtrl import QgisCtrl  # noqa: E402
from SAP_Gerente.modules.fme.fmeCtrl import FmeCtrl  # noqa: E402
from SAP_Gerente.modules.sap.api import sapHttp as moduloSapHttp  # noqa: E402
from SAP_Gerente.modules.sap.api.sapHttp import SapHttp  # noqa: E402
from SAP_Gerente.controllers.mToolCtrl import MToolCtrl  # noqa: E402
from SAP_Gerente.factories.dockDirector import DockDirector  # noqa: E402
from SAP_Gerente.factories.mDockBuilder import MDockBuilder  # noqa: E402

try:
    from SAP_Gerente.widgets import versionamento as moduloVersionamento
except ImportError:
    moduloVersionamento = None


def esperar(condicao, teto=15.0):
    fim = time.time() + teto
    while time.time() < fim:
        APP.processEvents()
        if condicao():
            return True
        time.sleep(0.01)
    APP.processEvents()
    return condicao()


def textos(tipo=None, desde=0):
    return [m['texto'] for m in MENSAGENS[desde:] if tipo is None or m['tipo'] == tipo]


SERVIDOR, ESTADO, BASE = servidor_falso.iniciar()


def cenario_falso(**valores):
    import requests
    requests.post(BASE + '/__cenario', json=valores, timeout=5)


def chamadas(metodo=None, prefixo='', desde=0):
    with ESTADO.lock:
        lista = list(ESTADO.chamadas[desde:])
    return [
        c for c in lista
        if (metodo is None or c['metodo'] == metodo) and c['caminho'].startswith(prefixo)
    ]


qgisCtrl = QgisCtrl()
fmeCtrl = FmeCtrl()
sap = SapHttp(qgis=qgisCtrl, fmeCtrl=fmeCtrl)
sap.setServer(BASE)
sap.setToken('token-falso')
controller = MToolCtrl(qgis=qgisCtrl, fmeCtrl=fmeCtrl, sapCtrl=sap)
builder = MDockBuilder()
DockDirector().constructSapMDock(builder, controller, qgisCtrl, sap, fmeCtrl)
dock = builder.getResult()
controller.dockSap = dock

RESULTADO = {'acoes': {}, 'cenarios': [], 'mensagens_ao_abrir': {}}

# --- 1. Abrir cada ação do painel --------------------------------------------
for nome in list(dock.widgets):
    inicio = len(MENSAGENS)
    try:
        widget = dock.widgets[nome]()
        widget.show()
        APP.processEvents()
        widget.close()
        APP.processEvents()
        RESULTADO['acoes'][nome] = 'ok'
    except Exception:
        RESULTADO['acoes'][nome] = traceback.format_exc(limit=4)
    erros = textos('critical', inicio)
    if erros:
        RESULTADO['mensagens_ao_abrir'][nome] = erros

# --- 2. Cenários da integração ------------------------------------------------
CENARIOS = []


def cenario(funcao):
    CENARIOS.append(funcao)
    return funcao


def abrir(nome):
    if nome not in dock.widgets:
        raise AssertionError('a ação "{0}" não está no painel'.format(nome))
    widget = dock.widgets[nome]()
    widget.show()
    APP.processEvents()
    return widget


def itens(combo):
    return [(combo.itemText(i), combo.itemData(i)) for i in range(combo.count())]


@cenario
def item1_combos_gerar_ut_aceitam_tipo4():
    """Gerar UT (simples e avançado) lista o dado de produção tipo 4, com rótulo."""
    for nome in ('Gerar Unidades de Trabalho', 'Gerar Unidades de Trabalho Avançado'):
        w = abrir(nome)
        lista = itens(w.databasesCb)
        w.close()
        ids = [d for _, d in lista]
        assert 4 in ids, '{0}: tipo 4 ausente do combo {1}'.format(nome, lista)
        rotulo = [t for t, d in lista if d == 4][0]
        assert rotulo and 'Base versionada' in rotulo, '{0}: rótulo do tipo 4 = {1!r}'.format(nome, rotulo)
        assert {1, 2} <= set(ids), '{0}: sumiram os tipos 2 e 3: {1}'.format(nome, lista)
    return 'tipo 4 presente nos dois combos'


@cenario
def item1_revogar_continua_so_tipos_2_e_3():
    """Revogar Permissões (e de usuários) não oferece a base versionada."""
    for nome in ('Revogar Permissões', 'Revogar Permissões Usuários'):
        w = abrir(nome)
        lista = itens(w.databasesCb)
        w.close()
        ids = [d for _, d in lista if d is not None]
        assert ids == [1, 2], '{0}: esperado [1, 2], veio {1}'.format(nome, lista)
    return 'só 1 e 2 (tipos 2 e 3)'


@cenario
def item2_configuracoes_conexao_tipo4_so_repo():
    """Tipo 4 pede só o repo_id (lista do serviço), sem IP/porta/banco nem teste psycopg2."""
    from SAP_Gerente.widgets.addProductionDataForm import AddProductionDataForm
    desde = len(ESTADO.chamadas)
    form = AddProductionDataForm(controller, sap, qgisCtrl)
    form.show()
    APP.processEvents()
    form.typeProductionDataCb.setCurrentIndex(form.typeProductionDataCb.findData(4))
    APP.processEvents()
    assert not form.ipDBLe.isVisible(), 'IP do banco visível no tipo 4'
    assert not form.portDBLe.isVisible() and not form.nameDBLe.isVisible(), 'porta/banco visíveis'
    repos = [form.repoCb.itemData(i) for i in range(form.repoCb.count())]
    assert repos == ['base-edgv-1'], 'lista de bases do serviço: {0}'.format(repos)
    form.repoCb.setCurrentIndex(0)
    with mock.patch('SAP_Gerente.widgets.addProductionDataForm.TestDatabase') as teste:
        form.okBtn.click()
        APP.processEvents()
        assert not teste.called, 'testou conexão psycopg2 no tipo 4'
    posts = chamadas('POST', '/api/producao/dado_producao', desde)
    assert posts, 'não gravou o dado de produção'
    corpo = posts[-1]['corpo']
    assert corpo == {'dado_producao': [{'configuracao_producao': 'base-edgv-1', 'tipo_dado_producao_id': 4}]}, corpo
    # Tipo 2: os campos de banco voltam.
    form2 = AddProductionDataForm(controller, sap, qgisCtrl)
    form2.show()
    form2.typeProductionDataCb.setCurrentIndex(form2.typeProductionDataCb.findData(2))
    APP.processEvents()
    assert form2.ipDBLe.isVisible() and not form2.repoCb.isVisible(), 'tipo 2 sem os campos de banco'
    form2.close()
    return 'corpo {0}'.format(corpo)


@cenario
def item2_sem_acesso_a_lista_digita_repo():
    """Se o repasse recusa GET /repos (403), o repo_id é digitado e nenhuma caixa de erro aparece."""
    from SAP_Gerente.widgets.addProductionDataForm import AddProductionDataForm
    cenario_falso(reposProibido=True)
    try:
        inicio = len(MENSAGENS)
        desde = len(ESTADO.chamadas)
        form = AddProductionDataForm(controller, sap, qgisCtrl)
        form.show()
        form.typeProductionDataCb.setCurrentIndex(form.typeProductionDataCb.findData(4))
        APP.processEvents()
        assert form.repoCb.count() == 0, 'lista deveria vir vazia'
        assert not textos('critical', inicio), 'caixa de erro: {0}'.format(textos('critical', inicio))
        form.repoCb.setEditText('base-digitada')
        form.okBtn.click()
        APP.processEvents()
        corpo = chamadas('POST', '/api/producao/dado_producao', desde)[-1]['corpo']
        assert corpo['dado_producao'][0]['configuracao_producao'] == 'base-digitada', corpo
        form.close()
    finally:
        cenario_falso(reposProibido=False)
    return 'digitado e gravado'


@cenario
def item3_importar_camadas_da_base_versionada():
    """Importar Camadas lê os datasets do repositório (schema.nome), sem PostGIS, e importa."""
    w = abrir('Importar Camadas')
    alvo = [i for i in range(w.databasesCb.count()) if 'Base versionada' in w.databasesCb.itemText(i)]
    assert alvo, 'a base versionada não aparece no combo: {0}'.format(itens(w.databasesCb))
    desde = len(ESTADO.chamadas)
    with mock.patch.object(controller.databasesFactory, 'getDatabase') as pg:
        w.databasesCb.setCurrentIndex(alvo[0])
        APP.processEvents()
        assert not pg.called, 'abriu conexão PostGIS para a base versionada'
    linhas = [w.getRowData(i) for i in range(w.tableWidget.rowCount())]
    pares = sorted((l['schema'], l['nome']) for l in linhas)
    assert pares == [('edgv', 'cobter_area_construida_a'), ('edgv', 'elemnat_curva_nivel_l')], pares
    lidos = chamadas('GET', '/api/versionamento/servico/repos/base-edgv-1/datasets', desde)
    assert lidos, 'não leu os datasets pelo repasse'
    w.tableWidget.cellWidget(0, 0).layout().itemAt(0).widget().setChecked(True)
    nomeMarcado = w.getRowData(0)['nome']
    w.saveTable()
    APP.processEvents()
    posts = chamadas('POST', '/api/producao/configuracao/camadas', desde)
    assert posts and posts[-1]['corpo'] == {'camadas': [{'nome': nomeMarcado, 'schema': 'edgv'}]}, posts
    w.close()
    return 'importada {0}'.format(nomeMarcado)


@cenario
def item3_import_layers_nao_quebra_depois_de_gravar():
    """Defeito antigo: `mToolCtrl.importLayers` quebrava DEPOIS de gravar (fábrica devolvia None)."""
    desde = len(ESTADO.chamadas)
    resposta = controller.importLayers([{'nome': 'teste_p', 'schema': 'edgv'}])
    assert chamadas('POST', '/api/producao/configuracao/camadas', desde), 'não gravou'
    return 'devolveu {0!r}'.format(resposta)


def _esperarTarefa(widget, jobId):
    assert esperar(lambda: 'succeeded' in widget.statusLb.text(), 20), \
        'a tarefa {0} não terminou: {1!r}'.format(jobId, widget.statusLb.text())


@cenario
def item4_versionar_lote_com_progresso_sem_travar():
    """Versionar Lote: POST com dado_producao_id, 202 com job_id, progresso por QgsTask sem travar."""
    if moduloVersionamento is not None:
        moduloVersionamento.VersionamentoJobTask.INTERVALO = 0.3
    w = abrir('Versionar Lote')
    w.lotesCb.setCurrentIndex(w.lotesCb.findData(10))
    w.basesCb.setCurrentIndex(w.basesCb.findData(4))
    desde = len(ESTADO.chamadas)
    t0 = time.time()
    w.okBtn.click()
    duracaoClique = time.time() - t0
    posts = chamadas('POST', '/api/versionamento/lote/', desde)
    assert posts and posts[-1]['caminho'] == '/api/versionamento/lote/10', posts
    assert posts[-1]['corpo'] == {'dado_producao_id': 4}, posts[-1]['corpo']
    tiques = {'n': 0}
    relogio = QtCore.QTimer()
    relogio.timeout.connect(lambda: tiques.__setitem__('n', tiques['n'] + 1))
    relogio.start(20)
    vistos = set()

    def progresso():
        vistos.add(w.statusLb.text())
        return 'succeeded' in w.statusLb.text()
    assert esperar(progresso, 20), 'a tarefa não terminou: {0!r}'.format(w.statusLb.text())
    relogio.stop()
    leituras = chamadas('GET', '/api/versionamento/servico/jobs/job-lote-10', desde)
    assert len(leituras) >= 3, 'leu a tarefa {0} vezes'.format(len(leituras))
    assert any('running' in v for v in vistos), 'o progresso intermediário não apareceu: {0}'.format(vistos)
    assert duracaoClique < 0.5, 'o clique travou a interface por {0:.2f} s'.format(duracaoClique)
    assert tiques['n'] >= 10, 'o laço de eventos não girou durante a tarefa ({0} tiques)'.format(tiques['n'])
    w.close()
    return 'clique {0:.3f} s, {1} leituras, {2} tiques'.format(duracaoClique, len(leituras), tiques['n'])


@cenario
def item4_versionar_bloco():
    """Versionar Bloco: POST /api/versionamento/bloco/:id e acompanhamento."""
    w = abrir('Versionar Bloco')
    w.blocosCb.setCurrentIndex(w.blocosCb.findData(20))
    desde = len(ESTADO.chamadas)
    w.okBtn.click()
    posts = chamadas('POST', '/api/versionamento/bloco/', desde)
    assert posts and posts[-1]['caminho'] == '/api/versionamento/bloco/20', posts
    _esperarTarefa(w, 'job-bloco-20')
    w.close()
    return 'corpo {0}'.format(posts[-1]['corpo'])


@cenario
def item4_acompanhar_e_descartar():
    """Acompanhar Versionamento: lista, acompanha a tarefa e descarta com motivo."""
    w = abrir('Acompanhar Versionamento')
    assert w.tabela.rowCount() == 2, 'linhas: {0}'.format(w.tabela.rowCount())
    estados = [w.tabela.item(i, 6).text() for i in range(2)]
    assert estados == ['vivo', 'vivo'], estados
    assert 'running: Copiando feições (20)' == w.tabela.item(0, 7).text(), w.tabela.item(0, 7).text()
    assert 'job-bloco-20' == w.tabela.item(1, 7).text(), w.tabela.item(1, 7).text()
    ESTADO.leiturasJob.pop('job-bloco-20', None)
    w.tabela.selectRow(1)
    desde = len(ESTADO.chamadas)
    w.acompanharBtn.click()
    _esperarTarefa(w, 'job-bloco-20')
    w.tabela.selectRow(1)
    desde = len(ESTADO.chamadas)
    w.descartarBtn.click()
    APP.processEvents()
    posts = chamadas('POST', '/api/versionamento/repositorio/', desde)
    assert posts and posts[-1]['caminho'] == '/api/versionamento/repositorio/2/descartar', posts
    assert posts[-1]['corpo'] == {'motivo': RESPOSTA_INPUT['texto']}, posts[-1]['corpo']
    w.close()
    return 'descartado com motivo'


@cenario
def item5_tipo_etapa_e_padroes_vem_do_servidor():
    """Etapa 6 'Integração': o combo de tipo de etapa e os padrões de etapas vêm do servidor."""
    w = abrir('Criar Etapas Padrão')
    padroes = [d for _, d in itens(w.defaultCb)]
    w.close()
    assert 4 in padroes, 'Criar Etapas Padrão usa a lista fixa: {0}'.format(padroes)
    from SAP_Gerente.widgets.addProfileProductionSetting import AddProfileProductionSetting
    form = AddProfileProductionSetting(controller, None)
    form.loadSteps(controller.getSapStepType())
    tipos = [d for _, d in itens(form.stepCb)]
    form.close()
    assert 6 in tipos, 'tipo de etapa 6 ausente: {0}'.format(tipos)
    return 'padrões {0}, tipos de etapa {1}'.format(padroes, tipos)


class BancoLocalFalso:
    # `public.sap_local` em memória: a fumaça não abre PostgreSQL. Registra as
    # consultas e guarda a linha que o "Configurar SAP Local" grava e o
    # "Finalizar SAP Local" lê.
    def __init__(self):
        self.linha = None
        self.consultas = []
        self.conexoes = []

    def fabrica(self):
        banco = self

        class PgFalso:
            def __init__(self, *args):
                banco.conexoes.append(args)

            def execute(self, query, params):
                q = ' '.join(query.split())
                banco.consultas.append((q, params))
                if q.startswith('SELECT * FROM public.sap_local'):
                    return []
                if q.startswith('SELECT count(*) FROM public.sap_local'):
                    return [(1 if banco.linha else 0,)]
                if q.startswith('INSERT INTO public.sap_local'):
                    banco.linha = {'atividade_id': params[0], 'json': params[1]}
                    return [(params[0],)]
                if q.startswith('SELECT atividade_id, data_inicio::text'):
                    l = banco.linha
                    return [(l['atividade_id'], '2026-10-13 08:00:00-03', '2026-10-13 12:00:00-03',
                             '00000000-0000-4000-8000-000000000001', l['json'])]
                if q.startswith('UPDATE public.sap_local SET json_atividade'):
                    banco.linha['json'] = params[0]
                    return [(banco.linha['atividade_id'],)]
                raise AssertionError('consulta não esperada no banco local: ' + q)
        return PgFalso

    def pacote(self):
        return json.loads(self.linha['json'])


DB_LOCAL = {
    'alias': 'teste', 'database': 'banco_local', 'host': 'servidor-local', 'port': '0',
    'username': 'usuario_local', 'password': 'senha-do-banco-local-falsa'
}
SENHA_GERENTE = 'senha-do-gerente-no-sap-falsa'


def _settingsFalso(chave):
    return {'sapmanager:user': 'gerente', 'sapmanager:password': SENHA_GERENTE}.get(chave)


def _zerarCampo():
    with ESTADO.lock:
        ESTADO.iniciadas.clear()
        ESTADO.emCampo.clear()
        ESTADO.campoRecebido.clear()
        ESTADO.campoRecusa = None
        ESTADO.conflitosFinalizar = 0
        ESTADO.campoPendenteSempre = False
        ESTADO.sessaoResolvida = False
        ESTADO.pendentesServidor = None


def _configurarSAPLocal(banco, atividade, pasta):
    w = abrir('Configurar SAP Local')
    w.dbCb.addItem('banco local de teste', json.dumps(DB_LOCAL))
    w.dbCb.setCurrentIndex(w.dbCb.count() - 1)
    w.activityIdLe.setText(str(atividade))
    if pasta is not None:
        w.pastaCampoFw.setFilePath(pasta)
    inicio = len(MENSAGENS)
    with mock.patch.object(moduloSapHttp, 'Postgresql', banco.fabrica()), \
            mock.patch.object(qgisCtrl, 'getSettingsVariable', side_effect=_settingsFalso):
        w.okBtn.click()
    APP.processEvents()
    QtWidgets.QApplication.restoreOverrideCursor()
    w.close()
    return MENSAGENS[inicio:]


def _prepararCampo():
    # O estado de uma atividade do tipo 4 configurada em modo local: banco
    # local com o pacote e a pasta com o arquivo de campo.
    _zerarCampo()
    banco = BancoLocalFalso()
    pasta = tempfile.mkdtemp(prefix='fumaca_campo_')
    vistas = _configurarSAPLocal(banco, 77, pasta)
    assert banco.linha, 'o pacote não foi gravado no banco local: {0}'.format(vistas)
    return banco, pasta


def _finalizarSAPLocal(banco, pasta):
    w = abrir('Finalizar SAP Local')
    w.dbCb.addItem('banco local de teste', dict(DB_LOCAL))
    w.dbCb.setCurrentIndex(w.dbCb.count() - 1)
    if pasta is not None and hasattr(w, 'pastaCampoFw'):
        w.pastaCampoFw.setFilePath(pasta)
    inicio = len(MENSAGENS)
    with mock.patch.object(moduloSapHttp, 'Postgresql', banco.fabrica()):
        w.okBtn.click()
    APP.processEvents()
    QtWidgets.QApplication.restoreOverrideCursor()
    w.close()
    return MENSAGENS[inicio:]


def _indice(lista, metodo, caminho):
    for i, c in enumerate(lista):
        if c['metodo'] == metodo and c['caminho'] == caminho:
            return i
    return None


@cenario
def item7_sap_local_tipo4_baixa_o_campo():
    """Configurar SAP Local, tipo 4: inicia o modo local, DEPOIS baixa o campo em fluxo e põe arquivo e sha256 no pacote."""
    import hashlib
    _zerarCampo()
    banco = BancoLocalFalso()
    pasta = tempfile.mkdtemp(prefix='fumaca_campo_')
    desde = len(ESTADO.chamadas)
    vistas = _configurarSAPLocal(banco, 77, pasta)
    lista = chamadas(desde=desde)
    iniciar = _indice(lista, 'PUT', '/api/gerencia_producao/iniciar_modo_local')
    baixar = _indice(lista, 'GET', '/api/versionamento/atividade/77/campo')
    assert iniciar is not None, 'não iniciou o modo local: {0}'.format(vistas)
    assert baixar is not None and baixar > iniciar, \
        'o campo tem de ser baixado depois do iniciar_modo_local (iniciar {0}, baixar {1})'.format(iniciar, baixar)
    arquivo = os.path.join(pasta, 'atividade-77.gpkg')
    assert os.path.isfile(arquivo), 'arquivo de campo ausente: {0}'.format(os.listdir(pasta))
    assert not [n for n in os.listdir(pasta) if n.endswith('.part')], 'sobrou .part: {0}'.format(os.listdir(pasta))
    esperado = hashlib.sha256(servidor_falso.ARQUIVO_CAMPO).hexdigest()
    with open(arquivo, 'rb') as f:
        assert hashlib.sha256(f.read()).hexdigest() == esperado, 'o arquivo baixado não é o do servidor'
    pacote = banco.pacote()
    versionamento = (pacote['dados'].get('atividade') or {}).get('versionamento') or pacote['dados'].get('versionamento')
    assert versionamento['arquivo'] == 'atividade-77.gpkg', versionamento
    assert versionamento['sha256'] == esperado, versionamento
    assert versionamento['repo_id'] == 'atividade-77', 'o pacote ficou sem o repo_id do clone: {0}'.format(versionamento)
    assert not any(m['tipo'] == 'critical' for m in vistas), vistas
    return '{0} bytes, sha256 {1}..., arquivo {2}'.format(
        os.path.getsize(arquivo), esperado[:12], versionamento['arquivo'])


@cenario
def item7_sap_local_tipo4_sem_pasta_nao_inicia():
    """Configurar SAP Local, tipo 4 sem a pasta do campo: recusa ANTES de iniciar o modo local."""
    _zerarCampo()
    banco = BancoLocalFalso()
    desde = len(ESTADO.chamadas)
    vistas = _configurarSAPLocal(banco, 77, None)
    assert not chamadas('PUT', '/api/gerencia_producao/iniciar_modo_local', desde), \
        'iniciou o modo local sem ter onde gravar o campo'
    assert any('pasta' in m['texto'] for m in vistas if m['tipo'] == 'critical'), vistas
    assert banco.linha is None, 'gravou pacote sem o campo'
    return 'recusado sem mutar'


@cenario
def item7_sap_local_nao_grava_segredo():
    """Configurar SAP Local: o pacote gravado no banco local não leva a senha do gerente no SAP nem a do banco local."""
    _zerarCampo()
    banco = BancoLocalFalso()
    vistas = _configurarSAPLocal(banco, 78, None)
    assert banco.linha, 'não gravou o pacote: {0}'.format(vistas)
    texto = banco.linha['json']
    achados = [s for s in (SENHA_GERENTE, DB_LOCAL['password']) if s in texto]
    assert not achados, 'segredo gravado no banco local: {0}'.format(achados)
    pacote = banco.pacote()
    assert pacote['local_db'].get('host') == 'localhost' and pacote['local_db'].get('database') == 'banco_local', \
        pacote['local_db']
    return 'local_db {0}'.format(sorted(pacote['local_db']))


@cenario
def item7_finalizar_tipo4_sobe_campo_e_finaliza():
    """Finalizar SAP Local, tipo 4: sobe o arquivo (binário, em fluxo) e SÓ ENTÃO chama finalizar_modo_local."""
    import hashlib
    banco, pasta = _prepararCampo()
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    lista = chamadas(desde=desde)
    subir = _indice(lista, 'POST', '/api/versionamento/atividade/77/campo')
    finalizar = _indice(lista, 'PUT', '/api/gerencia_producao/finalizar_modo_local')
    assert subir is not None, 'não subiu o campo: {0}'.format(vistas)
    assert finalizar is not None and finalizar > subir, 'finalizou antes de subir o campo'
    corpo = lista[subir]['corpo']
    with open(os.path.join(pasta, 'atividade-77.gpkg'), 'rb') as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    assert corpo.get('sha256') == sha and corpo.get('content_type') == 'application/geopackage+sqlite3', corpo
    assert lista[finalizar]['status'] == 200, lista[finalizar]
    assert lista[finalizar]['corpo']['atividade_id'] == 77, lista[finalizar]['corpo']
    assert any('finalizada' in m['texto'] for m in vistas if m['tipo'] == 'information'), vistas
    assert not any(m['tipo'] == 'critical' for m in vistas), vistas
    return '{0} bytes enviados, finalizar {1}'.format(corpo.get('binario'), lista[finalizar]['status'])


@cenario
def item7_finalizar_tipo4_conflito_abre_resolucao():
    """Finalizar SAP Local, tipo 4: o 409 conflito_versionamento abre a resolução do módulo comum e finaliza de novo."""
    from SAP_Gerente.modules.versionamento import painel
    banco, pasta = _prepararCampo()
    ESTADO.conflitosFinalizar = 1
    visto = {}

    def execFalso(dialogo):
        visto['linhas'] = dialogo.table.rowCount()
        visto['sessao'] = (dialogo.resolver.repo, dialogo.resolver.session)
        dialogo.table.selectRow(0)
        dialogo.decide('mine', ask=False)
        visto['pendentes'] = dialogo.pending
        return QtWidgets.QDialog.DialogCode.Accepted

    desde = len(ESTADO.chamadas)
    with mock.patch.object(painel.ConflictDialog, 'exec', execFalso):
        vistas = _finalizarSAPLocal(banco, pasta)
    finais = chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde)
    assert [c['status'] for c in finais] == [409, 200], [c['status'] for c in finais]
    assert visto.get('sessao') == ('bloco-20', 'sessao-1'), visto
    assert visto.get('linhas') == 1, 'a resolução não leu os itens da sessão: {0}'.format(visto)
    itens_ = chamadas('GET', '/api/versionamento/servico/repos/bloco-20/sessions/sessao-1/items', desde)
    resolve = chamadas('POST', '/api/versionamento/servico/repos/bloco-20/sessions/sessao-1/resolve', desde)
    assert itens_ and all(c['bearer'] for c in itens_), 'itens da sessão sem Bearer pelo repasse'
    assert resolve, 'a decisão não foi gravada pelo repasse'
    # Sessão de merge (`mode` push, no bloco): "o meu" é a origem, o trabalho de campo.
    assert resolve[-1]['corpo'].get('result') == {'nome': 'C'}, resolve[-1]['corpo']
    assert len(chamadas('POST', '/api/versionamento/atividade/77/campo', desde)) == 1, 'subiu o campo duas vezes'
    assert not any(m['tipo'] == 'critical' for m in vistas), vistas
    return 'sessão {0}, {1} item, pendentes depois {2}'.format(visto['sessao'], visto['linhas'], visto['pendentes'])


@cenario
def item7_finalizar_tipo4_conflito_fechado_e_reenvio():
    """Conflito com a tela fechada: mensagem com a sessão; a segunda finalização NÃO sobe o mesmo campo de novo."""
    from SAP_Gerente.modules.versionamento import painel
    banco, pasta = _prepararCampo()
    ESTADO.conflitosFinalizar = 1
    desde = len(ESTADO.chamadas)
    with mock.patch.object(painel.ConflictDialog, 'exec',
                           lambda d: QtWidgets.QDialog.DialogCode.Rejected):
        vistas = _finalizarSAPLocal(banco, pasta)
    erros = [m['texto'] for m in vistas if m['tipo'] == 'critical']
    assert erros and 'sessao-1' in erros[-1] and 'continua em modo local' in erros[-1], vistas
    assert [c['status'] for c in chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde)] == [409]
    versionamento = banco.pacote()['dados']['atividade']['versionamento']
    assert versionamento.get('enviado_sha256') == versionamento.get('sha256'), versionamento
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    assert not chamadas('POST', '/api/versionamento/atividade/77/campo', desde), 'subiu de novo o mesmo campo'
    assert [c['status'] for c in chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde)] == [200]
    return erros[-1].replace('\n', ' | ')


@cenario
def item7_finalizar_tipo4_campo_ja_devolvido():
    """nao_em_campo na devolução: sem marca local, finaliza; com a marca de OUTRO arquivo, para sem finalizar."""
    banco, pasta = _prepararCampo()
    ESTADO.emCampo.discard(77)
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    finais = chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde)
    assert [c['status'] for c in chamadas('POST', '/api/versionamento/atividade/77/campo', desde)] == [409]
    assert [c['status'] for c in finais] == [200], vistas
    assert not any(m['tipo'] == 'critical' for m in vistas), vistas
    banco, pasta = _prepararCampo()
    ESTADO.emCampo.discard(77)
    pacote = banco.pacote()
    pacote['dados']['atividade']['versionamento']['enviado_sha256'] = '0' * 64
    banco.linha['json'] = json.dumps(pacote)
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    assert not chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde), 'finalizou com edições perdidas'
    erros = [m['texto'] for m in vistas if m['tipo'] == 'critical']
    assert erros and 'mudou depois de devolvido' in erros[-1], vistas
    return erros[-1]


@cenario
def item7_finalizar_tipo4_arquivo_aberto_no_qgis():
    """Arquivo aberto no QGIS (bytes mudados) e com o .sap-conferido.json ao lado: sobe o arquivo de agora e finaliza."""
    import hashlib
    banco, pasta = _prepararCampo()
    arquivo = os.path.join(pasta, 'atividade-77.gpkg')
    # O SAP Operador mediu: abrir o GeoPackage no QGIS já muda os bytes, e
    # ele grava a conferência ao lado.
    with open(arquivo, 'ab') as f:
        f.write(b'aberto no QGIS')
    with open(arquivo + '.sap-conferido.json', 'w', encoding='utf-8') as f:
        json.dump({'repo_id': 'atividade-77', 'sha256': 'do download'}, f)
    with open(arquivo, 'rb') as f:
        agora = hashlib.sha256(f.read()).hexdigest()
    versionamento = banco.pacote()['dados']['atividade']['versionamento']
    assert versionamento['sha256'] != agora, 'a preparação não mudou os bytes'
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    subidas = chamadas('POST', '/api/versionamento/atividade/77/campo', desde)
    assert len(subidas) == 1 and subidas[0]['corpo']['sha256'] == agora, subidas
    assert [c['status'] for c in chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde)] == [200], vistas
    assert banco.pacote()['dados']['atividade']['versionamento']['enviado_sha256'] == agora
    assert not any(m['tipo'] == 'critical' for m in vistas), vistas
    return 'subiu o sha256 de agora ({0}...), não o do pacote'.format(agora[:12])


def _gpkgComEdicaoSoNoWal(destino):
    # O estado de um GeoPackage que o QGIS editou e não consolidou: a edição
    # está só no `-wal`. Copiado enquanto a conexão que editou está aberta (o
    # fechamento faria o checkpoint).
    import shutil
    import sqlite3
    origem = os.path.join(tempfile.mkdtemp(prefix='fumaca_wal_'), 'origem.gpkg')
    conexao = sqlite3.connect(origem)
    conexao.execute('PRAGMA journal_mode=WAL')
    conexao.execute('CREATE TABLE f_teste (dsg_id TEXT PRIMARY KEY, nome TEXT)')
    conexao.execute("INSERT INTO f_teste VALUES ('f-1', 'antes')")
    conexao.commit()
    conexao.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    conexao.execute('PRAGMA wal_autocheckpoint=0')
    conexao.execute("UPDATE f_teste SET nome = 'editado em campo' WHERE dsg_id = 'f-1'")
    conexao.commit()
    for sufixo in ('', '-wal'):
        shutil.copyfile(origem + sufixo, destino + sufixo)
    conexao.close()


def _nomeNoArquivo(conteudo):
    # Abre bytes de GeoPackage SOZINHOS (sem `-wal`) e lê a feição de teste.
    import sqlite3
    caminho = os.path.join(tempfile.mkdtemp(prefix='fumaca_lido_'), 'lido.gpkg')
    with open(caminho, 'wb') as f:
        f.write(conteudo)
    conexao = sqlite3.connect(caminho)
    try:
        return conexao.execute("SELECT nome FROM f_teste WHERE dsg_id = 'f-1'").fetchone()[0]
    finally:
        conexao.close()


@cenario
def item7_finalizar_tipo4_consolida_o_wal():
    """Edição só no -wal: o checkpoint TRUNCATE a leva para o arquivo ANTES de subir; sem ele, ela não chegaria."""
    banco, pasta = _prepararCampo()
    arquivo = os.path.join(pasta, 'atividade-77.gpkg')
    os.remove(arquivo)
    _gpkgComEdicaoSoNoWal(arquivo)
    with open(arquivo, 'rb') as f:
        semGuarda = _nomeNoArquivo(f.read())
    assert semGuarda == 'antes', 'a preparação não deixou a edição só no -wal: {0}'.format(semGuarda)
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    assert chamadas('POST', '/api/versionamento/atividade/77/campo', desde), 'não subiu: {0}'.format(vistas)
    recebido = _nomeNoArquivo(ESTADO.ultimoBinario)
    assert recebido == 'editado em campo', 'a edição do -wal não chegou ao corpo enviado: {0}'.format(recebido)
    wal = arquivo + '-wal'
    assert not os.path.exists(wal) or os.path.getsize(wal) == 0, 'sobrou -wal com conteúdo'
    assert [c['status'] for c in chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde)] == [200], vistas
    return 'só o arquivo: {0!r}; corpo enviado: {1!r}'.format(semGuarda, recebido)


@cenario
def item7_finalizar_tipo4_wal_em_uso_recusa():
    """Arquivo em uso (leitor aberto segura o -wal): recusa com mensagem clara e não sobe nem finaliza."""
    import sqlite3
    banco, pasta = _prepararCampo()
    arquivo = os.path.join(pasta, 'atividade-77.gpkg')
    os.remove(arquivo)
    _gpkgComEdicaoSoNoWal(arquivo)
    leitor = sqlite3.connect(arquivo, isolation_level=None)
    try:
        leitor.execute('BEGIN')
        leitor.execute('SELECT count(*) FROM f_teste').fetchone()
        desde = len(ESTADO.chamadas)
        vistas = _finalizarSAPLocal(banco, pasta)
    finally:
        leitor.execute('COMMIT')
        leitor.close()
    assert not chamadas('POST', '/api/versionamento/atividade/77/campo', desde), 'subiu o arquivo em uso'
    assert not chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde), 'finalizou'
    erros = [m['texto'] for m in vistas if m['tipo'] == 'critical']
    assert erros and 'atividade-77.gpkg-wal' in erros[-1] and 'Nada foi enviado' in erros[-1], vistas
    return erros[-1]


@cenario
def item7_finalizar_tipo4_recusas_do_campo():
    """field_diverged, field_tampered e campo_pendente: mensagem clara e nenhuma finalização calada."""
    vistos = []
    for recusa in ('field_diverged', 'field_tampered'):
        banco, pasta = _prepararCampo()
        ESTADO.campoRecusa = recusa
        desde = len(ESTADO.chamadas)
        vistas = _finalizarSAPLocal(banco, pasta)
        erros = [m['texto'] for m in vistas if m['tipo'] == 'critical']
        assert erros and recusa in erros[-1] and 'Nada mudou no servidor' in erros[-1], (recusa, vistas)
        assert not chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde), \
            '{0}: finalizou com o campo recusado'.format(recusa)
        assert 'enviado_sha256' not in banco.pacote()['dados']['atividade']['versionamento'], recusa
        vistos.append(recusa)
    banco, pasta = _prepararCampo()
    ESTADO.campoPendenteSempre = True
    vistas = _finalizarSAPLocal(banco, pasta)
    erros = [m['texto'] for m in vistas if m['tipo'] == 'critical']
    assert erros and 'campo_pendente' in erros[-1], vistas
    assert not any(m['tipo'] == 'information' for m in vistas), vistas
    vistos.append('campo_pendente')
    return ', '.join(vistos)


def _repositorioDeCampo(caminho, repo='atividade-77'):
    # Um GeoPackage de campo com a parte do repositório do versionamento que a
    # devolução lê (`dsg_meta`, `dsg_seq`, `dsg_revisions`) e uma tabela
    # editável cuja captura faz `dsg_seq` andar, como os gatilhos do serviço
    # (`storage-gpkg`). Criado pelo GDAL, para o QGIS abri-lo pelo `ogr` como
    # abre o de verdade. Fica com 3 versões capturadas, 2 pendentes de registro.
    import sqlite3
    from osgeo import ogr
    ds = ogr.GetDriverByName('GPKG').CreateDataSource(caminho)
    camada = ds.CreateLayer('f_teste', geom_type=ogr.wkbNone)
    for nome in ('dsg_id', 'nome'):
        camada.CreateField(ogr.FieldDefn(nome, ogr.OFTString))
    ds = None
    conexao = sqlite3.connect(caminho, isolation_level=None)
    conexao.executescript('''
        CREATE TABLE dsg_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE dsg_seq (k INTEGER PRIMARY KEY CHECK (k = 1), last INTEGER NOT NULL);
        INSERT INTO dsg_seq VALUES (1, 0);
        CREATE TABLE dsg_revisions (rev_seq INTEGER PRIMARY KEY, id TEXT NOT NULL UNIQUE,
          seq_first INTEGER, seq_last INTEGER);
        CREATE TRIGGER f_teste_captura_insert AFTER INSERT ON f_teste
          BEGIN UPDATE dsg_seq SET last = last + 1 WHERE k = 1; END;
        CREATE TRIGGER f_teste_captura_update AFTER UPDATE ON f_teste
          BEGIN UPDATE dsg_seq SET last = last + 1 WHERE k = 1; END;
        CREATE TRIGGER f_teste_captura_delete AFTER DELETE ON f_teste
          BEGIN UPDATE dsg_seq SET last = last + 1 WHERE k = 1; END;
    ''')
    conexao.executemany('INSERT INTO dsg_meta VALUES (?, ?)', [
        ('family', 'dsg-versioning'), ('repo_id', repo), ('parent_id', 'bloco-20')])
    conexao.execute("INSERT INTO f_teste (dsg_id, nome) VALUES ('f-1', 'do servidor')")
    conexao.execute("INSERT INTO dsg_revisions VALUES (1, 'rev-1', 1, 1)")
    conexao.execute("INSERT INTO f_teste (dsg_id, nome) VALUES ('f-2', 'de campo')")
    conexao.execute("UPDATE f_teste SET nome = 'de campo, editado' WHERE dsg_id = 'f-2'")
    conexao.execute('PRAGMA journal_mode=WAL')
    conexao.close()


def _versoesCapturadas(caminho):
    import sqlite3
    conexao = sqlite3.connect(caminho)
    try:
        return conexao.execute('SELECT last FROM dsg_seq WHERE k = 1').fetchone()[0]
    finally:
        conexao.close()


def _abrirNoQgis(caminho, editar=False):
    # O gerente (ou o operador) reabre o arquivo devolvido no QGIS, pelo `ogr`,
    # e opcionalmente grava uma edição nova nele.
    from qgis.core import QgsFeature, QgsProject, QgsVectorLayer
    camada = QgsVectorLayer(caminho + '|layername=f_teste', 'campo reaberto', 'ogr')
    assert camada.isValid(), 'o QGIS não abriu o arquivo de campo: {0}'.format(camada.error().summary())
    QgsProject.instance().addMapLayer(camada)
    lidas = sorted(f['nome'] for f in camada.getFeatures())
    if editar:
        assert camada.startEditing()
        nova = QgsFeature(camada.fields())
        nova['dsg_id'] = 'f-3'
        nova['nome'] = 'gravada depois da devolução'
        assert camada.addFeature(nova)
        assert camada.commitChanges(), camada.commitErrors()
    QgsProject.instance().removeMapLayer(camada.id())
    APP.processEvents()
    return lidas


def _devolverComConflito(banco, pasta):
    # Primeira finalização: o arquivo volta ao servidor e o merge para num
    # conflito, com a tela fechada. A atividade continua em modo local.
    from SAP_Gerente.modules.versionamento import painel
    ESTADO.conflitosFinalizar = 1
    desde = len(ESTADO.chamadas)
    with mock.patch.object(painel.ConflictDialog, 'exec',
                           lambda d: QtWidgets.QDialog.DialogCode.Rejected):
        vistas = _finalizarSAPLocal(banco, pasta)
    assert [c['status'] for c in chamadas('POST', '/api/versionamento/atividade/77/campo', desde)] == [200], vistas
    assert [c['status'] for c in chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde)] == [409], vistas
    return banco.pacote()['dados']['atividade']['versionamento']


def _campoReal():
    banco, pasta = _prepararCampo()
    arquivo = os.path.join(pasta, 'atividade-77.gpkg')
    os.remove(arquivo)
    _repositorioDeCampo(arquivo)
    return banco, pasta, arquivo


@cenario
def item7_finalizar_tipo4_devolvido_e_reaberto_no_qgis():
    """Devolvido, reaberto no QGIS (bytes mudados, nenhuma edição) e finalizado de novo: compara a identidade do repositório, não sobe de novo e finaliza."""
    import hashlib
    banco, pasta, arquivo = _campoReal()
    versionamento = _devolverComConflito(banco, pasta)
    lidas = _abrirNoQgis(arquivo)
    assert lidas == ['de campo, editado', 'do servidor'], lidas
    with open(arquivo, 'rb') as f:
        agora = hashlib.sha256(f.read()).hexdigest()
    assert agora != versionamento['enviado_sha256'], 'reabrir no QGIS não mudou os bytes: o cenário não exercita nada'
    assert _versoesCapturadas(arquivo) == 3, 'reabrir capturou versão nova'
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    assert not chamadas('POST', '/api/versionamento/atividade/77/campo', desde), 'subiu de novo o arquivo já devolvido'
    assert [c['status'] for c in chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde)] == [200], vistas
    assert not any(m['tipo'] == 'critical' for m in vistas), vistas
    assert versionamento.get('enviado_repo_id') == 'atividade-77' and versionamento.get('enviado_seq') == 3, \
        'a devolução não marcou a identidade e as versões do arquivo: {0}'.format(versionamento)
    return 'bytes mudaram ({0}... -> {1}...), identidade igual, finalizado sem subir de novo'.format(
        versionamento['enviado_sha256'][:10], agora[:10])


@cenario
def item7_finalizar_tipo4_edicao_depois_da_devolucao_recusa():
    """Devolvido e editado depois no QGIS: a edição nova não some calada; recusa com o motivo, sem subir nem finalizar."""
    banco, pasta, arquivo = _campoReal()
    _devolverComConflito(banco, pasta)
    _abrirNoQgis(arquivo, editar=True)
    assert _versoesCapturadas(arquivo) == 4, 'a edição no QGIS não foi capturada'
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    assert not chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde), 'finalizou com edição perdida'
    assert not chamadas('POST', '/api/versionamento/atividade/77/campo', desde), 'tentou subir o arquivo editado'
    erros = [m['texto'] for m in vistas if m['tipo'] == 'critical']
    assert erros and '1 edição(ões) gravada(s) depois de devolvido' in erros[-1] and 'nada foi finalizado' in erros[-1], vistas
    return erros[-1]


@cenario
def item7_finalizar_tipo4_servidor_sem_todas_as_versoes():
    """A resposta da devolução diz menos versões capturadas que o arquivo tem: para sem finalizar, agora e na próxima tentativa."""
    banco, pasta, arquivo = _campoReal()
    ESTADO.pendentesServidor = 1
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    assert [c['status'] for c in chamadas('POST', '/api/versionamento/atividade/77/campo', desde)] == [200], vistas
    assert not chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde), 'finalizou com versão de campo a menos'
    erros = [m['texto'] for m in vistas if m['tipo'] == 'critical']
    assert erros and 'servidor tem 1 versão(ões)' in erros[-1] and 'o arquivo tem 2' in erros[-1], vistas
    desde = len(ESTADO.chamadas)
    vistas = _finalizarSAPLocal(banco, pasta)
    assert not chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde), 'a segunda tentativa finalizou'
    assert not chamadas('POST', '/api/versionamento/atividade/77/campo', desde), 'a segunda tentativa subiu de novo'
    segunda = [m['texto'] for m in vistas if m['tipo'] == 'critical']
    assert segunda and segunda[-1] == erros[-1], vistas
    return erros[-1]


@cenario
def item10_criar_integracao_do_lote():
    """Criar Integração do Lote: POST /api/versionamento/lote/:id/integracao com subfase_id e dado_producao_id opcional."""
    w = abrir('Criar Integração do Lote')
    w.lotesCb.setCurrentIndex(w.lotesCb.findData(10))
    APP.processEvents()
    subfases = [d for _, d in itens(w.subfasesCb)]
    assert subfases == [None, 31, 32], 'subfases do lote 10: {0}'.format(subfases)
    w.subfasesCb.setCurrentIndex(w.subfasesCb.findData(32))
    desde = len(ESTADO.chamadas)
    inicio = len(MENSAGENS)
    w.okBtn.click()
    APP.processEvents()
    w.basesCb.setCurrentIndex(w.basesCb.findData(4))
    w.okBtn.click()
    APP.processEvents()
    posts = chamadas('POST', '/api/versionamento/lote/', desde)
    assert [p['caminho'] for p in posts] == ['/api/versionamento/lote/10/integracao'] * 2, posts
    assert posts[0]['corpo'] == {'subfase_id': 32}, posts[0]['corpo']
    assert posts[1]['corpo'] == {'subfase_id': 32, 'dado_producao_id': 4}, posts[1]['corpo']
    assert any('atividade 901' in t for t in textos('information', inicio)), textos(None, inicio)
    w.close()
    return 'corpos {0} e {1}'.format(posts[0]['corpo'], posts[1]['corpo'])


@cenario
def item10_criar_integracao_do_bloco():
    """Criar Integração do Bloco: POST /api/versionamento/bloco/:id/integracao com subfase_id (do lote do bloco) e dado_producao_id opcional."""
    w = abrir('Criar Integração do Bloco')
    w.blocosCb.setCurrentIndex(w.blocosCb.findData(20))
    APP.processEvents()
    subfases = [d for _, d in itens(w.subfasesCb)]
    assert subfases == [None, 31, 32], 'subfases do lote do bloco 20: {0}'.format(subfases)
    w.subfasesCb.setCurrentIndex(w.subfasesCb.findData(32))
    desde = len(ESTADO.chamadas)
    inicio = len(MENSAGENS)
    w.okBtn.click()
    APP.processEvents()
    w.basesCb.setCurrentIndex(w.basesCb.findData(4))
    w.okBtn.click()
    APP.processEvents()
    posts = [p for p in chamadas('POST', '/api/versionamento/bloco/', desde)]
    assert [p['caminho'] for p in posts] == ['/api/versionamento/bloco/20/integracao'] * 2, posts
    assert posts[0]['corpo'] == {'subfase_id': 32}, posts[0]['corpo']
    assert posts[1]['corpo'] == {'subfase_id': 32, 'dado_producao_id': 4}, posts[1]['corpo']
    assert any('atividade 902' in t for t in textos('information', inicio)), textos(None, inicio)
    w.close()
    return 'corpos {0} e {1}'.format(posts[0]['corpo'], posts[1]['corpo'])


@cenario
def defeito_formulario_conexao_tipo1():
    """Configurações de Conexão: o tipo 1 'Não controlado' edita e cria sem banco (configuracao_producao nula)."""
    w = abrir('Configurações de Conexão')
    linhas = [w.getRowData(i) for i in range(w.tableWidget.rowCount())]
    alvo = [i for i, l in enumerate(linhas) if l['tipo_dado_producao_id'] == 1]
    assert alvo, 'o tipo 1 não está na lista: {0}'.format(linhas)
    desde = len(ESTADO.chamadas)
    inicio = len(MENSAGENS)
    indice = w.tableWidget.model().index(alvo[0], 1)
    w.handleEditBtn(indice)
    form = w.addProductionDataFormDlg
    APP.processEvents()
    assert not form.ipDBLe.isVisible() and not form.repoCb.isVisible(), 'campos de banco no tipo 1'
    with mock.patch('SAP_Gerente.widgets.addProductionDataForm.TestDatabase') as teste:
        form.okBtn.click()
        APP.processEvents()
        assert not teste.called, 'testou conexão psycopg2 no tipo 1'
    puts = chamadas('PUT', '/api/producao/dado_producao', desde)
    assert puts and puts[-1]['corpo'] == {'dado_producao': [
        {'id': 5, 'configuracao_producao': None, 'tipo_dado_producao_id': 1}]}, puts
    novo = type(form)(controller, sap, qgisCtrl)
    novo.show()
    novo.typeProductionDataCb.setCurrentIndex(novo.typeProductionDataCb.findData(1))
    APP.processEvents()
    novo.okBtn.click()
    APP.processEvents()
    posts = chamadas('POST', '/api/producao/dado_producao', desde)
    assert posts and posts[-1]['corpo'] == {'dado_producao': [
        {'configuracao_producao': None, 'tipo_dado_producao_id': 1}]}, posts
    assert not textos('critical', inicio), textos('critical', inicio)
    w.close()
    return 'editado e criado: {0}'.format(posts[-1]['corpo'])


@cenario
def defeito_dock_widget_v2_show_info():
    """DockWidgetV2.showInfo usava `message` indefinida (NameError)."""
    from SAP_Gerente.widgets.dockWidgetV2 import DockWidgetV2
    caixa = mock.MagicMock()
    alvo = mock.MagicMock()
    alvo.messageFactory.createMessage.return_value = caixa
    DockWidgetV2.showInfo(alvo, 'Aviso', 'texto de teste')
    caixa.show.assert_called_once_with(alvo, 'Aviso', 'texto de teste')
    return 'mostrou o texto'


@cenario
def defeito_qgis_api_base64():
    """QgisApi.setProjectVariable/getProjectVariable usavam `base64` sem importar."""
    from SAP_Gerente.modules.qgis.api.qgisApi import QgisApi
    api = QgisApi()
    api.setProjectVariable('sap_gerente_fumaca', 'valor çá')
    lido = api.getProjectVariable('sap_gerente_fumaca')
    assert lido == 'valor çá', lido
    return 'ida e volta: {0}'.format(lido)


def _maquinaDeEstado(nome, campo, valor):
    w = abrir(nome)
    getattr(w, campo).setText(valor)
    inicio = len(MENSAGENS)
    w.okBtn.click()
    APP.processEvents()
    w.close()
    return MENSAGENS[inicio:]


@cenario
def item8_pausar_mostra_revogacao_que_falhou():
    """Pausar: mostra a mensagem do servidor e a revogação ok:false, como erro."""
    vistas = _maquinaDeEstado('Pausar Atividades em Execução', 'activityIdLe', '5')
    texto = '\n'.join(m['texto'] for m in vistas)
    assert 'Atividade pausada com sucesso' in texto, vistas
    assert 'FALHOU' in texto and 'O banco de produção não respondeu' in texto, vistas
    assert 'continua aberto' in texto, vistas
    assert any(m['tipo'] == 'critical' for m in vistas), 'a falha da revogação não saiu como erro'
    assert 'Executado com sucesso!' not in texto, vistas
    return texto.replace('\n', ' | ')


@cenario
def item8_reiniciar_e_voltar_mostram_a_mensagem_do_servidor():
    """Reiniciar e Retornar: a mensagem é a do servidor (e a revogação ok:true quando vem)."""
    vistas = _maquinaDeEstado('Reiniciar Atividades em Execução ou Pausadas', 'activityIdLe', '5')
    texto = '\n'.join(m['texto'] for m in vistas)
    assert 'Atividade reiniciada com sucesso' in texto, vistas
    vistas = _maquinaDeEstado('Retornar Atividades para Etapa Anterior', 'activityIdLe', '6')
    texto2 = '\n'.join(m['texto'] for m in vistas)
    assert 'voltou para a etapa anterior' in texto2 and 'revogado em 2' in texto2, vistas
    return (texto + ' | ' + texto2).replace('\n', ' | ')


@cenario
def item6_remover_feicoes_nao_depende_de_postgres():
    """Remover Feições em Área: as ferramentas editam pelo buffer da camada, sem `postgres`."""
    pasta = os.path.join(PLUGIN, 'modules', 'qgis', 'mapTools')
    achados = []
    for arquivo in ('removeByClip.py', 'removeByIntersect.py'):
        with open(os.path.join(pasta, arquivo), encoding='utf-8') as f:
            conteudo = f.read().lower()
        for termo in ('postgres', 'psycopg2', 'dataprovider().uri', 'providertype'):
            if termo in conteudo:
                achados.append((arquivo, termo))
    assert not achados, achados
    return 'sem dependência de provedor'


for funcao in CENARIOS:
    inicio = len(MENSAGENS)
    try:
        detalhe = funcao()
        RESULTADO['cenarios'].append({'nome': funcao.__name__, 'ok': True, 'detalhe': detalhe,
                                      'descricao': funcao.__doc__})
    except Exception as e:
        RESULTADO['cenarios'].append({
            'nome': funcao.__name__, 'ok': False, 'descricao': funcao.__doc__,
            'detalhe': '{0}: {1}'.format(type(e).__name__, e),
            'traceback': traceback.format_exc(limit=3),
        })
    for w in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(w, QtWidgets.QDialog) and w.isVisible():
            w.close()
    QtWidgets.QApplication.restoreOverrideCursor()
    APP.processEvents()

RESULTADO['chamadas'] = ESTADO.chamadas
RESULTADO['plugin'] = 'worktree' if PLUGIN != PLUGIN_PADRAO else 'atual'
falhasAcoes = {k: v for k, v in RESULTADO['acoes'].items() if v != 'ok'}
falhasCenarios = [c['nome'] for c in RESULTADO['cenarios'] if not c['ok']]
RESULTADO['resumo'] = {
    'acoes_total': len(RESULTADO['acoes']),
    'acoes_com_excecao': sorted(falhasAcoes),
    'cenarios_total': len(RESULTADO['cenarios']),
    'cenarios_reprovados': falhasCenarios,
    'chamadas': len(ESTADO.chamadas),
    'chamadas_rota_padrao_do_falso': sorted({
        '{0} {1}'.format(c['metodo'], c['caminho']) for c in ESTADO.chamadas if c['padrao']
    }),
}
with open(ARGS.saida, 'w', encoding='utf-8') as f:
    json.dump(RESULTADO, f, ensure_ascii=False, indent=1, default=str)

print(json.dumps(RESULTADO['resumo'], ensure_ascii=False, indent=1))
for c in RESULTADO['cenarios']:
    print('{0} {1}: {2}'.format('OK  ' if c['ok'] else 'FALHA', c['nome'], c['detalhe']))
SERVIDOR.shutdown()
APP.exitQgis()
sys.exit(1 if (falhasAcoes or falhasCenarios) else 0)
