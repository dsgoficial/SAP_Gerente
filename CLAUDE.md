# CLAUDE.md - SAP_Gerente

## Visão Geral

Plugin QGIS para gerenciamento de produção cartográfica do Exército Brasileiro (DSG).
Gerencia atividades, unidades de trabalho, perfis, workflows e integração com SAP backend.

## Stack

- **QGIS 4.0+** / PyQt6 / Python 3
- **REST API** do **SAP 3.0** (via `requests`), e só dele: a 2.0.0 não fala com o SAP 2.3.5
- **PostgreSQL/PostGIS** (via `psycopg2`)
- **FME** (integração opcional)

## Estrutura do Projeto

```
SAP_Gerente/
├── main.py                  # Entry point do plugin (classFactory)
├── config.py                # Constantes de configuração
├── controllers/
│   └── mToolCtrl.py         # Controller principal (~1400 linhas)
├── factories/               # Singletons e factories globais
│   ├── dockDirector.py      # Builder do dock widget
│   └── widgetFactory.py     # Instanciação de dialogs
├── functionsSettings/       # Registro de funções de workflow
├── modules/
│   ├── sap/api/sapHttp.py   # Cliente REST do SAP (~3000 linhas)
│   ├── qgis/                # Camada de integração QGIS
│   ├── fme/                 # Integração FME
│   ├── databases/           # Abstração PostgreSQL
│   ├── dsgTools/            # Processing launchers
│   ├── versionamento/       # CÓPIA do provedor do SAP Operador (não edite aqui)
│   └── utils/               # Mensagens e utilitários
├── widgets/                 # 100+ dialogs especializados
├── uis/                     # Arquivos Qt Designer (.ui)
├── rules/                   # Templates de regras
├── tests/versionamento/     # Fumaça no QGIS 4 real, servidor falso e conferidores
└── .dev/                    # Setup de dev e copiar_versionamento.py
```

## Convenções de Código

- **Classes:** `PascalCase` (ex: `LoadWorkUnit`, `ErrorMessageBox`)
- **Métodos:** `camelCase` (ex: `getActivityDataById`, `loadProjects`)
- **Constantes:** `UPPER_SNAKE_CASE` (ex: `SSL_VERIFY`, `TIMEOUT`)
- **Interfaces:** prefixo `I` (ex: `IQgisCtrl`, `IMessage`)
- **Singletons:** sufixo `Singleton` (ex: `LoginSingleton`)
- **Factories:** sufixo `Factory` (ex: `WidgetFactory`)
- **Dialogs gerenciais:** prefixo `M` (ex: `MStyles`, `MRules`)
- **Imports:** absolutos com caminho completo (`from SAP_Gerente.modules...`)
- **Idioma:** português brasileiro em UI, commits e nomes de configuração
- **Sem type hints** nem docstrings extensivas

## Padrões Arquiteturais

- **Factory:** WidgetFactory, MessageFactory, MapFunctionsFactory
- **Singleton:** Login, API clients, Settings (via factories/)
- **Builder:** DockDirector + MDockBuilder para dock widget
- **MVC:** Controllers em controllers/, Views em widgets/, Models em dataModels/
- **Interface contracts:** Classes abstratas com prefixo `I`

## Comandos Úteis

```bash
# Setup de dev (Windows)
.dev/setup_dev_windows.bat

# Ver mudanças
git diff

# Branch viva (QGIS 4 / Qt6): é daqui que se ramifica
git checkout qgis4

# Branch antiga (QGIS 3 / PyQt5), congelada
git checkout master
```

## Git

- **Branch viva:** `qgis4` (QGIS 4 / Qt6, contrato do SAP 2.3.5). Todo trabalho novo sai daqui.
- **`sap3`:** a 2.0.0, porte para o contrato do SAP 3.0 (só QGIS 4), saída da `qgis4`.
- **`master`:** congelado na 1.31.6 (PyQt5, último commit 2026-02-26). Não corrija bugs nele: parte do que está lá já foi consertado na `qgis4`.
- **Commits:** em português, com referência a versão (ex: "1.31.6 - alteração fluxo")
- **Sem CI/CD.** O núcleo do wizard (`modules/sap/wizard/`) é escrito sem Qt e sem HTTP para poder ser exercitado fora do QGIS, e `tests/versionamento/` tem a suíte do plugin (seção "Versionamento" abaixo).

## Contrato do servidor (SAP 3.0)

A fonte da verdade é o router e os schemas Joi do servidor SAP 3.0 (repositório `controle_acervo`,
`server/src/routes.js` e as pastas `producao/`, `gerencia_producao/`, `acompanhamento_producao/`,
`perigo/`, `metadado/`, `microcontrole/`, `projeto/`, `login/`), e o porquê de cada quebra está em
`docs/decisoes.md` de lá ("Os plugins sobem em LOCKSTEP com o servidor").

- **O validador do servidor é ESTRITO:** chave desconhecida no corpo vira 400. O SAP 2.3.5 descartava
  a chave calado, então corpo que reenvia a linha lida do GET (com `id` e nomes de exibição) quebra
  aqui. Monte o item só com os campos do schema de criação.
- Prefixos: `/api/producao/*` (era `/api/projeto/*`) e `/api/gerencia_producao/*` (era `/api/gerencia/*`).
  `perfil_producao*` e `perfil_bloco_operador` viraram `habilitacao`, `habilitacao_etapa`,
  `habilitacao_usuario` e `habilitacao_bloco`.
- Pessoa é `usuario_uuid` (e `uuid` em `/api/usuarios`, que é só do administrador). A lista de usuários
  do gerente que não é administrador é montada em `sapHttp._usuariosDoGerente`. Telas exibem `rotulo`.
- Projeto e lote são do ACERVO (`/api/projetos/projeto`, `/api/projetos/lote`, perfil no módulo
  Acervo); o lote não tem linha de produção, escala nem nome abreviado, e o par (lote, linha) nasce da
  etapa. Quem não lê o acervo recebe os seletores do acompanhamento (`sapHttp.leAcervo`).
- Status é `status_execucao_id` (`dominio.tipo_status_execucao`); "em andamento" é não encerrado
  (`contrato.emAndamento`, encerrado é 3 e 4).
- Metadado aponta a VERSÃO (`versao_id`), e não o produto.
- Login (`POST /api/login`, cliente `sap_fg`): aceita administrador ou perfil 3 (gerente) em `producao`;
  só versão de servidor com major `3`. Token vencido é 401; 403 é falta de perfil.
- O que não atravessou responde por `contrato.naoDisponivel` (em `sapHttp.py`) e por
  `dockDirector.indisponivel` (no painel), com o motivo: produtos, PIT, relatórios de `/rh`,
  projeto QGIS de acompanhamento, importação e sincronização de usuários, varreduras de produto e lote.
  O campo da base versionada atravessou (seção seguinte).

## Versionamento (base versionada, dado de produção tipo 4)

Contrato: `versionamento/docs/contrato-sap.md` do `controle_acervo` (seções 5, 7 e 9). O QGIS fala só
com o SAP: o ciclo é rota do SAP (`/api/versionamento/*`) e o serviço é alcançado pelo repasse
`/api/versionamento/servico/*`. Código em `widgets/versionamento.py`, `sapHttp.py` (fim do arquivo) e
`contrato.py`.

- **Ciclo do gerente:** Versionar Lote, Versionar Bloco e Acompanhar Versionamento (tarefa longa em
  QgsTask, descarte com motivo); Criar Integração do Bloco (`POST /bloco/:id/integracao`, merge do
  bloco no lote) e Criar Integração do Lote (`POST /lote/:id/integracao`, merge do lote na base), as
  duas com `{subfase_id, dado_producao_id?}`. Releases e funções da base ficam no SAP web e no CLI.
- **Campo do tipo 4 (SAP Local):** o GeoPackage de campo é o PRÓPRIO clone da atividade no serviço,
  em arquivo. "Configurar SAP Local" confere o banco local, chama `iniciar_modo_local` (que cria o
  clone e o marca em campo), relê o pacote (antes dele o `repo_id` vem nulo) e baixa
  `GET /versionamento/atividade/:id/campo` em fluxo para a pasta escolhida; o pacote em
  `public.sap_local` guarda só `versionamento.arquivo` (o nome) e `versionamento.sha256`.
  "Finalizar SAP Local" sobe o arquivo (`POST .../campo`, binário em fluxo) e SÓ ENTÃO chama
  `finalizar_modo_local`; `field_diverged`, `field_tampered` e `campo_pendente` viram mensagem, e o 409
  `conflito_versionamento` abre o `ConflictDialog` do módulo comum na sessão do `repo_id` do 409. A
  devolução aceita grava `enviado_sha256` no pacote local, para a finalização repetida não subir o
  mesmo arquivo de novo.
- **Sem segredo no banco local:** `contrato.pacoteParaSAPLocal` tira o login e a senha do gerente e a
  senha do banco local antes de gravar o pacote; o SAP Operador repõe `local_db` no próprio login.
- **O provedor é cópia:** `modules/versionamento/` vem de `SAP_Operador/modules/versionamento/` por
  `python .dev/copiar_versionamento.py`, que grava `manifesto.json` (commit de origem e SHA-256 de
  cada arquivo, com fim de linha LF). Nunca edite a cópia: mude no Operador e rode o script.
  `tests/versionamento/conferir_copia_versionamento.py` confere a cópia contra o manifesto e contra o
  irmão (`--provar` degrada e exige reprovação).
- **Testes:** `QT_QPA_PLATFORM=offscreen "<QGIS 4>/bin/python-qgis.bat" tests/versionamento/fumaca_painel.py --saida <json>`
  abre cada ação do painel e roda os cenários contra `servidor_falso.py` (`--plugin <outra pasta
  SAP_Gerente>` roda os mesmos cenários contra outra versão, para provar que reprovam).
  `conferir_chamadas.py --fumaca <json> --servidor <controle_acervo/server>` confere cada chamada no
  roteador e nos Joi reais, e `provar_conferidor.py` degrada o registro e exige reprovação (rode com
  `PYTHONIOENCODING=utf-8` no console do Windows). Uma instância de QGIS por vez.

## Pontos de Atenção

- `sapHttp.py` e `mToolCtrl.py` são os arquivos mais críticos e extensos
- SSL verification está desabilitado (`SSL_VERIFY=False`)
- O plugin suporta modo local (SAP Local) para operação offline
- Widget factory cria 100+ dialogs dinamicamente — verificar `widgetFactory.py` ao adicionar novos
- `functionsSettings.py` registra todas as funções de workflow — atualizar ao criar novas
