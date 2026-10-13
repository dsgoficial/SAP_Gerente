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


@cenario
def item7_sap_local_recusa_base_versionada():
    """Configurar SAP Local: tipo 4 mostra o aviso e NÃO inicia o modo local."""
    w = abrir('Configurar SAP Local')
    w.dbCb.addItem('banco local de teste', json.dumps({
        'alias': 'teste', 'database': 'x', 'host': 'x', 'port': '0', 'username': 'x', 'password': 'x'
    }))
    w.dbCb.setCurrentIndex(w.dbCb.count() - 1)
    w.activityIdLe.setText('77')
    inicio = len(MENSAGENS)
    desde = len(ESTADO.chamadas)
    w.okBtn.click()
    APP.processEvents()
    QtWidgets.QApplication.restoreOverrideCursor()
    assert not chamadas('PUT', '/api/gerencia_producao/iniciar_modo_local', desde), \
        'iniciou o modo local para a base versionada'
    assert any('GeoPackage de campo' in t for t in textos(None, inicio)), textos(None, inicio)
    w.close()
    return 'aviso mostrado, nada mutado'


@cenario
def item7_finalizar_sap_local_recusa_base_versionada():
    """Finalizar SAP Local: pacote tipo 4 no banco local não chama finalizar_modo_local."""
    from servidor_falso import pacote

    class PgFalso:
        def __init__(self, *args):
            pass

        def execute(self, query, params):
            return [(77, '2026-10-13 08:00', '2026-10-13 12:00', 'u-1', json.dumps(pacote(77, 4)))]

    desde = len(ESTADO.chamadas)
    erro = None
    with mock.patch.object(moduloSapHttp, 'Postgresql', PgFalso):
        try:
            sap.endLocalMode({'database': 'x', 'username': 'x', 'host': 'x', 'port': '0', 'password': 'x'})
        except Exception as e:
            erro = str(e)
    assert not chamadas('PUT', '/api/gerencia_producao/finalizar_modo_local', desde), \
        'finalizou o modo local da base versionada'
    assert erro and 'GeoPackage de campo' in erro, erro
    return erro


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
