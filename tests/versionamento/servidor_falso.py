# -*- coding: utf-8 -*-
# Servidor FALSO do SAP 3.0 para a fumaça do SAP Gerente: responde as rotas que
# o painel chama ao abrir cada ação e as rotas novas do versionamento (contrato
# do versionamento no SAP 3.0, seção 5), e REGISTRA toda chamada (método,
# caminho, corpo) para o conferidor comparar com o roteador do servidor Node.
#
# Só escuta em 127.0.0.1 e numa porta livre escolhida pelo sistema. Os dados são
# fictícios. Rota GET não modelada responde `dados: []` e fica marcada como
# `padrao` no registro: quem diz se ela existe no servidor é o conferidor.

import hashlib
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


def envelope(dados=None, message='ok'):
    return {'version': '3.32.0', 'success': True, 'message': message, 'dados': dados}


BANCO_DADOS = [
    {'id': 1, 'tipo_dado_producao_id': 2, 'tipo_dado_producao': 'PostGIS com controle de permissão',
     'nome': 'banco_a', 'lote_status_execucao_id': 2},
    {'id': 2, 'tipo_dado_producao_id': 3, 'tipo_dado_producao': 'PostGIS',
     'nome': 'banco_b', 'lote_status_execucao_id': 2},
    # Tipo 4: sem banco. O servidor não sabe ler `configuracao_producao` como
    # alvo PostgreSQL e devolve `nome` nulo (o que `getBancoDados` faz hoje).
    {'id': 4, 'tipo_dado_producao_id': 4, 'tipo_dado_producao': 'Base versionada',
     'nome': None, 'lote_status_execucao_id': 1},
]

DADO_PRODUCAO = [
    {'id': 1, 'tipo_dado_producao_id': 2, 'tipo_dado_producao': 'PostGIS com controle de permissão',
     'configuracao_producao': 'servidor-ficticio:0/banco_a', 'lote_status_execucao_id': 2},
    {'id': 2, 'tipo_dado_producao_id': 3, 'tipo_dado_producao': 'PostGIS',
     'configuracao_producao': 'servidor-ficticio:0/banco_b', 'lote_status_execucao_id': 2},
    {'id': 4, 'tipo_dado_producao_id': 4, 'tipo_dado_producao': 'Base versionada',
     'configuracao_producao': 'base-edgv-1', 'lote_status_execucao_id': 1},
    # Tipo 1 'Não controlado': o SAP só aponta, `configuracao_producao` nula
    # (a coluna é anulável por causa dele, `trabalho_schema.js`).
    {'id': 5, 'tipo_dado_producao_id': 1, 'tipo_dado_producao': 'Não controlado',
     'configuracao_producao': None, 'lote_status_execucao_id': 2},
]

SUBFASES = [
    {'linha_producao_id': 1, 'linha_producao': 'Carta topográfica', 'fase_id': 1, 'fase': 'Edição',
     'subfase_id': 31, 'subfase': 'Edição da base', 'lote_id': 10, 'lote': 'Lote 10'},
    {'linha_producao_id': 1, 'linha_producao': 'Carta topográfica', 'fase_id': 2, 'fase': 'Integração',
     'subfase_id': 32, 'subfase': 'Integração na base', 'lote_id': 10, 'lote': 'Lote 10'},
    {'linha_producao_id': 1, 'linha_producao': 'Carta topográfica', 'fase_id': 1, 'fase': 'Edição',
     'subfase_id': 41, 'subfase': 'Edição de outro lote', 'lote_id': 11, 'lote': 'Lote 11'},
]

# O arquivo de campo do clone da atividade (contrato 9.1): 3 MiB, para o
# download em fluxo passar por vários pedaços.
ARQUIVO_CAMPO = b'SQLite format 3\x00' + bytes(range(256)) * (3 * 4096)

PACOTE_BASE = {
    'usuario_uuid': 'u-1', 'login': 'operador', 'usuario_nome': 'Operador',
    'atividade': {
        'id': 0, 'epsg': '31982', 'lote': 'Lote 10', 'bloco': 'Bloco 20',
        'geom': 'SRID=4326;POLYGON((0 0,0 1,1 1,1 0,0 0))',
        'camadas': [], 'fme': [], 'insumos': [],
    },
}


class Estado:
    def __init__(self):
        self.chamadas = []
        self.lock = threading.Lock()
        self.reposProibido = False
        self.leiturasJob = {}
        self.leiturasAteFim = 3
        # Campo da base versionada (contrato 9.2).
        self.iniciadas = set()
        self.emCampo = set()
        self.campoRecusa = None
        self.campoRecebido = {}
        self.conflitosFinalizar = 0
        self.campoPendenteSempre = False
        self.sessaoResolvida = False
        # Os bytes do último corpo binário, para o cenário do WAL abrir o
        # arquivo que de fato chegou.
        self.ultimoBinario = None


def pacote(atividadeId, tipo, iniciada=False):
    dados = json.loads(json.dumps(PACOTE_BASE))
    dados['atividade']['id'] = atividadeId
    if tipo == 4:
        # Contrato, seção 5: sem `login_info` e sem `configuracao_producao`, e
        # com `versionamento`, que o servidor põe em `dados.atividade`
        # (`ciclo_atividade.completarPacote`). O `repo_id` é o do clone da
        # atividade, que só existe depois do `inicia` (aqui, do
        # `iniciar_modo_local`): antes dele, nulo.
        dados['atividade']['dado_producao'] = {'tipo_dado_producao_id': 4}
        dados['atividade']['versionamento'] = {
            'repo_id': 'atividade-{0}'.format(atividadeId) if iniciada else None,
            'servico': '/api/versionamento/servico',
            'papel': 'atividade',
            'datasets': [{'schema': 'edgv', 'nome': 'cobter_area_construida_a',
                          'dataset': 'edgv.cobter_area_construida_a'}],
        }
    else:
        dados['atividade']['dado_producao'] = {
            'tipo_dado_producao_id': tipo,
            'configuracao_producao': 'servidor-ficticio:0/banco_a',
        }
    return envelope(dados, 'Atividade retornada')


def rotas(estado):
    def job(m, corpo):
        jobId = m.group(1)
        n = estado.leiturasJob.get(jobId, 0) + 1
        estado.leiturasJob[jobId] = n
        if n < estado.leiturasAteFim:
            return 200, {'id': jobId, 'operation': 'clone', 'state': 'running',
                         'progress': {'completed': n * 10, 'phase': 'Copiando feições'},
                         'error': None, 'error_code': None, 'cancel_requested': 0}
        return 200, {'id': jobId, 'operation': 'clone', 'state': 'succeeded',
                     'progress': {'completed': 30, 'phase': 'Concluído'}, 'result': {},
                     'error': None, 'error_code': None, 'cancel_requested': 0}

    def repos(m, corpo):
        if estado.reposProibido:
            return 403, {'success': False, 'message': 'Rota do serviço não liberada para o perfil.'}
        return 200, {'repositories': [
            {'id': 'base-edgv-1', 'label': 'Base EDGV', 'backend': 'postgis', 'parent_id': None},
            {'id': 'lote-10', 'label': 'Lote 10', 'backend': 'postgis', 'parent_id': 'base-edgv-1'},
        ]}

    def recusa(status, message, codigo=None, dados=None):
        corpo = {'version': '3.33.0', 'success': False, 'message': message, 'dados': dados, 'error': None}
        if codigo:
            corpo['codigo'] = codigo
        return status, corpo

    def iniciarModoLocal(m, corpo):
        atividade = (corpo or {}).get('atividade_id')
        estado.iniciadas.add(atividade)
        if atividade == 77:
            estado.emCampo.add(atividade)
        return 200, envelope(None, 'Atividade iniciada em modo local com sucesso')

    def baixarCampo(m, corpo):
        atividade = int(m.group(1))
        if atividade not in estado.emCampo:
            return recusa(409, 'A atividade não está em campo.', 'nao_em_campo')
        return 200, ARQUIVO_CAMPO, {
            'Content-Type': 'application/geopackage+sqlite3',
            'Content-Disposition': 'attachment; filename="atividade-{0}.gpkg"'.format(atividade),
            'X-Dsg-Head': '5',
        }

    def subirCampo(m, corpo):
        atividade = int(m.group(1))
        if not (isinstance(corpo, dict) and corpo.get('binario')):
            return recusa(400, 'O corpo deve ser o arquivo de campo.')
        if atividade not in estado.emCampo:
            return recusa(409, 'O clone desta atividade não está em campo.', 'nao_em_campo')
        if estado.campoRecusa:
            return recusa(409, 'Recusa do serviço: {0}'.format(estado.campoRecusa), estado.campoRecusa)
        estado.campoRecebido[atividade] = corpo
        if not estado.campoPendenteSempre:
            estado.emCampo.discard(atividade)
        return 200, envelope({'repo_id': 'atividade-{0}'.format(atividade), 'head': 5,
                              'pending_versions': 2}, 'Arquivo de campo recebido')

    def finalizarModoLocal(m, corpo):
        atividade = (corpo or {}).get('atividade_id')
        if atividade in estado.emCampo:
            return recusa(409, 'O arquivo de campo ainda não voltou.', 'campo_pendente')
        if atividade == 77 and estado.conflitosFinalizar > 0:
            estado.conflitosFinalizar -= 1
            return recusa(
                409,
                'Há 1 conflito(s) entre o seu trabalho e o que já foi integrado: resolva-os pela '
                'sessão sessao-1 e chame de novo.',
                'conflito_versionamento',
                {'sessao_id': 'sessao-1', 'repo_id': 'bloco-20', 'conflitos': 1}
            )
        return 200, envelope(None, 'Atividade finalizada em modo local com sucesso')

    def itensSessao(m, corpo):
        if estado.sessaoResolvida:
            return 200, {'items': [], 'next': None, 'counts': {'conflict': 0, 'resolved': 1}}
        return 200, {'items': [{
            'dataset': 'edgv.cobter_area_construida_a', 'feature_id': 'f-1', 'status': 'conflict',
            'conflicts': [{'field': 'nome', 'reason': 'both_changed'}],
            'base': {'nome': 'A'}, 'ours': {'nome': 'B'}, 'theirs': {'nome': 'C'}, 'result': None,
        }], 'next': None, 'counts': {'conflict': 1}}

    def resolverSessao(m, corpo):
        estado.sessaoResolvida = True
        return 200, {'feature_id': (corpo or {}).get('id'), 'status': 'resolved'}

    G, P, U, D = 'GET', 'POST', 'PUT', 'DELETE'
    return [
        (G, r'/api/producao/subfases', lambda m, c: (200, envelope(SUBFASES))),
        (P, r'/api/versionamento/lote/(\d+)/integracao', lambda m, c: (201, envelope(
            {'atividade_id': 901, 'unidade_trabalho_id': 801, 'etapa_id': 701},
            'Atividade de integração do lote criada'))),
        (P, r'/api/versionamento/bloco/(\d+)/integracao', lambda m, c: (201, envelope(
            {'atividade_id': 902, 'unidade_trabalho_id': 802, 'etapa_id': 702,
             'geometria': 'uniao', 'unidades_de_origem': 3},
            'Atividade de integração do bloco criada'))),
        (G, r'/api/versionamento/atividade/(\d+)/campo', baixarCampo),
        (P, r'/api/versionamento/atividade/(\d+)/campo', subirCampo),
        (G, r'/api/versionamento/servico/repos/([^/]+)/sessions/([^/]+)/items', itensSessao),
        (P, r'/api/versionamento/servico/repos/([^/]+)/sessions/([^/]+)/resolve', resolverSessao),
        (G, r'/api/producao/banco_dados', lambda m, c: (200, envelope(BANCO_DADOS))),
        (G, r'/api/producao/dado_producao', lambda m, c: (200, envelope(DADO_PRODUCAO))),
        (P, r'/api/producao/dado_producao', lambda m, c: (201, envelope(None, 'Dado de produção criado'))),
        (G, r'/api/producao/tipo_dado_producao', lambda m, c: (200, envelope([
            {'code': 1, 'nome': 'Não controlado'},
            {'code': 2, 'nome': 'PostGIS com controle de permissão'},
            {'code': 3, 'nome': 'PostGIS'},
            {'code': 4, 'nome': 'Base versionada'},
        ]))),
        (G, r'/api/producao/tipo_etapa', lambda m, c: (200, envelope([
            {'code': 1, 'nome': 'Execução'}, {'code': 2, 'nome': 'Revisão'},
            {'code': 3, 'nome': 'Correção'}, {'code': 4, 'nome': 'Revisão/Correção'},
            {'code': 5, 'nome': 'Revisão final'}, {'code': 6, 'nome': 'Integração'},
        ]))),
        # Padrão 4 FICTÍCIO: prova que a lista do "Criar Etapas Padrão" é a do
        # servidor, e não a fixa no plugin.
        (G, r'/api/producao/tipo_controle_qualidade', lambda m, c: (200, envelope([
            {'code': 1, 'nome': 'Sem controle de qualidade nas subfases'},
            {'code': 2, 'nome': 'Uma Revisão/Correção em todas as subfases'},
            {'code': 3, 'nome': 'Uma Revisão em todas as subfases'},
            {'code': 4, 'nome': 'Padrão de teste com Integração'},
        ]))),
        (G, r'/api/producao/status', lambda m, c: (200, envelope([
            {'code': 1, 'nome': 'Não iniciado'}, {'code': 2, 'nome': 'Em execução'},
            {'code': 3, 'nome': 'Concluído'}, {'code': 4, 'nome': 'Concluído parcialmente'},
            {'code': 5, 'nome': 'Pausado'},
        ]))),
        (G, r'/api/gerencia_producao/lotes', lambda m, c: (200, envelope([
            {'id': 10, 'nome': 'Lote 10', 'projeto': 'Projeto X', 'projeto_id': 1,
             'status_execucao_id': 2, 'ativo': True},
        ]))),
        (G, r'/api/producao/bloco', lambda m, c: (200, envelope([
            {'id': 20, 'nome': 'Bloco 20', 'lote_id': 10, 'lote': 'Lote 10', 'prioridade': 1,
             'status_execucao_id': 2, 'status_execucao': 'Em execução'},
        ]))),
        (G, r'/api/producao/configuracao/camadas', lambda m, c: (200, envelope([
            {'id': 1, 'schema': 'edgv', 'nome': 'ja_importada_p'},
        ]))),
        (P, r'/api/producao/configuracao/camadas', lambda m, c: (201, envelope(None, 'Camadas importadas com sucesso'))),
        (G, r'/api/gerencia_producao/versao_qgis', lambda m, c: (200, envelope({'versao_minima': '4.0.0'}))),
        (G, r'/api/gerencia_producao/plugin_path', lambda m, c: (200, envelope({'path': 'repositorio-ficticio'}))),
        (G, r'/api/gerencia_producao/habilitacao', lambda m, c: (200, envelope([
            {'id': 1, 'nome': 'Habilitação de teste'},
        ]))),
        (G, r'/api/gerencia_producao/habilitacao_usuario', lambda m, c: (200, envelope([
            {'id': 1, 'usuario_uuid': 'u-1', 'usuario': 'Sd Operador', 'habilitacao_id': 1},
        ]))),
        # Máquina de estado: a revogação volta no envelope (gerencia_producao_route).
        (P, r'/api/gerencia_producao/atividade/pausar', lambda m, c: (201, envelope(
            {'revogacao': {
                'ok': False, 'revogadas': 0,
                'falhas': [{'atividade_id': 5, 'mensagem': 'O banco de produção não respondeu'}],
                'providencia': 'A operação foi concluída e as atividades foram pausadas. O acesso '
                               'ao banco de produção das atividades acima continua aberto até que '
                               'um gerente o revogue.'}},
            'Atividade pausada com sucesso'))),
        (P, r'/api/gerencia_producao/atividade/reiniciar', lambda m, c: (201, envelope(
            None, 'Atividade reiniciada com sucesso'))),
        (P, r'/api/gerencia_producao/atividade/voltar', lambda m, c: (201, envelope(
            {'revogacao': {'ok': True, 'revogadas': 2}},
            'Atividade voltou para a etapa anterior com sucesso'))),
        (G, r'/api/gerencia_producao/atividade/(77)', lambda m, c: (200, pacote(77, 4, 77 in estado.iniciadas))),
        (G, r'/api/gerencia_producao/atividade/(78)', lambda m, c: (200, pacote(78, 2))),
        (U, r'/api/gerencia_producao/iniciar_modo_local', iniciarModoLocal),
        (U, r'/api/gerencia_producao/finalizar_modo_local', finalizarModoLocal),
        # Versionamento: ciclo (SAP) e repasse (serviço, sem envelope).
        (P, r'/api/versionamento/lote/(\d+)', lambda m, c: (202, envelope(
            {'job_id': 'job-lote-{0}'.format(m.group(1)),
             'repositorio': {'id': 1, 'repo_id': 'lote-{0}'.format(m.group(1)), 'estado': 'vivo'}},
            'Versionamento do lote iniciado'))),
        (P, r'/api/versionamento/bloco/(\d+)', lambda m, c: (202, envelope(
            {'job_id': 'job-bloco-{0}'.format(m.group(1))}, 'Versionamento do bloco iniciado'))),
        (G, r'/api/versionamento/repositorios', lambda m, c: (200, envelope([
            {'id': 1, 'repo_id': 'lote-10', 'papel': 'lote', 'pai_id': None, 'dado_producao_id': 4,
             'lote_id': 10, 'bloco_id': None, 'atividade_id': None, 'estado': 'vivo',
             'job_id': 'job-lote-10',
             # A forma de `versionamento_ctrl.listar`: só a linha viva ainda sem
             # `repo_id` traz a tarefa, com as chaves em português.
             'tarefa': {'id': 'job-lote-10', 'estado': 'running',
                        'progresso': {'completed': 20, 'phase': 'Copiando feições'}, 'erro': None}},
            {'id': 2, 'repo_id': 'bloco-20', 'papel': 'bloco', 'pai_id': 1, 'dado_producao_id': 4,
             'lote_id': 10, 'bloco_id': 20, 'atividade_id': None, 'estado': 'vivo',
             'job_id': 'job-bloco-20', 'tarefa': None},
        ]))),
        (P, r'/api/versionamento/repositorio/(\d+)/descartar', lambda m, c: (201, envelope(
            None, 'Repositório descartado'))),
        (G, r'/api/versionamento/servico/repos', repos),
        (G, r'/api/versionamento/servico/repos/([^/]+)/datasets', lambda m, c: (200, {'datasets': [
            {'name': 'edgv.cobter_area_construida_a', 'fields': [], 'geometry_type': 'MultiPolygon', 'srid': 4674},
            {'name': 'edgv.elemnat_curva_nivel_l', 'fields': [], 'geometry_type': 'MultiLineString', 'srid': 4674},
            {'name': 'edgv.ja_importada_p', 'fields': [], 'geometry_type': 'MultiPoint', 'srid': 4674},
        ]})),
        (G, r'/api/versionamento/servico/jobs/([^/]+)', job),
    ]


class Manipulador(BaseHTTPRequestHandler):
    estado = None
    tabela = None

    def log_message(self, *args):
        pass

    def _responder(self, metodo):
        partes = urlsplit(self.path)
        tamanho = int(self.headers.get('Content-Length') or 0)
        bruto = self.rfile.read(tamanho) if tamanho else b''
        tipo = (self.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        if bruto and tipo and tipo != 'application/json':
            # Corpo binário (o arquivo de campo): registrado pelo tamanho e
            # pelo SHA-256, nunca inteiro no registro.
            corpo = {'binario': len(bruto), 'sha256': hashlib.sha256(bruto).hexdigest(),
                     'content_type': tipo}
            self.estado.ultimoBinario = bruto
        else:
            try:
                corpo = json.loads(bruto.decode('utf-8')) if bruto else None
            except ValueError:
                corpo = bruto.decode('utf-8', 'replace')
        if partes.path == '/__cenario':
            for chave, valor in (corpo or {}).items():
                setattr(self.estado, chave, valor)
            return self._enviar(200, {'ok': True})
        status, resposta, padrao, cabecalhos = None, None, False, None
        for m_, padraoRota, funcao in self.tabela:
            if m_ != metodo:
                continue
            achou = re.fullmatch(padraoRota, partes.path)
            if achou:
                saida = funcao(achou, corpo)
                status, resposta = saida[0], saida[1]
                cabecalhos = saida[2] if len(saida) > 2 else None
                break
        if status is None:
            padrao = True
            if metodo == 'GET':
                status, resposta = 200, envelope([])
            else:
                status, resposta = 201, envelope(None, 'ok (falso)')
        with self.estado.lock:
            self.estado.chamadas.append({
                'metodo': metodo, 'caminho': partes.path, 'query': partes.query,
                'corpo': corpo, 'status': status, 'padrao': padrao,
                'autorizacao': bool(self.headers.get('authorization')),
                'bearer': (self.headers.get('authorization') or '').startswith('Bearer '),
            })
        self._enviar(status, resposta, cabecalhos)

    def _enviar(self, status, resposta, cabecalhos=None):
        binario = isinstance(resposta, bytes)
        dados = resposta if binario else json.dumps(resposta).encode('utf-8')
        self.send_response(status)
        if not binario:
            self.send_header('Content-Type', 'application/json; charset=utf-8')
        for chave, valor in (cabecalhos or {}).items():
            self.send_header(chave, valor)
        self.send_header('Content-Length', str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        self._responder('GET')

    def do_POST(self):
        self._responder('POST')

    def do_PUT(self):
        self._responder('PUT')

    def do_DELETE(self):
        self._responder('DELETE')


def iniciar():
    estado = Estado()
    manipulador = type('ManipuladorFalso', (Manipulador,), {
        'estado': estado, 'tabela': rotas(estado)
    })
    servidor = ThreadingHTTPServer(('127.0.0.1', 0), manipulador)
    linha = threading.Thread(target=servidor.serve_forever, daemon=True)
    linha.start()
    base = 'http://127.0.0.1:{0}'.format(servidor.server_address[1])
    return servidor, estado, base
