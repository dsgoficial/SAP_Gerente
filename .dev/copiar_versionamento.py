# -*- coding: utf-8 -*-
# Copia o provedor do versionamento do SAP Operador para o SAP Gerente e grava o
# manifesto SHA-256 de cada arquivo (contrato do versionamento no SAP 3.0,
# seções 7 e 9.4). O código vive em `SAP_Operador/modules/versionamento/`; aqui
# ele é CÓPIA, nunca editada à mão: quem muda o provedor muda lá e roda isto.
#
# Uso (da raiz do SAP_Gerente):
#   python .dev/copiar_versionamento.py [--operador <pasta do SAP_Operador>]
#
# Sem `--operador`, usa o repositório irmão (`../SAP_Operador`). A pasta de
# destino é espelhada: arquivo que sumiu da fonte some daqui. O manifesto
# (`modules/versionamento/manifesto.json`) guarda o commit do SAP Operador, os
# arquivos da pasta com alteração não commitada no momento da cópia e o SHA-256
# de cada arquivo. O teste `tests/versionamento/conferir_copia_versionamento.py`
# confere a cópia contra o manifesto e, havendo o irmão, contra a fonte.

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.abspath(os.path.join(AQUI, '..'))
RELATIVO = os.path.join('modules', 'versionamento')
MANIFESTO = 'manifesto.json'
IGNORAR_PASTAS = {'__pycache__'}
IGNORAR_SUFIXOS = ('.pyc', '.pyo')


def arquivosDe(pasta):
    # Caminhos relativos (com '/') dos arquivos da pasta, sem cache do Python e
    # sem o manifesto.
    saida = []
    for raiz, pastas, arquivos in os.walk(pasta):
        pastas[:] = sorted(p for p in pastas if p not in IGNORAR_PASTAS)
        for nome in sorted(arquivos):
            if nome.endswith(IGNORAR_SUFIXOS):
                continue
            relativo = os.path.relpath(os.path.join(raiz, nome), pasta).replace(os.sep, '/')
            if relativo == MANIFESTO:
                continue
            saida.append(relativo)
    return sorted(saida)


def sha256(caminho):
    # Do conteúdo com fim de linha LF, a forma que o git guarda: com
    # `core.autocrlf` o mesmo commit sai CRLF no Windows e LF no Linux, e o
    # manifesto tem de valer nos dois.
    with open(caminho, 'rb') as f:
        return hashlib.sha256(f.read().replace(b'\r\n', b'\n')).hexdigest()


def git(pasta, *args):
    try:
        proc = subprocess.run(
            ['git', '-C', pasta] + list(args),
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def copiar(operador, plugin=PLUGIN):
    fonte = os.path.join(operador, RELATIVO)
    destino = os.path.join(plugin, RELATIVO)
    if not os.path.isfile(os.path.join(fonte, '__init__.py')):
        raise SystemExit('fonte não encontrada: {0} sem __init__.py'.format(RELATIVO))
    arquivos = arquivosDe(fonte)
    # Espelho: o que não está na fonte sai do destino (a pasta é só cópia).
    if os.path.isdir(destino):
        for relativo in arquivosDe(destino):
            if relativo not in arquivos:
                os.remove(os.path.join(destino, relativo))
    for relativo in arquivos:
        alvo = os.path.join(destino, relativo)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        shutil.copyfile(os.path.join(fonte, relativo), alvo)
    commit = (git(operador, 'rev-parse', 'HEAD') or '').strip() or None
    sujos = []
    status = git(operador, 'status', '--porcelain', '--', RELATIVO.replace(os.sep, '/'))
    for linha in (status or '').splitlines():
        caminho = linha[3:].strip().strip('"')
        prefixo = RELATIVO.replace(os.sep, '/') + '/'
        if caminho.startswith(prefixo) and '__pycache__' not in caminho:
            sujos.append(caminho[len(prefixo):])
    manifesto = {
        'origem': 'SAP_Operador/' + RELATIVO.replace(os.sep, '/'),
        'commit_operador': commit,
        'alteracoes_nao_commitadas': sorted(sujos),
        'arquivos': {relativo: sha256(os.path.join(destino, relativo)) for relativo in arquivos},
    }
    with open(os.path.join(destino, MANIFESTO), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write('\n')
    return manifesto


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--operador', default=os.path.join(os.path.dirname(PLUGIN), 'SAP_Operador'))
    args = p.parse_args()
    manifesto = copiar(os.path.abspath(args.operador))
    print('copiados {0} arquivos; commit do SAP Operador {1}{2}'.format(
        len(manifesto['arquivos']), manifesto['commit_operador'],
        '; ALTERAÇÕES NÃO COMMITADAS: ' + ', '.join(manifesto['alteracoes_nao_commitadas'])
        if manifesto['alteracoes_nao_commitadas'] else ''
    ))


if __name__ == '__main__':
    sys.exit(main())
