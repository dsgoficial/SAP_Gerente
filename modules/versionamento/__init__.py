"""Versionamento do SAP 3.0 no QGIS: o provedor `dsgversioning` do plugin
antigo (cache local e canal DSGP/1), falando com o repasse do SAP, e, no modo
local do tipo 4, o GeoPackage de campo aberto pelo `ogr` (`campo.py`).

Este diretório só usa import relativo e é copiado igual (mesmo SHA-256) para
o SAP Gerente (contrato-sap.md, seção 7). O plugin chama `registrar(iface)` ao
carregar e `desregistrar()` ao descarregar; o QGIS não remove provedor, então o
registro vale pela sessão inteira.
"""

_state={'reports':None,'hooked':False}


def _attach(layers):
    from . import campo,provider
    from qgis.core import QgsVectorLayer
    for layer in layers:
        if not isinstance(layer,QgsVectorLayer): continue
        provider.attach_layer(layer)
        # Camada do GeoPackage de campo de um projeto reaberto: identidade nova e permissão da etapa.
        campo.ligarCamada(layer)


def registrar(iface=None):
    """Registra o provedor, liga o salvamento em lote das camadas que entram no
    projeto e os avisos de salvamento. Idempotente."""
    from qgis.core import QgsProject
    from . import provider
    from .painel import SaveReports
    provider.register_provider()
    if not _state['hooked']:
        QgsProject.instance().layersAdded.connect(_attach)
        _state['hooked']=True
    if _state['reports'] is None:
        _state['reports']=SaveReports(iface)
    return _state['reports']


def desregistrar():
    from qgis.core import QgsProject
    if _state['hooked']:
        try: QgsProject.instance().layersAdded.disconnect(_attach)
        except TypeError: pass
        _state['hooked']=False
    if _state['reports'] is not None:
        _state['reports'].disconnect(); _state['reports']=None
