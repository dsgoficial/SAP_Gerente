# -*- coding: utf-8 -*-
# Prova de que o conferidor REPROVA: pega o registro REAL de uma fumaça que
# passou, degrada cada eixo que o conferidor afirma medir (rota, método, corpo
# no Joi, query no Joi, `authorization`, lista do repasse) e exige que cada
# degradação saia reprovada. Se alguma passar, o eixo é aprovado por omissão.
#
# Uso:
#   python provar_conferidor.py --fumaca <saida da fumaça que passou> --servidor <pasta server>

import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))


def achar(chamadas, metodo, prefixo):
    for c in chamadas:
        if c['metodo'] == metodo and c['caminho'].startswith(prefixo):
            return c
    raise SystemExit('o registro não tem {0} {1}: rode a fumaça atual'.format(metodo, prefixo))


def degradacoes(chamadas):
    lote = achar(chamadas, 'POST', '/api/versionamento/lote/')
    descarte = achar(chamadas, 'POST', '/api/versionamento/repositorio/')
    pausa = achar(chamadas, 'POST', '/api/gerencia_producao/atividade/pausar')
    repositorios = achar(chamadas, 'GET', '/api/versionamento/repositorios')
    datasets = achar(chamadas, 'GET', '/api/versionamento/servico/repos/')

    def com(base, **mudancas):
        c = copy.deepcopy(base)
        c.update(mudancas)
        return c

    return [
        ('chave do corpo trocada (Joi estrito)', com(lote, corpo={'dado_producao': lote['corpo']['dado_producao_id']})),
        ('chave a mais no corpo', com(lote, corpo=dict(lote['corpo'], actor='x'))),
        ('motivo vazio no descarte', com(descarte, corpo={'motivo': ''})),
        ('método trocado', com(pausa, metodo='PUT')),
        ('caminho inexistente', com(pausa, caminho='/api/gerencia_producao/atividade/pausa')),
        ('query fora do Joi', com(repositorios, query='lote=10')),
        ('sem authorization', com(datasets, autorizacao=False)),
        ('rota do repasse fora da lista', com(datasets, metodo='POST', caminho='/api/versionamento/servico/repos/x/drop')),
    ]


def conferir(chamadas, servidor):
    pasta = tempfile.mkdtemp(prefix='provar_conferidor_')
    arquivo = os.path.join(pasta, 'fumaca.json')
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump({'chamadas': chamadas}, f)
    proc = subprocess.run(
        [sys.executable, os.path.join(AQUI, 'conferir_chamadas.py'), '--fumaca', arquivo, '--servidor', servidor],
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300
    )
    return proc.returncode, proc.stdout


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--fumaca', required=True)
    p.add_argument('--servidor', default=os.environ.get('SAP_SERVIDOR_DIR'))
    args = p.parse_args()
    with open(args.fumaca, encoding='utf-8') as f:
        chamadas = json.load(f)['chamadas']

    codigo, _ = conferir(chamadas, args.servidor)
    if codigo != 0:
        sys.exit('o registro de base já reprova: a prova precisa partir de uma fumaça aprovada')
    print('base aprovada: {0} chamadas'.format(len(chamadas)))

    aprovadas = []
    for nome, chamada in degradacoes(chamadas):
        codigo, saida = conferir([chamada], args.servidor)
        linha = next((l for l in saida.splitlines() if l.startswith(('FALHA', 'ok'))), '')
        print('{0:6} {1}: {2}'.format('REPROVA' if codigo else 'PASSOU', nome, linha.strip()))
        if codigo == 0:
            aprovadas.append(nome)
    if aprovadas:
        sys.exit('degradações que o conferidor deixou passar: {0}'.format(aprovadas))
    print('todas as degradações reprovadas')


if __name__ == '__main__':
    main()
