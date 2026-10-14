# -*- coding: utf-8 -*-
# Conferidor das chamadas que a fumaça registrou (`fumaca_painel.py --saida`)
# contra o servidor SAP 3.0 de verdade (o roteador e os Joi, por
# `conferir_rotas.cjs`) e, para as rotas do versionamento que o servidor ainda
# não tiver, contra o contrato (`versionamento/docs/contrato-sap.md`, seção 5).
#
# Uso:
#   python conferir_chamadas.py --fumaca <saida da fumaça> --servidor <pasta server do controle_acervo>
#
# Reprova (código 1): chamada sem rota no servidor, corpo/query recusado pelo
# Joi da rota, chamada sem `authorization`, ou chamada do versionamento fora do
# contrato. Rota do repasse fora da lista do gerente sai como AVISO.

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))


def _corpoLote(corpo, query):
    if not ( isinstance(corpo, dict) and set(corpo) == {'dado_producao_id'} ):
        return 'corpo deve ser {dado_producao_id}, veio %r' % (corpo,)
    if not isinstance(corpo['dado_producao_id'], int):
        return 'dado_producao_id deve ser inteiro'
    return None


def _corpoBloco(corpo, query):
    if corpo not in (None, {}):
        return 'o contrato não define corpo para o bloco, veio %r' % (corpo,)
    return None


def _queryRepositorios(corpo, query):
    chaves = {par.split('=')[0] for par in (query or '').split('&') if par}
    if not chaves <= {'lote_id', 'bloco_id'}:
        return 'query fora do contrato: %s' % sorted(chaves)
    return None


def _corpoDescartar(corpo, query):
    if not ( isinstance(corpo, dict) and set(corpo) == {'motivo'} and isinstance(corpo['motivo'], str)
             and corpo['motivo'].strip() ):
        return 'corpo deve ser {motivo: texto}, veio %r' % (corpo,)
    return None


def _ehBinario(corpo):
    # O servidor falso registra corpo binário pelo tamanho e pelo SHA-256.
    return isinstance(corpo, dict) and isinstance(corpo.get('binario'), int)


def _corpoBinario(corpo, query):
    # Contrato 9.2: `POST .../campo` leva o GeoPackage, binário, em fluxo.
    if not _ehBinario(corpo) or corpo['binario'] <= 0:
        return 'o corpo deve ser o arquivo de campo (binário), veio %r' % (corpo,)
    if corpo.get('content_type') in (None, '', 'application/json'):
        return 'o arquivo de campo não pode ir como JSON (content-type %r)' % (corpo.get('content_type'),)
    return None


def _semCorpo(corpo, query):
    if corpo not in (None, {}):
        return 'o contrato não define corpo para esta rota, veio %r' % (corpo,)
    return None


def _corpoIntegracaoLote(corpo, query):
    if not (isinstance(corpo, dict) and 'subfase_id' in corpo
            and set(corpo) <= {'subfase_id', 'dado_producao_id'}):
        return 'corpo deve ser {subfase_id, dado_producao_id?}, veio %r' % (corpo,)
    if not all(isinstance(v, int) for v in corpo.values()):
        return 'subfase_id e dado_producao_id devem ser inteiros'
    return None


# Seção 5 e 9.2 do contrato. (método, caminho, conferência, aviso)
CONTRATO = [
    ('GET', r'/api/versionamento/atividade/\d+/campo', _semCorpo, None),
    ('POST', r'/api/versionamento/atividade/\d+/campo', _corpoBinario, None),
    ('POST', r'/api/versionamento/lote/\d+/integracao', _corpoIntegracaoLote, None),
    ('POST', r'/api/versionamento/bloco/\d+/integracao', _corpoIntegracaoLote, None),
    ('POST', r'/api/versionamento/lote/\d+', _corpoLote, None),
    ('POST', r'/api/versionamento/bloco/\d+', _corpoBloco, None),
    ('GET', r'/api/versionamento/repositorios', _queryRepositorios, None),
    ('POST', r'/api/versionamento/repositorio/\d+/descartar', _corpoDescartar, None),
    # Repasse: lista do gerente = as do operador em qualquer repositório
    # registrado, mais children, coverage, releases, GET /jobs/:id e cancel.
    ('GET', r'/api/versionamento/servico/repos/[^/]+/datasets', None, None),
    ('GET', r'/api/versionamento/servico/jobs/[^/]+', None, None),
    ('GET', r'/api/versionamento/servico/repos', None,
     'GET /repos não está na lista do repasse (contrato, seção 5, e `repasse.classificar`): '
     'responde 403, e o plugin cai para o repo_id digitado, sem caixa de erro'),
]


# Conferências do contrato que valem MESMO com a rota no servidor: a rota do
# arquivo de campo não tem schema de corpo (o corpo é o arquivo, em fluxo), e o
# Joi não diria nada de um JSON mandado no lugar dele.
SEMPRE = [
    ('POST', r'/api/versionamento/atividade/\d+/campo', _corpoBinario),
]


def conferirSempre(chamada):
    for metodo, padrao, conferencia in SEMPRE:
        if chamada['metodo'] == metodo and re.fullmatch(padrao, chamada['caminho']):
            return conferencia(chamada.get('corpo'), chamada.get('query'))
    return None


def conferirContrato(chamada):
    for metodo, padrao, conferencia, aviso in CONTRATO:
        if chamada['metodo'] == metodo and re.fullmatch(padrao, chamada['caminho']):
            erro = conferencia(chamada.get('corpo'), chamada.get('query')) if conferencia else None
            return padrao, erro, aviso
    return None, 'rota do versionamento fora do contrato', None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--fumaca', required=True)
    p.add_argument('--servidor', default=os.environ.get('SAP_SERVIDOR_DIR'))
    p.add_argument('--node', default='node')
    args = p.parse_args()
    if not args.servidor:
        sys.exit('informe --servidor (ou SAP_SERVIDOR_DIR): a pasta server do controle_acervo')

    with open(args.fumaca, encoding='utf-8') as f:
        fumaca = json.load(f)

    unicas, vistas = [], set()
    for c in fumaca['chamadas']:
        chave = (c['metodo'], c['caminho'], c.get('query') or '', json.dumps(c.get('corpo'), sort_keys=True))
        if chave in vistas:
            continue
        vistas.add(chave)
        unicas.append({k: c.get(k) for k in ('metodo', 'caminho', 'query', 'corpo', 'autorizacao')})

    pasta = tempfile.mkdtemp(prefix='conferir_sap_')
    entrada = os.path.join(pasta, 'chamadas.json')
    saida = os.path.join(pasta, 'saida.json')
    # O corpo binário (registrado pelo tamanho e pelo SHA-256) não vai ao Joi
    # como se fosse JSON: para o roteador ele é fluxo, sem corpo lido.
    paraNode = [dict(c, corpo=None) if _ehBinario(c.get('corpo')) else c for c in unicas]
    with open(entrada, 'w', encoding='utf-8') as f:
        json.dump(paraNode, f)
    proc = subprocess.run(
        [args.node, os.path.join(AQUI, 'conferir_rotas.cjs'), args.servidor, entrada, saida],
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180
    )
    if proc.returncode != 0 or not os.path.exists(saida):
        sys.exit('conferir_rotas.cjs falhou:\n' + proc.stderr[-3000:])
    with open(saida, encoding='utf-8') as f:
        conferidas = json.load(f)

    temRotasVersionamento = os.path.isdir(os.path.join(args.servidor, 'src', 'versionamento'))
    reprovadas, avisos, linhas = [], [], []
    porContrato = 0
    for original, c in zip(unicas, conferidas):
        c['corpo'] = original.get('corpo')
        rotulo = '{0} {1}{2}'.format(c['metodo'], c['caminho'], '?' + c['query'] if c.get('query') else '')
        problema = None
        if not c.get('autorizacao'):
            problema = 'sem authorization'
        problema = problema or conferirSempre(c)
        versionamento = c['caminho'].startswith('/api/versionamento/')
        if c.get('rota') and 'repasse' in c:
            # O repasse do servidor: a lista dele diz o nível (livre, gerente,
            # repositorio) ou recusa (null = 403).
            origem = 'servidor repasse ' + c['rota'] + ' (nível: {0})'.format(c['repasse'])
            if c['repasse'] is None:
                padrao, erro, aviso = conferirContrato(c)
                if aviso:
                    avisos.append('{0}: {1}'.format(rotulo, aviso))
                else:
                    problema = problema or 'o repasse do servidor recusa (403) esta rota'
        elif c.get('rota'):
            origem = 'servidor ' + c['rota'] + (' (Joi)' if c.get('joi') else ' (sem Joi)')
            problema = problema or c.get('erro')
        elif versionamento:
            porContrato += 1
            padrao, erro, aviso = conferirContrato(c)
            origem = 'contrato ' + (padrao or '?')
            problema = problema or erro
            if aviso:
                avisos.append('{0}: {1}'.format(rotulo, aviso))
        else:
            origem = 'SEM ROTA no servidor'
            problema = problema or 'chamada sem rota'
        linhas.append(('FALHA' if problema else 'ok', rotulo, origem, problema or ''))
        if problema:
            reprovadas.append(rotulo)

    for estado, rotulo, origem, problema in linhas:
        print('{0:5} {1}  <- {2}{3}'.format(estado, rotulo, origem, ('  !! ' + problema) if problema else ''))
    print()
    print('chamadas únicas: {0}; conferidas no servidor: {1}; pelo contrato: {2}; reprovadas: {3}'.format(
        len(conferidas), sum(1 for c in conferidas if c.get('rota')), porContrato, len(reprovadas)))
    print('rotas do versionamento no servidor: {0}'.format(
        'SIM (server/src/versionamento existe)' if temRotasVersionamento
        else 'NÃO (server/src/versionamento ausente): versionamento conferido pelo contrato'))
    # As rotas da onda 2 (contrato 9.2): no roteador do disco ou só no contrato.
    for metodo, padrao in ONDA2:
        vistas_ = [c for c in conferidas if c['metodo'] == metodo and re.fullmatch(padrao, c['caminho'])]
        if not vistas_:
            situacao = 'nenhuma chamada na fumaça'
        elif all(c.get('rota') for c in vistas_):
            situacao = 'no servidor ({0})'.format(vistas_[0]['rota'])
        else:
            situacao = 'AUSENTE do servidor: conferida pelo contrato'
        print('onda 2: {0} {1}: {2}'.format(metodo, padrao, situacao))
    for aviso in avisos:
        print('AVISO ' + aviso)
    sys.exit(1 if reprovadas else 0)


ONDA2 = [
    ('GET', r'/api/versionamento/atividade/\d+/campo'),
    ('POST', r'/api/versionamento/atividade/\d+/campo'),
    ('POST', r'/api/versionamento/lote/\d+/integracao'),
    ('POST', r'/api/versionamento/bloco/\d+/integracao'),
    ('PUT', r'/api/gerencia_producao/finalizar_modo_local'),
    ('GET', r'/api/versionamento/servico/repos/[^/]+/sessions/[^/]+/items'),
    ('POST', r'/api/versionamento/servico/repos/[^/]+/sessions/[^/]+/resolve'),
]


if __name__ == '__main__':
    main()
