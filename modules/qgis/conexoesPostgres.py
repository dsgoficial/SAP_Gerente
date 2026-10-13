from qgis.PyQt import QtCore


def conexoesPostgresSalvas():
    """As conexões PostgreSQL salvas no QGIS com usuário e senha gravados.

    No SAP 3.0 o servidor não devolve mais o endereço nem a senha do banco de
    produção (`GET /producao/banco_dados` traz só o nome, `GET /producao/login`
    só o login): quem lê o banco direto usa a conexão do próprio QGIS.
    """
    settings = QtCore.QSettings()
    aliases = sorted({
        key.split('/')[2]
        for key in settings.allKeys()
        if 'postgresql' in key.lower()
            and 'host' in key.lower()
            and len(key.split('/')) > 3
    })
    conexoes = []
    for alias in aliases:
        prefixo = 'PostgreSQL/connections/' + alias + '/'
        if not (
                settings.value(prefixo + 'savePassword') == 'true'
                and
                settings.value(prefixo + 'saveUsername') == 'true'
            ):
            continue
        conexoes.append({
            'alias': alias,
            'database': settings.value(prefixo + 'database'),
            'host': settings.value(prefixo + 'host'),
            'port': settings.value(prefixo + 'port'),
            'username': settings.value(prefixo + 'username'),
            'password': settings.value(prefixo + 'password'),
        })
    return conexoes
