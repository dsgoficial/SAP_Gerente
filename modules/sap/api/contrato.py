# Constantes do contrato do SAP 3.0 que o plugin inteiro usa. Módulo sem
# dependência nenhuma, para os widgets importarem sem puxar o cliente HTTP.
#
# O plugin fala SÓ com o SAP 3.0: sem alias e sem tradução de nome antigo,
# porque o validador do servidor é ESTRITO (chave desconhecida no corpo vira 400).

import json

# dominio.tipo_status_execucao do SAP 3.0 (lote, projeto, bloco). "Encerrado" é
# 3 e 4; pausado (5) NÃO é encerrado. O "Previsto / Em Execução" (code 1 de
# dominio.status) do SAP 2.3.5 corresponde a tudo o que não está encerrado.
STATUS_NAO_INICIADO = 1
STATUS_EM_EXECUCAO = 2
STATUS_ENCERRADO = (3, 4)

# dominio.tipo_perfil do SAP 3.0, e o nome_abrev dos módulos na chave de `perfis`
# da resposta do login.
PERFIL_CONSULTA = 1
PERFIL_GERENTE = 3
MODULO_PRODUCAO = 'producao'
MODULO_ACERVO = 'acervo'

# Marca das funções cuja rota NÃO existe no SAP 3.0. O script de prova do porte
# conta as funções que chamam `naoDisponivel` como desabilitadas de propósito.
NAO_DISPONIVEL_SAP3 = 'Não disponível no SAP 3.0: {0}'


def naoDisponivel(motivo):
    raise Exception(NAO_DISPONIVEL_SAP3.format(motivo))


def emAndamento(item, chave='status_execucao_id'):
    return item.get(chave) not in STATUS_ENCERRADO


# dominio.tipo_dado_producao do SAP 3.0. O tipo 4 'Base versionada' é a base no
# serviço de versionamento: `configuracao_producao` guarda o `repo_id` da BASE,
# sem servidor, porta nem credencial (contrato do versionamento, seção 4).
# O tipo 1 'Não controlado' é dado que o SAP só aponta: `configuracao_producao`
# é opcional (nulo) e não há banco a testar.
TIPO_DADO_NAO_CONTROLADO = 1
TIPO_DADO_POSTGIS_COM_PERMISSAO = 2
TIPO_DADO_POSTGIS = 3
TIPO_DADO_BASE_VERSIONADA = 4
# Só estes dois são banco PostgreSQL: revogar permissão só faz sentido neles.
TIPOS_COM_BANCO = (TIPO_DADO_POSTGIS_COM_PERMISSAO, TIPO_DADO_POSTGIS)
# Gerar unidade de trabalho aceita também a base versionada.
TIPOS_GERAR_UT = TIPOS_COM_BANCO + (TIPO_DADO_BASE_VERSIONADA,)

# Pacote de campo da base versionada (contrato, seções 9.1, 9.2 e 9.4): no modo
# local do tipo 4 o Gerente baixa o clone da atividade em GeoPackage, que vai a
# campo ao lado do pacote, e o devolve antes de `finalizar_modo_local`.
CODIGO_CAMPO_PENDENTE = 'campo_pendente'
CODIGO_CONFLITO = 'conflito_versionamento'
CODIGO_CAMPO_DIVERGIU = 'field_diverged'
CODIGO_CAMPO_ADULTERADO = 'field_tampered'
# O clone vivo já não está em campo: o arquivo já voltou (`campo.js` do
# servidor), e só falta finalizar.
CODIGO_NAO_EM_CAMPO = 'nao_em_campo'


class ErroVersionamento(Exception):
    # Recusa de uma rota do versionamento com o que o plugin decide: o status
    # HTTP, o código estável (`codigo` do envelope do SAP ou `code` do serviço)
    # e os `dados` (no conflito: `sessao_id`, `repo_id`, `conflitos`).
    def __init__(self, mensagem, status=None, codigo=None, dados=None):
        super(ErroVersionamento, self).__init__(mensagem)
        self.mensagem = mensagem
        self.status = status
        self.codigo = codigo
        self.dados = dados if isinstance(dados, dict) else {}


def codigoDaRecusa(corpo):
    # O SAP põe o código da recusa em `codigo` (AppError); o serviço, em `code`
    # (ou `error_code`). A rota pode repassar o corpo do serviço dentro de
    # `dados`: o código é procurado nos dois níveis.
    if not isinstance(corpo, dict):
        return None
    dados = corpo.get('dados') if isinstance(corpo.get('dados'), dict) else {}
    for fonte in (corpo, dados):
        for chave in ('codigo', 'code', 'error_code'):
            if isinstance(fonte.get(chave), str) and fonte.get(chave):
                return fonte[chave]
    return None


def mensagemErroCampo(erro):
    # O texto que o gerente lê para cada recusa do fluxo de campo.
    codigo = getattr(erro, 'codigo', None)
    servidor = getattr(erro, 'mensagem', None) or str(erro)
    if codigo == CODIGO_CAMPO_DIVERGIU:
        return (
            'O clone da atividade no servidor recebeu gravações depois que o arquivo de campo '
            'foi baixado (field_diverged), e o arquivo não pode substituí-lo. Nada mudou no '
            'servidor: o clone ficou intocado e a atividade continua em modo local.\n{0}'
        ).format(servidor)
    if codigo == CODIGO_CAMPO_ADULTERADO:
        return (
            'As permissões gravadas no arquivo de campo não são as do clone no servidor '
            '(field_tampered): o arquivo foi alterado fora do SAP Operador. Nada mudou no '
            'servidor e a atividade continua em modo local.\n{0}'
        ).format(servidor)
    if codigo == CODIGO_CAMPO_PENDENTE:
        return (
            'O servidor ainda não recebeu o arquivo de campo desta atividade (campo_pendente), '
            'e por isso não a finaliza. A atividade continua em modo local.\n{0}'
        ).format(servidor)
    if codigo == CODIGO_CONFLITO:
        dados = getattr(erro, 'dados', None) or {}
        return (
            '{0}\nO arquivo de campo já está no servidor e a atividade continua em modo local: '
            'resolva os conflitos da sessão {1} (repositório {2}) e use "Finalizar SAP Local" de novo.'
        ).format(servidor, dados.get('sessao_id'), dados.get('repo_id'))
    return servidor


def versionamentoDoPacote(pacote):
    # A seção `versionamento` do pacote da atividade. O servidor a põe em
    # `dados.atividade.versionamento` (`ciclo_atividade.completarPacote`); o
    # contrato (seção 5) a descreve em `dados.versionamento`. Vale a que vier.
    dados = (pacote or {}).get('dados') or {}
    atividade = dados.get('atividade') or {}
    for fonte in (atividade, dados):
        if isinstance(fonte.get('versionamento'), dict):
            return fonte['versionamento']
    return None


def nomeArquivoCampo(contentDisposition, repoId):
    # O nome do arquivo de campo: o de `Content-Disposition` (o serviço manda
    # `<repo_id>.gpkg`), ou `<repo_id>.gpkg`. Só o nome, sem caminho, e só com
    # caracteres seguros: ele vai para o pacote e volta para montar o caminho.
    nome = None
    for parte in (contentDisposition or '').split(';'):
        chave, _, valor = parte.strip().partition('=')
        if chave.lower() == 'filename' and valor:
            nome = valor.strip().strip('"')
    if not nome:
        nome = '{0}.gpkg'.format(repoId or 'campo')
    nome = nome.replace('\\', '/').split('/')[-1]
    nome = ''.join(c if (c.isalnum() or c in '-_.') else '_' for c in nome).lstrip('.')
    if not nome.lower().endswith('.gpkg'):
        nome = nome + '.gpkg'
    return nome


def pacoteParaSAPLocal(pacote):
    # A cópia do pacote que vai para `public.sap_local` do banco local, SEM
    # segredo: `getActivityDataById` acrescenta o login e a senha do gerente no
    # SAP (`user`, `password`), e o banco local vinha com a senha dele. O SAP
    # Operador repõe `local_db` (usuário, senha, servidor, porta e banco) do
    # próprio login ao carregar o pacote, então nada disso precisa ser gravado.
    copia = json.loads(json.dumps(pacote))
    copia.pop('user', None)
    copia.pop('password', None)
    if isinstance(copia.get('dados'), dict):
        copia['dados'].pop('login_info', None)
    localDb = copia.get('local_db')
    if isinstance(localDb, dict):
        localDb.pop('password', None)
        localDb['host'] = 'localhost'
    return copia

# Estados finais de uma tarefa do serviço de versionamento (`GET /jobs/:id`).
JOB_TERMINAIS = ('succeeded', 'failed', 'cancelled', 'interrupted')


def ehTipo(item, tipos):
    # Linha sem o campo é a do servidor anterior ao tipo 4, que só devolvia
    # banco PostgreSQL (tipos 2 e 3) em `GET /producao/banco_dados`.
    tipo = item.get('tipo_dado_producao_id')
    return tipo is None or tipo in tipos


def ehBaseVersionada(item):
    return item.get('tipo_dado_producao_id') == TIPO_DADO_BASE_VERSIONADA


def rotuloDadoProducao(item):
    # O rótulo do dado de produção nos combos. Para o PostgreSQL é o nome do
    # banco (o `nome` de `GET /producao/banco_dados`). A base versionada não tem
    # banco: mostra o tipo e o `repo_id`, quando o servidor o devolve.
    ident = item.get('id')
    if ehBaseVersionada(item):
        repo = item.get('repo_id') or item.get('nome') or item.get('configuracao_producao')
        tipo = item.get('tipo_dado_producao') or 'Base versionada'
        if repo:
            return '{0}: {1} (dado de produção {2})'.format(tipo, repo, ident)
        return '{0} (dado de produção {1})'.format(tipo, ident)
    if item.get('nome'):
        return item['nome']
    # `nome` nulo é cadastro malformado (o servidor não sabe ler a coluna).
    return 'Dado de produção {0} (cadastro incompleto)'.format(ident)


def pacoteEhBaseVersionada(pacote):
    # O pacote da atividade (`GET /gerencia_producao/atividade/:id`) da base
    # versionada traz `versionamento` e não traz `configuracao_producao`.
    dados = (pacote or {}).get('dados') or {}
    atividade = dados.get('atividade') or {}
    if dados.get('versionamento') or atividade.get('versionamento'):
        return True
    dado = atividade.get('dado_producao') or {}
    return dado.get('tipo_dado_producao_id') == TIPO_DADO_BASE_VERSIONADA


def mensagemComRevogacao(resposta):
    # Pausar, reiniciar e voltar devolvem `dados.revogacao` quando havia acesso
    # ao banco de edição a fechar; `ok: false` diz que a operação valeu, mas a
    # porta ficou aberta. Nada disso pode virar "sucesso" calado.
    if not resposta:
        return None
    partes = [resposta.get('message') or 'Executado.']
    dados = resposta.get('dados')
    revogacao = dados.get('revogacao') if isinstance(dados, dict) else None
    if revogacao:
        if revogacao.get('ok'):
            partes.append(
                'Acesso ao banco de produção revogado em {0} atividade(s).'.format(
                    revogacao.get('revogadas', 0)
                )
            )
        else:
            partes.append(
                'ATENÇÃO: a revogação do acesso ao banco de produção FALHOU '
                '(revogadas: {0}).'.format(revogacao.get('revogadas', 0))
            )
            for falha in revogacao.get('falhas') or []:
                partes.append('Atividade {0}: {1}'.format(
                    falha.get('atividade_id'), falha.get('mensagem')
                ))
            if revogacao.get('providencia'):
                partes.append(revogacao['providencia'])
    return '\n'.join(partes)


def revogacaoFalhou(resposta):
    dados = (resposta or {}).get('dados')
    revogacao = dados.get('revogacao') if isinstance(dados, dict) else None
    return bool(revogacao) and not revogacao.get('ok')


def jobIdDaResposta(resposta):
    # `POST /api/versionamento/lote|bloco` responde 202 com o `job_id` (seção 5
    # do contrato). O envelope do SAP põe a carga em `dados`.
    if not resposta:
        return None
    dados = resposta.get('dados')
    for fonte in (dados if isinstance(dados, dict) else {}, resposta):
        if fonte.get('job_id'):
            return fonte['job_id']
        repositorio = fonte.get('repositorio')
        if isinstance(repositorio, dict) and repositorio.get('job_id'):
            return repositorio['job_id']
    return None


def resumoJob(job):
    # Uma linha legível de uma tarefa. Aceita a tarefa do serviço (`state`,
    # `progress`, `error`, de `GET /servico/jobs/:id`) e o resumo que o SAP põe
    # em cada linha de `GET /versionamento/repositorios` (`tarefa: {id, estado,
    # progresso, erro}`). `progress` é `{completed, phase}`, e `completed` é
    # contagem, não porcentagem (`Progress::report` do dsg-service).
    if not job:
        return ''
    estado = job.get('state') or job.get('estado') or '?'
    progresso = job.get('progress') or job.get('progresso')
    erro = job.get('error') or job.get('erro')
    texto = estado
    if isinstance(progresso, dict) and progresso.get('phase'):
        texto = '{0}: {1} ({2})'.format(estado, progresso['phase'], progresso.get('completed', 0))
    if erro:
        texto = '{0} - {1}'.format(texto, erro)
    return texto


def datasetParaCamada(nome):
    # O importador EDGV nomeia o dataset `schema.tabela` (dsg-import,
    # `ClassPlan.name`); a camada do SAP é o par (schema, nome).
    if '.' in nome:
        schema, tabela = nome.split('.', 1)
        return {'schema': schema, 'nome': tabela}
    return {'schema': '', 'nome': nome}
