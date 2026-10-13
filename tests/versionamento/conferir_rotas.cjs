'use strict'
// Confere chamadas HTTP do SAP Gerente contra o roteador REAL do servidor SAP 3.0
// (Express 5): para cada chamada, acha a rota (método e caminho) e roda nela os
// middlewares de validação Joi que a própria rota declara (`schemaValidation`),
// com o corpo, a query e os parâmetros da chamada. Não abre banco nem porta: só
// carrega `src/routes.js` e percorre a pilha do roteador.
//
// Uso: node conferir_rotas.cjs <pasta server do controle_acervo> <chamadas.json> <saida.json>
// `chamadas.json`: lista de { metodo, caminho, query, corpo }. `saida.json`: a
// mesma lista com `rota` (o padrão casado ou null), `joi` e `erro`. A saída vai
// para arquivo porque o servidor escreve na saída padrão ao carregar o `.env`.

const path = require('path')
const fs = require('fs')

const [, , pastaServidor, arquivoChamadas, arquivoSaida] = process.argv
if (!pastaServidor || !arquivoChamadas || !arquivoSaida) {
  console.error('uso: node conferir_rotas.cjs <pasta server> <chamadas.json> <saida.json>')
  process.exit(2)
}

const src = path.resolve(pastaServidor, 'src')

// Os dois middlewares de validação passam a marcar a função que devolvem com o
// schema, ANTES de as rotas serem carregadas (elas os pegam no require).
for (const nome of ['schema_validation', 'schema_validation_estrito']) {
  const arquivo = path.join(src, 'utils', nome + '.js')
  if (!fs.existsSync(arquivo)) continue
  const original = require(arquivo)
  const marcado = schemas => {
    const mw = original(schemas)
    mw.__schemas = schemas
    return mw
  }
  require.cache[require.resolve(arquivo)].exports = marcado
}
const indiceUtils = require.resolve(path.join(src, 'utils', 'index.js'))
delete require.cache[indiceUtils]

const roteador = require(path.join(src, 'routes.js'))

const acharRota = (pilha, caminho, metodo, prefixo) => {
  for (const camada of pilha) {
    if (!camada.match(caminho)) continue
    if (camada.route) {
      const metodos = camada.route.methods || {}
      if (!metodos[metodo.toLowerCase()] && !metodos._all) continue
      return { camada, padrao: prefixo + camada.route.path, params: { ...camada.params } }
    }
    // O repasse do versionamento (`router.use('/servico', ..., repasse)`) não é
    // rota: é um middleware com a lista própria (`repasse.classificar`), que
    // devolve o nível exigido ou null (403).
    if (camada.handle && typeof camada.handle.classificar === 'function') {
      const resto = caminho.slice(camada.path.length) || '/'
      const segmentos = camada.handle.segmentosDe ? camada.handle.segmentosDe(resto) : resto.split('/').filter(Boolean)
      const regra = segmentos ? camada.handle.classificar(metodo, segmentos) : null
      return { camada, padrao: prefixo + camada.path + '/*', params: {}, repasse: regra ? regra.nivel : null }
    }
    const sub = camada.handle && camada.handle.stack
    if (!sub) continue
    const resto = caminho.slice(camada.path.length) || '/'
    const achou = acharRota(sub, resto, metodo, prefixo + camada.path)
    if (achou) {
      achou.params = { ...camada.params, ...achou.params }
      return achou
    }
  }
  return null
}

const validar = (achou, chamada) => {
  const erros = []
  const query = Object.fromEntries(new URLSearchParams(chamada.query || ''))
  for (const item of achou.camada.route.stack) {
    const mw = item.handle
    if (!mw || !mw.__schemas) continue
    const req = {
      method: chamada.metodo,
      originalUrl: chamada.caminho,
      body: chamada.corpo === null || chamada.corpo === undefined ? undefined : JSON.parse(JSON.stringify(chamada.corpo)),
      query,
      params: { ...achou.params },
      headers: {}
    }
    let erro = null
    mw(req, {}, e => { if (e) erro = e })
    if (erro) erros.push(erro.message || String(erro))
  }
  return erros
}

const chamadas = JSON.parse(fs.readFileSync(arquivoChamadas, 'utf8'))
const saida = chamadas.map(chamada => {
  const caminho = chamada.caminho.replace(/^\/api(?=\/)/, '')
  const achou = acharRota(roteador.stack, caminho, chamada.metodo, '/api')
  if (!achou) return { ...chamada, rota: null, erro: null }
  if (!achou.camada.route) {
    return {
      ...chamada, rota: achou.padrao, joi: false, repasse: achou.repasse,
      erro: null
    }
  }
  const erros = validar(achou, chamada)
  return { ...chamada, rota: achou.padrao, joi: achou.camada.route.stack.some(i => i.handle && i.handle.__schemas), erro: erros.length ? erros.join(' | ') : null }
})

fs.writeFileSync(arquivoSaida, JSON.stringify(saida))
// O require do servidor pode deixar temporizadores e conexões preguiçosas.
setTimeout(() => process.exit(0), 50)
