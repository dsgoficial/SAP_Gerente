# Constantes do contrato do SAP 3.0 que o plugin inteiro usa. Módulo sem
# dependência nenhuma, para os widgets importarem sem puxar o cliente HTTP.
#
# O plugin fala SÓ com o SAP 3.0: sem alias e sem tradução de nome antigo,
# porque o validador do servidor é ESTRITO (chave desconhecida no corpo vira 400).

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
TIPO_DADO_POSTGIS_COM_PERMISSAO = 2
TIPO_DADO_POSTGIS = 3
TIPO_DADO_BASE_VERSIONADA = 4
# Só estes dois são banco PostgreSQL: revogar permissão só faz sentido neles.
TIPOS_COM_BANCO = (TIPO_DADO_POSTGIS_COM_PERMISSAO, TIPO_DADO_POSTGIS)
# Gerar unidade de trabalho aceita também a base versionada.
TIPOS_GERAR_UT = TIPOS_COM_BANCO + (TIPO_DADO_BASE_VERSIONADA,)

# Mensagem dos fluxos de banco local para a base versionada.
MSG_SAP_LOCAL_VERSIONADA = (
    'O dado de produção desta atividade é uma Base versionada, que não usa banco '
    'local. Use a exportação do GeoPackage de campo (onda 2).'
)

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
