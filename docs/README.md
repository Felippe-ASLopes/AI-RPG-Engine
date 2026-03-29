# DOCUMENTAÇÃO DE ARQUITETURA: FELPINHO's RPG ENGINE

## 1. VISÃO GERAL
O FELPINHO's RPG Engine é um sistema de RPG de texto de codificação local e modular, projetado para rodar em hardware doméstico. O objetivo é criar uma experiência imersiva de longa duração com memória persistente, coerência visual e acesso híbrido a dados (Local, RAG e Web).

## 2. ESPECIFICAÇÕES DE HARDWARE (TARGET)
- **CPU:** AMD Ryzen 7 5700X (8 Cores/16 Threads)
- **GPU:** AMD Radeon RX 7600 8GB VRAM (Interface: DirectML / ZLUDA / Vulkan)
- **RAM:** 32GB DDR4
- **OS:** Windows 11 Nativo

## 3. PADRÃO DE PROJETO E ARQUITETURA
O projeto utiliza a **Clean Architecture** para garantir que as regras do RPG fiquem estritamente separadas das implementações de infraestrutura.
- **Domain (Entidades):** Regras de negócio puras (ex: lógicas de Pontos de Ação, Atributos de Personagens, Presets).
- **Use Cases (Casos de Uso):** O fluxo central da aplicação (ex: `LoadNestedPreset`, `ProcessMultimodalInput`, `TriggerVRAMSwap`).
- **Adapters (Adaptadores):** Camada de conexão com ferramentas externas (ex: ChromaDB, Repositórios SQLite, APIs do KoboldCPP e ComfyUI).

## 4. COMPONENTES DA INFRAESTRUTURA E TECNOLOGIAS

### A. Frontend (Interface, HUD e UX)
- **Framework:** Tauri (utilizando WebView2 nativo para otimização extrema de uso de RAM no Windows 11).
- **Tecnologias:** React com TypeScript.
- **Responsabilidade:** Renderizar o terminal de texto, Player HUD, Quest Log, mapas procedurais interativos (Canvas/WebGL) e formulários dinâmicos de setup.

### B. Backend (Orquestração e Lógica de Negócio)
- **Framework:** Python utilizando FastAPI.
- **Responsabilidade:** Servidor assíncrono para gestão do fluxo de turnos, roteamento de inputs, logger em tempo real e orquestração das APIs de inteligência artificial.
- **Banco de Dados Relacional/Estado:** SQLite (armazenamento leve e local das entidades, arquivos de configuração, inventário e preferências de jogador).
- **Banco de Dados Vetorial (RAG):** ChromaDB local para indexação semântica e recuperação de memórias de longo prazo e marcos narrativos.

### C. Backend de Texto e Visão (LLM / VLM)
- **Ferramenta:** KoboldCPP (focado em GGUF com suporte eficiente a offload em GPUs AMD).
- **Modelo LLM:** Llama-3.1-8B-Instruct ou Mistral-Nemo-12B (Q4_K_M ou Q5_K_M).
- **Responsabilidade:** Processar o System Prompt, gerenciar diálogos, interpretar intenções narrativas e formatar resumos.

### D. Backend de Imagem (Diffusion)
- **Ferramenta:** ComfyUI em modo API.
- **Modelos:** SDXL Turbo ou FLUX.1 [schnell] (FP8/GGUF).
- **Responsabilidade:** Renderizar cenários e avatares utilizando LoRA e IP-Adapter para manter a identidade dos NPCs e coerência visual entre os turnos.

## 5. SISTEMA DE CONTEXTO LOCAL (ASSETS & METADATA)
Para garantir a verossimilhança do mundo e forçar a criatividade da IA dentro de limites pré-estabelecidos, o sistema utiliza um diretório estruturado:
* **/Assets/Scenery/** e **/Assets/Characters/**: Imagens e referências visuais.
* **/Metadata/**: Arquivos JSON com `tags`, `description` técnica e `style_prompt`.
* **/Global_Library/**: Presets reutilizáveis e modulares globais de NPCs e itens.

## 6. FLUXO DE EXECUÇÃO (PIPELINE E VRAM SWAP)
1. **Captura de Input:** O Tauri (React) empacota o comando do jogador e envia para o FastAPI.
2. **Recuperação de Contexto:** * O backend consulta o **Atlas Local** e o SQLite por entidades ativas (@tags).
    * Busca no **ChromaDB** por memórias relevantes e marcos da narrativa.
    * Executa scraping na **Web** como fallback, se necessário.
3. **Construção do Prompt:** O FastAPI monta o contexto final e chama o KoboldCPP. A maior parte dos 8GB de VRAM está alocada para o modelo de texto neste momento.
4. **VRAM_Optimizer (Swap):** Após o texto finalizado, o FastAPI força a rotina de "unloading" do modelo de texto da VRAM para a memória RAM do sistema.
5. **Geração Visual:** Com a VRAM agora livre, o ComfyUI assume, carregando os nós necessários (IP-Adapter/LoRA) para gerar a imagem.
6. **Retorno:** A VRAM é devolvida ao KoboldCPP, e o frontend atualiza a tela com a nova narrativa e imagem.

## 7. PRINCIPAIS FUNÇÕES E MÓDULOS (ADAPTADOS PARA CLEAN ARCHITECTURE)
- **`AssetBridgeAdapter`**: Escaneia diretórios e extrai descrições para injeção dinâmica no prompt.
- **`VectorMemoryAdapter`**: Centraliza a comunicação de persistência e *exact matches* com o ChromaDB.
- **`VRAM_Optimizer`**: Script em Python que monitora e orquestra o gargalo entre KoboldCPP e ComfyUI para evitar sobrecarga na placa de vídeo.
- **`Logger`**: Módulo singleton em Python para rastreabilidade de eventos no console, rodando sem impacto na latência do jogador.

## 8. RESTRIÇÕES E TRATAMENTO DE ERROS
- **Limite de VRAM (Hard Constraint):** O uso da GPU não pode exceder 7.5GB. O uso simultâneo de texto e imagem de alta qualidade deve ser bloqueado pelo orquestrador.
- **Compatibilidade:** O código de IA deve evitar dependências exclusivas de CUDA, priorizando Vulkan, DirectML ou ZLUDA para compatibilidade nativa com a RX 7600.
- **Latência de Swap:** O Tauri precisará gerenciar estados visuais de carregamento enquanto os pesos dos modelos são transferidos entre RAM e VRAM durante os turnos.