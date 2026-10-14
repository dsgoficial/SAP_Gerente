# -*- coding: utf-8 -*-
# Confere a cópia do provedor do versionamento (`modules/versionamento/`) contra
# o manifesto SHA-256 que `.dev/copiar_versionamento.py` grava e, quando o
# repositório irmão SAP_Operador existe, contra a fonte (contrato do
# versionamento no SAP 3.0, seções 7 e 9.4). Só biblioteca padrão, sem QGIS.
#
# Uso:
#   python conferir_copia_versionamento.py [--plugin <pasta SAP_Gerente>] [--operador <pasta SAP_Operador>]
#   python conferir_copia_versionamento.py --provar
#
# Reprova (código 1): manifesto ausente ou ilegível; arquivo da cópia fora do
# manifesto; arquivo do manifesto ausente da cópia; SHA-256 diferente; e, com o
# irmão presente, arquivo da fonte fora da cópia ou com SHA-256 diferente (a
# fonte mudou e a cópia não foi refeita pelo script).
#
# `--provar` degrada uma cópia temporária da cópia REAL em cada eixo e exige que
# cada degradação reprove; a cópia real tem de passar antes.

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
PLUGIN_PADRAO = os.path.abspath(os.path.join(AQUI, '..', '..'))
RELATIVO = os.path.join('modules', 'versionamento')
MANIFESTO = 'manifesto.json'


def arquivosDe(pasta):
    saida = []
    for raiz, pastas, arquivos in os.walk(pasta):
        pastas[:] = sorted(p for p in pastas if p != '__pycache__')
        for nome in sorted(arquivos):
            if nome.endswith(('.pyc', '.pyo')):
                continue
            relativo = os.path.relpath(os.path.join(raiz, nome), pasta).replace(os.sep, '/')
            if relativo != MANIFESTO:
                saida.append(relativo)
    return sorted(saida)


def sha256(caminho):
    # Do conteúdo com fim de linha LF, a forma que o git guarda: com
    # `core.autocrlf` o mesmo commit sai CRLF no Windows e LF no Linux, e o
    # manifesto tem de valer nos dois.
    with open(caminho, 'rb') as f:
        return hashlib.sha256(f.read().replace(b'\r\n', b'\n')).hexdigest()


def conferir(plugin, operador):
    # Lista de problemas (vazia = aprovado) e o resumo do que foi conferido.
    destino = os.path.join(plugin, RELATIVO)
    caminhoManifesto = os.path.join(destino, MANIFESTO)
    if not os.path.isfile(caminhoManifesto):
        return ['manifesto ausente: {0}/{1}'.format(RELATIVO.replace(os.sep, '/'), MANIFESTO)], ''
    try:
        with open(caminhoManifesto, encoding='utf-8') as f:
            manifesto = json.load(f)
        esperado = manifesto['arquivos']
        if not isinstance(esperado, dict) or not esperado:
            raise ValueError('sem arquivos')
    except (ValueError, KeyError, TypeError) as e:
        return ['manifesto ilegível: {0}'.format(e)], ''
    problemas = []
    copia = arquivosDe(destino)
    for relativo in copia:
        if relativo not in esperado:
            problemas.append('na cópia e fora do manifesto: ' + relativo)
        elif sha256(os.path.join(destino, relativo)) != esperado[relativo]:
            problemas.append('SHA-256 da cópia difere do manifesto: ' + relativo)
    for relativo in esperado:
        if relativo not in copia:
            problemas.append('no manifesto e ausente da cópia: ' + relativo)
    fonte = os.path.join(operador, RELATIVO) if operador else None
    if fonte and os.path.isdir(fonte):
        origem = arquivosDe(fonte)
        for relativo in origem:
            if relativo not in esperado:
                problemas.append('na fonte (SAP_Operador) e fora da cópia: ' + relativo)
            elif sha256(os.path.join(fonte, relativo)) != esperado[relativo]:
                problemas.append('a fonte (SAP_Operador) mudou e a cópia não: ' + relativo)
        for relativo in esperado:
            if relativo not in origem:
                problemas.append('na cópia e ausente da fonte (SAP_Operador): ' + relativo)
        contra = 'manifesto e fonte'
    else:
        contra = 'só o manifesto (SAP_Operador irmão ausente)'
    resumo = '{0} arquivos conferidos contra {1}; commit do SAP Operador no manifesto: {2}'.format(
        len(esperado), contra, manifesto.get('commit_operador'))
    return problemas, resumo


def provar(plugin, operador):
    problemas, _ = conferir(plugin, operador)
    if problemas:
        sys.exit('a cópia real já reprova; a prova precisa partir de uma cópia aprovada:\n' + '\n'.join(problemas))
    base = tempfile.mkdtemp(prefix='provar_copia_versionamento_')

    def montar(nome):
        raiz = os.path.join(base, nome)
        pluginTmp = os.path.join(raiz, 'SAP_Gerente')
        operadorTmp = os.path.join(raiz, 'SAP_Operador')
        shutil.copytree(os.path.join(plugin, RELATIVO), os.path.join(pluginTmp, RELATIVO),
                        ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(os.path.join(operador, RELATIVO), os.path.join(operadorTmp, RELATIVO),
                        ignore=shutil.ignore_patterns('__pycache__'))
        return pluginTmp, operadorTmp

    def acrescentarByte(caminho):
        with open(caminho, 'ab') as f:
            f.write(b'\n# degradado\n')

    def tirarDoManifesto(pluginTmp, relativo):
        caminho = os.path.join(pluginTmp, RELATIVO, MANIFESTO)
        with open(caminho, encoding='utf-8') as f:
            m = json.load(f)
        m['arquivos'].pop(relativo)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(m, f)

    alvo = 'client.py'
    degradacoes = [
        ('byte a mais num arquivo da cópia',
         lambda p, o: acrescentarByte(os.path.join(p, RELATIVO, alvo))),
        ('arquivo removido da cópia',
         lambda p, o: os.remove(os.path.join(p, RELATIVO, alvo))),
        ('arquivo a mais na cópia',
         lambda p, o: open(os.path.join(p, RELATIVO, 'extra.py'), 'w').close()),
        ('arquivo fora do manifesto',
         lambda p, o: tirarDoManifesto(p, alvo)),
        ('manifesto ausente',
         lambda p, o: os.remove(os.path.join(p, RELATIVO, MANIFESTO))),
        ('fonte mudou e a cópia não',
         lambda p, o: acrescentarByte(os.path.join(o, RELATIVO, alvo))),
        ('arquivo novo na fonte',
         lambda p, o: open(os.path.join(o, RELATIVO, 'novo.py'), 'w').close()),
        ('arquivo removido da fonte',
         lambda p, o: os.remove(os.path.join(o, RELATIVO, alvo))),
    ]
    aprovadas = []
    for i, (nome, degradar) in enumerate(degradacoes):
        pluginTmp, operadorTmp = montar('caso{0}'.format(i))
        degradar(pluginTmp, operadorTmp)
        problemas, _ = conferir(pluginTmp, operadorTmp)
        print('{0:7} {1}: {2}'.format('REPROVA' if problemas else 'PASSOU', nome,
                                     problemas[0] if problemas else ''))
        if not problemas:
            aprovadas.append(nome)
    shutil.rmtree(base, ignore_errors=True)
    if aprovadas:
        sys.exit('degradações que o conferidor deixou passar: {0}'.format(aprovadas))
    print('todas as {0} degradações reprovadas'.format(len(degradacoes)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--plugin', default=PLUGIN_PADRAO)
    p.add_argument('--operador', default=None)
    p.add_argument('--provar', action='store_true')
    args = p.parse_args()
    plugin = os.path.abspath(args.plugin)
    operador = os.path.abspath(args.operador) if args.operador else os.path.join(
        os.path.dirname(plugin), 'SAP_Operador')
    if args.provar:
        if not os.path.isdir(os.path.join(operador, RELATIVO)):
            sys.exit('--provar precisa do SAP_Operador irmão')
        return provar(plugin, operador)
    problemas, resumo = conferir(plugin, operador)
    for problema in problemas:
        print('FALHA ' + problema)
    print(resumo or 'nada conferido')
    sys.exit(1 if problemas else 0)


if __name__ == '__main__':
    main()
