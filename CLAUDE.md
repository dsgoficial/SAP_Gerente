# CLAUDE.md - SAP_Gerente

## Visão Geral

Plugin QGIS para gerenciamento de produção cartográfica do Exército Brasileiro (DSG).
Gerencia atividades, unidades de trabalho, perfis, workflows e integração com SAP backend.

## Stack

- **QGIS 4.0+** / PyQt6 / Python 3
- **REST API** (SAP backend via `requests`)
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
│   └── utils/               # Mensagens e utilitários
├── widgets/                 # 100+ dialogs especializados
├── uis/                     # Arquivos Qt Designer (.ui)
└── rules/                   # Templates de regras
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

# Branch principal de produção
git checkout master

# Branch QGIS 4
git checkout qgis4
```

## Git

- **Branch principal:** `master`
- **Branch atual (QGIS 4):** `qgis4`
- **Commits:** em português, com referência a versão (ex: "1.31.6 - alteração fluxo")
- **Sem CI/CD** nem testes automatizados

## Pontos de Atenção

- `sapHttp.py` e `mToolCtrl.py` são os arquivos mais críticos e extensos
- SSL verification está desabilitado (`SSL_VERIFY=False`)
- O plugin suporta modo local (SAP Local) para operação offline
- Widget factory cria 100+ dialogs dinamicamente — verificar `widgetFactory.py` ao adicionar novos
- `functionsSettings.py` registra todas as funções de workflow — atualizar ao criar novas
