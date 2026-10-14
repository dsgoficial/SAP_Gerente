"""Regras de formatação nas camadas do versionamento.

O `dsgtools:assignformatrulestolayersalgorithm` descarta camada cujo provedor
não é `postgres`. Para a camada `dsgversioning` o plugin aplica as regras aqui,
com a mesma semântica do algoritmo (DsgTools, `assignFormatRulesToLayersAlgorithm.py`):
limpa estilos condicionais e o campo virtual `attribute_error_description`,
casa cada regra pelas `camadas` (nome `schema.tabela`, com curinga `*` do
fnmatch), põe um estilo condicional por regra no campo `atributo` (ordenado
pelo `rank` do `grupo_estilo`) e cria o campo virtual com o CASE das regras.

A estatística de regras (`dsgtools:rulestatistics`) acha a camada pela tabela
do endereço, que a camada `ogr` do GeoPackage de campo não tem: para ela vale
`estatisticaDeRegras`, com a mesma semântica e a saída que o SAP Operador lê do
algoritmo.
"""
import fnmatch
import json
from collections import defaultdict
from operator import itemgetter

from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsConditionalStyle,QgsExpression,QgsExpressionContext,QgsExpressionContextUtils,QgsFeatureRequest,
    QgsField)

from .camadas import tabelaDaCamada

ERROR_FIELD='attribute_error_description'


def _key(layer):
    schema,table=tabelaDaCamada(layer)
    return '{}.{}'.format(schema,table)


def _layerNames(filterList,nameList):
    output=set()
    for wildcard in [item for item in filterList if '*' in item]:
        output=output.union(set(fnmatch.filter(nameList,wildcard)))
    return output.union(set(name for name in nameList if name in filterList))


def ruleDict(data,names):
    rules=defaultdict(lambda:defaultdict(list))
    styles={style['tipo_estilo']:{'corRgb':list(map(int,style['cor_rgb'].split(','))),'rank':index}
            for index,style in enumerate(data['grupo_estilo'])}
    for rule in data['regras']:
        item=rule.copy(); item.update(styles[rule['tipo_estilo']])
        for name in _layerNames(rule['camadas'],names):
            rules[name][rule['atributo']].append(item)
        for name in rules:
            for attribute in rules[name]:
                rules[name][attribute]=sorted(rules[name][attribute],key=itemgetter('rank'),reverse=False)
    return rules


def _clean(layer):
    for field in layer.fields():
        layer.conditionalStyles().setFieldStyles(field.name(),[])
    index=layer.fields().indexFromName(ERROR_FIELD)
    if index!=-1:
        layer.removeExpressionField(index)


def _style(data):
    style=QgsConditionalStyle()
    style.setName(data['descricao'])
    style.setRule(data['regra'])
    style.setBackgroundColor(QColor(data['corRgb'][0],data['corRgb'][1],data['corRgb'][2]))
    if not style.isValid():
        raise Exception('Estilo condicional inválido:\n{0}\n{1}'.format(data['descricao'],data['regra']))
    return style


def _virtualField(layer,rules):
    key=_key(layer)
    names=[field.name() for field in layer.fields()]
    listed=[]
    for fieldName,items in rules[key].items():
        if fieldName in names: listed+=items
    expression='CASE\n'
    for data in sorted(listed,key=itemgetter('rank','atributo'),reverse=False):
        expression+="WHEN {condition} THEN '{result}'\n".format(condition=data['regra'],result=data['descricao'])
        if not QgsExpression(expression+"ELSE ''\nEND").isValid():
            raise Exception('Erro ao aplicar a regra:\n {0}\ncampo: {1}\ncamada: {2}'.format(data,data['atributo'],key))
    expression+="ELSE ''\nEND"
    if expression=="CASE\nELSE ''\nEND":
        return
    if QgsExpression(expression).hasParserError():
        raise Exception('Expressão inválida: \n{0}'.format(expression))
    layer.addExpressionField(expression,QgsField(ERROR_FIELD,QMetaType.Type.QString))


def aplicarRegrasDeFormatacao(layers,rulesText,cleanBefore=True):
    """`rulesText`: o JSON de regras do SAP (o mesmo `TEXT` do algoritmo)."""
    data=json.loads(rulesText) if isinstance(rulesText,str) else rulesText
    layers=list(layers)
    if not layers: return {}
    if cleanBefore:
        for layer in layers: _clean(layer)
    rules=ruleDict(data,[_key(layer) for layer in layers])
    for layer in layers:
        key=_key(layer)
        for field in layer.fields():
            if key not in rules or field.name() not in rules[key]: continue
            layer.conditionalStyles().setFieldStyles(field.name(),[_style(item) for item in rules[key][field.name()]])
        _virtualField(layer,rules)
    return rules


def estatisticaDeRegras(rulesText,layers):
    """Como `dsgtools:rulestatistics`, lido como o SAP Operador lê a saída dele
    (`processingLaunchers/ruleStatistics.py`): `{'[RULES] : <tipo_estilo>':
    [camadas com feição que cumpre a condição de erro]}`. A regra vale nas
    camadas que casam com `camadas` (schema.tabela, curinga do fnmatch) e que
    têm o campo `atributo` na tabela de atributos."""
    data=json.loads(rulesText) if isinstance(rulesText,str) else rulesText
    named={}
    for layer in layers: named.setdefault(_key(layer),layer)
    result={}
    for rule in data.get('regras') or []:
        failed=result.setdefault('[RULES] : '+rule['tipo_estilo'],[])
        for name in sorted(_layerNames(rule['camadas'],list(named))):
            layer=named[name]
            if rule['atributo'] not in [column.name for column in layer.attributeTableConfig().columns()]: continue
            context=QgsExpressionContext(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
            request=QgsFeatureRequest(QgsExpression(rule['regra'])).setExpressionContext(context).setLimit(1)
            if any(True for _ in layer.getFeatures(request)) and layer.name() not in failed:
                failed.append(layer.name())
    return {key:sorted(value) for key,value in sorted(result.items())}
