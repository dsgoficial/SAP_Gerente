"""Service contract this plugin version is distributed with (no QGIS imports).

Portado do plugin antigo sem o endereço padrão do serviço local: no SAP 3.0 o
QGIS fala só com o repasse do SAP, e /info chega por ele.

tools/build_qgis_plugin.py writes these values next to the plugin archive
(required and optional capabilities), tools/dist_rust.py records them in the
distribution manifest, and tools/test_dist.py checks that the packaged
service declares every required capability in GET /api/info and reports the
optional ones it lacks. The panel and the provider refuse a service that
lacks a required one, naming what is missing.
"""

# Capabilities the panel and the dsgversioning provider need (D024, D026):
# saving in one batch with an idempotency key and undoing it, the merge that
# closes the clone, its discard and the clones of a repository, and the reads
# by extent. There is no other flow: a service without one of them (an older
# one, or the retired Python reference) is refused.
REQUIRED_CAPABILITIES=(
    'batch_write',
    'children',
    'discard',
    'extent',
    'features_bbox',
    'features_ids',
    'merge_closes_clone',
    'save_request_id',
    'shallow_clone',
    'undo_last_save',
    # D040, D042: identities are canonical UUIDs and refusals carry a stable
    # code the plugin decides on (the stale save, for one).
    'uuid_identity',
    'error_codes',
)

# Capabilities the plugin uses when the service declares them and does
# without otherwise: the repository model (domains, defaults and rules of the
# classes) and the refusals of a save listed per feature and field.
OPTIONAL_CAPABILITIES=(
    'features_dsgp1',
    'repository_model',
    'save_violations',
)

# Storage format the service must report (formato-4.md).
STORAGE_FORMAT=4


def missing_capabilities(info):
    """Required capabilities absent from an /api/info answer, in order; () when none is."""
    declared=set((info or {}).get('capabilities') or [])
    return tuple(name for name in REQUIRED_CAPABILITIES if name not in declared)


def refusal(info):
    """Why this plugin does not work with the service of `info`, or None when it does."""
    missing=missing_capabilities(info)
    if not missing: return None
    service=(info or {}).get('service') or {}
    return ('O serviço '+str(service.get('version','sem versão declarada'))+' não declara '+', '.join(missing)+
            ', de que esta versão do plugin depende (salvamento sem commit, merge que encerra o clone, leitura por extensão). '
            'Atualize o serviço de versionamento do SAP e o plugin do SAP juntos.')
