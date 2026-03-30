# DIRETRIZES DE CÓDIGO E ARQUITETURA PARA IA
# Projeto: FELPINHO's RPG ENGINE
# Objetivo: Motor de RPG de texto local com foco em otimização de VRAM (8GB) e Clean Architecture.

## 1. CONTEXTO DE HARDWARE E RESTRIÇÕES (CRÍTICO)
- **GPU Alvo:** AMD Radeon RX 7600 (8GB VRAM).
- **Proibição de CUDA:** NUNCA sugira ou escreva código que dependa exclusivamente de NVIDIA/CUDA. Utilize bibliotecas compatíveis com DirectML, Vulkan, ZLUDA ou ONNX.
- **Gerenciamento de Memória:** O sistema intercala modelos de Texto (KoboldCPP) e Imagem (ComfyUI). A VRAM nunca deve exceder 7.5GB. O código deve suportar offload/onload de modelos para a RAM do sistema.

## 2. STACK TECNOLÓGICO
- **Backend:** Python 3.10+, FastAPI.
- **Frontend:** Tauri, React, TypeScript, Tailwind CSS.
- **Bancos de Dados:** SQLite (Relacional/Saves) e ChromaDB (Vetorial/RAG).
- **IA Engines:** KoboldCPP (LLM) e ComfyUI em modo API (Stable Diffusion).

## 3. Estrutura do Monorepositório
``` plaintext
ai-rpg-engine/
├── apps/
│   ├── frontend/                 # Tauri + React + TypeScript
│   │   ├── src-tauri/            # Configurações do Rust/Tauri
│   │   └── src/                  # Código React (Componentes, Hooks, HUD)
│   │
│   └── backend/                  # FastAPI + Python
│       ├── src/
│       │   ├── domain/           # Entidades e Regras de Negócio Puras
│       │   ├── use_cases/        # Lógica de Aplicação (Fluxos)
│       │   ├── adapters/         # Repositórios, Gateways (ComfyUI/Kobold) e Controllers
│       │   └── infrastructure/   # Setup FastAPI, DI, Logger Singleton
│       ├── scripts/              # VRAM_Optimizer.py, AssetBridge.py
│       └── requirements.txt
│
├── data/                         # Camada de Dados Isolada
│   ├── sqlite/                   # Banco relacional (Saves, Presets, Configs)
│   ├── chromadb/                 # Banco vetorial (Memória de longo prazo/RAG)
│   ├── Assets/                   # Imagens e Metadados Locais
│   └── Global_Library/           # Presets reutilizáveis
│
├── docs/                         # Documentação do Projeto
│   ├── ai_instructions.md        # Diretrizes para IAs (Abaixo)
│   ├── architecture.md           # Visão Geral
│   └── backlog.md                # Requisitos Funcionais
│
└── package.json                  # Scripts globais do monorepo (ex: npm run dev:all)
```

## 4. PADRÃO DE PROJETO: CLEAN ARCHITECTURE (BACKEND)
O backend em Python DEVE respeitar rigorosamente as seguintes camadas:
- **`domain/` (Domínio):** Contém entidades (`Campaign`, `Character`, `ActionToken`) e interfaces. NÃO pode importar nada de infraestrutura, frameworks ou banco de dados.
- **`use_cases/` (Casos de Uso):** Contém a lógica de orquestração (ex: `ProcessPlayerInput`). Depende apenas do Domínio.
- **`adapters/` (Adaptadores):** Implementa as interfaces do domínio. É aqui que o código fala com o ChromaDB, SQLite, KoboldCPP e ComfyUI.
- **`infrastructure/` (Infraestrutura):** Setup do FastAPI, injeção de dependências e configuração de rotas.

## 5. CONVENÇÕES DE CÓDIGO E NOMENCLATURA

### Backend (Python)
- **Estilo:** Siga o padrão PEP 8.
- **Nomenclatura:** `snake_case` para variáveis, funções e nomes de arquivos (ex: `vram_optimizer.py`). `PascalCase` para Classes.
- **Tipagem:** O uso de Type Hints é OBRIGATÓRIO em todas as funções (ex: `def get_context(query: str) -> dict:`).
- **Logs:** Utilize sempre o módulo Singleton `logger.py` para rastreabilidade, formato: `[HH:MM:SS:ms] [MODULO] Mensagem`. Evite `print()` genéricos.
- **Centralização de Prompts:** Todos os textos de instrução para a IA (System Prompts e Templates de Usuário) DEVEM ser obrigatoriamente armazenados em `Enum` na camada de domínio (`src/domain/prompts.py`). É ESTRITAMENTE PROIBIDO fazer hard-code de strings de prompt dentro dos Casos de Uso ou Adaptadores.

### Frontend (TypeScript / React)
- **Estilo:** Componentização estrita e hooks customizados para lógica de estado.
- **Nomenclatura:** `PascalCase` para componentes React e seus arquivos (ex: `PlayerHud.tsx`). `camelCase` para funções e variáveis.
- **Tipagem:** Interfaces TypeScript obrigatórias para props e respostas de API. Evite o uso de `any`.

## 6. REGRAS DE IMPLEMENTAÇÃO DE FUNCIONALIDADES
- **Arquivos de Save:** Devem ser estritamente manipulados em formato `.json` ou `.sqlite` locais para garantir integridade.
- **Comandos de Terminal:** A lógica de parsing deve isolar blocos de Ação (`>`), Fala (`"`) e Sistema (`$`, `#`) antes de enviar para a LLM.
- **Injeção de RAG e Metadados:** Ao encontrar uma tag de entidade (`@`), o código deve buscar o contexto no banco antes da inferência da LLM e embutir os dados silenciosamente no prompt.
- **Resiliência e Assincronicidade:** Funções que chamam APIs de geração (texto ou imagem) devem ser assíncronas (`async/await`) para não travar o loop de eventos do FastAPI ou a UI do Tauri.

## 7. INSTRUÇÃO OPERACIONAL PARA O AGENTE
Antes de iniciar a escrita de qualquer código, identifique a qual camada da arquitetura ele pertence. Se for implementar uma integração externa, crie a interface no diretório `domain/` antes de codificar o adaptador em `adapters/`.

## 8. TEST-DRIVEN DEVELOPMENT (TDD)
- **Cultura de Testes:** Antes de iniciar a implementação do código fonte de qualquer novo Épico ou Funcionalidade, o agente DEVE escrever primeiro os testes unitários utilizando o framework `pytest` para backend e ? para frontend.
- **Separação de Escopo:**
  - `backend/tests/`: Contém APENAS testes unitários. As classes devem ser testadas em isolamento absoluto usando mocks para repositórios ou dependências externas.
  - `backend/tests/integrated/`: Contém testes de integração e orquestração. Verifica se Casos de Uso (Use Cases) estão acionando corretamente os Adaptadores (Adapters) e serviços externos (VRAM, Bancos de Dados).
- **Cobertura Mínima:** Os testes devem cobrir fluxos de sucesso e fluxos de exceção (ex: arquivo não encontrado, limite excedido).
- **Assincronicidade:** Testes de rotinas assíncronas devem utilizar o decorador `@pytest.mark.asyncio`.

## 9. VARIÁVEIS DE AMBIENTE E CONFIGURAÇÃO (.ENV)
- **Proibição de Hard-Code:** É estritamente proibido utilizar valores fixos (hard-coded) no código para URLs de API, portas, caminhos de diretórios (paths) ou limites de hardware.
- **Centralização:** Todas as variáveis do `.env` devem ser tipadas e mapeadas na classe `AppConfig` localizada em `src/infrastructure/config.py`. As demais camadas devem importar esta classe para ler configurações.
- **Resolução de Caminhos (Paths):** Evite utilizar retrocessos como `../../` em strings de diretório. Configure os caminhos de forma limpa no `.env` (ex: `data/chromadb`) e utilize a constante `AppConfig.PROJECT_ROOT` para resolver o caminho absoluto dinamicamente.
- **Pureza do Domínio:** A camada de `domain/` NUNCA deve importar `AppConfig` ou `os.getenv`. Se uma entidade de domínio precisar de um valor padrão vindo do `.env` (como as flags de Gore/NSFW), esse valor deve ser injetado pelo Caso de Uso (Use Case) durante a sua instanciação.