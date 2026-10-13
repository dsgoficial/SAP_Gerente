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
