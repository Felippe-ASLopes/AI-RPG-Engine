# BACKLOG DO PRODUTO: FELPINHO's RPG ENGINE (REORGANIZADO EM CASCATA)

## PARTE 1: REQUISITOS TÉCNICOS (INFRAESTRUTURA E BACKEND)

### FASE 1: Infraestrutura Core e Orquestração (Dependência Zero) [CONCLUÍDO]
* ÉPICO 1: INFRAESTRUTURA DE IA DE TEXTO (LLM)
    * História de Usuário: Como jogador, quero que a IA responda rapidamente e com boa escrita, para que a narrativa não seja interrompida.
    * Tarefa 1.1: Instalar e configurar KoboldCPP ou LM Studio com suporte a DirectML/ZLUDA para AMD.
    * Tarefa 1.2: Implementar quantização de modelos (Llama-3.1 8B em Q4_K_M) para otimizar 8GB de VRAM.
    * Tarefa 1.3: Configurar System Prompt persistente com diretrizes de estilo de RPG.
* ÉPICO 2: GESTÃO INTELIGENTE DE VRAM (ORQUESTRAÇÃO)
    * História de Usuário: Como usuário de uma GPU de 8GB, quero que o sistema alterne entre modelos de texto e imagem automaticamente para evitar travamentos do Windows.
    * Tarefa 2.1: Desenvolver script de VRAM_Optimizer para monitorar uso de memória em tempo real.
    * Tarefa 2.2: Criar rotina de "unloading" do modelo de texto após a geração do parágrafo.
* ÉPICO 18: MÓDULO DE LOG CENTRALIZADO (LOGGER)
    * História de Usuário: Como desenvolvedor, quero ver o que está acontecendo no backend em tempo real para entender o fluxo de dados e o gerenciamento de hardware.
    * Requisito Funcional 18.1 (Singleton Logger): Desenvolver um módulo único logger.py que possa ser importado em qualquer parte do projeto.
    * Requisito Funcional 18.2 (Formatação de Log): Todo log deve seguir o padrão: [HH:MM:SS:ms] [MODULO] Mensagem de Status.
    * Requisito Funcional 18.3 (Rastreabilidade de Contexto): O log deve indicar a origem do dado sem expor o conteúdo sensível.
* ÉPICO 19: GESTÃO DE CICLO DE VIDA DOS LOGS
    * História de Usuário: Como usuário, quero logs leves que não ocupem espaço desnecessário e que sejam reiniciados a cada nova aventura.
    * Requisito Funcional 19.1 (Limpeza Automática): O arquivo session.log deve ser deletado e recriado em cada inicialização do app (main.py) e em cada execução de /load [save].
    * Requisito Funcional 19.2 (Exibição Real-time): Implementar uma flag --debug ou uma janela de console paralela que faça o "tail" (leitura em tempo real) do arquivo de log conforme ele é escrito.
    * Requisito Funcional 19.3 (Otimização de Escrita): Utilizar escrita assíncrona ou buffer de log para que o registro no SSD não atrase a geração da IA (latência zero para o jogador).

### FASE 2: Motor Visual e Integração Externa (Depende da Infra Base)
* ÉPICO 5: GERAÇÃO DE IMAGEM COM COERÊNCIA (STABLE DIFFUSION)
    * História de Usuário: Como jogador, quero ver imagens dos cenários e personagens que sejam consistentes visualmente entre si.
    * Tarefa 5.1: Configurar ComfyUI em modo API.
    * Tarefa 5.2: Integrar o nó de IP-Adapter para usar a última imagem gerada como referência de estilo.
    * Tarefa 5.3: Criar pipeline de carregamento de LoRAs de identidade de personagem.
* ÉPICO 6: CONEXÃO COM O MUNDO REAL (WEB SEARCH)
    * História de Usuário: Como jogador, quero que a IA pesquise fatos reais na internet se eu interagir com locais ou eventos do mundo real.
    * Tarefa 6.1: Integrar API de busca (Serper ou DuckDuckGo) ao orquestrador.
    * Tarefa 6.2: Criar filtro de "Sanity Check" para evitar que a IA traga lixo da web para dentro do RPG.

### FASE 3: Persistência, Memória e Contexto (Depende da Infra e IA) [CONCLUÍDO]
* ÉPICO 3: SISTEMA DE CONTEXTO LOCAL E ATLAS VISUAL (ASSET BRIDGE)
    * História de Usuário: Como mestre/autor, quero que a IA utilize minhas imagens e descrições reais para manter a verossimilhança.
    * Tarefa 3.1: Criar estrutura de pastas /Assets/Scenery e /Metadata.
    * Tarefa 3.2: Desenvolver o script AssetBridge para indexar arquivos .jpg/.png e .md/.json correspondentes.
    * Tarefa 3.3: Implementar função de injeção de metadados no prompt da LLM quando palavras-chave forem detectadas.
* ÉPICO 4: MEMÓRIA DE LONGO PRAZO (RAG)
    * História de Usuário: Como jogador de sessões longas, quero que a IA lembre de decisões tomadas há semanas para que o mundo pareça vivo.
    * Tarefa 4.1: Configurar ChromaDB local para armazenamento de vetores de chat.
    * Tarefa 4.2: Ajustar o "k-nearest neighbors" (k-NN) para recuperar apenas as 3 memórias mais relevantes por turno.
* ÉPICO 12: GESTÃO DE SAVES MANUAIS (SNAPSHOTS)
    * História de Usuário: Como jogador, quero salvar momentos específicos da minha jornada em arquivos permanentes para poder explorá-los novamente depois ou evitar perdas por queda de energia.
    * Requisito Funcional 12.1 (Comando de Save): Implementar comandos de console: `/save [nome]`, com suporte à flag de substituição `/save -overwrite [nome]` ou sua forma abreviada `/save -o [nome]`.
    * Requisito Funcional 12.2 (Serialização de Contexto): O save deve conter o "Buffer de Contexto" completo (Texto + Metadados de @tags ativos + Logs de Feedback).
    * Requisito Funcional 12.3 (Persistência em Disco): O salvamento deve ser obrigatoriamente em arquivos .json ou .sqlite locais para garantir integridade pós-desligamento.
* ÉPICO 13: SISTEMA DE CARREGAMENTO E TROCA DE TIMELINE (LOAD)
    * História de Usuário: Como jogador, quero alternar entre diferentes arquivos de save durante a sessão para testar diferentes decisões.
    * Requisito Funcional 13.1 (Hot-Swap): Implementar o comando `/load [nome]`. Ao ser executado, o sistema limpa a VRAM do contexto atual e carrega o novo histórico.
    * Requisito Funcional 13.2 (Verificação de Integridade): O sistema deve validar se os modelos de IA (LLM/Diffusion) necessários para aquele save estão disponíveis antes de carregar.
* ÉPICO 35: INTEGRAÇÃO DE HOT-SWAP E LIMPEZA PROFUNDA DE CONTEXTO (PREVENÇÃO DE ALUCINAÇÃO)
    * História de Usuário: Como jogador, quero que ao carregar um save diferente, a IA esqueça completamente a sessão anterior, limpando a VRAM e os ponteiros do banco vetorial, para que histórias de campanhas distintas não se misturem.
    * Requisito Funcional 35.1 (Orquestração de Descarregamento): O `LoadManager` deve atuar como orquestrador central, injetando as dependências do `VRAMOptimizer` e `VectorMemoryAdapter`.
    * Requisito Funcional 35.2 (Flush de VRAM): Ao acionar o `/load`, o sistema deve notificar o `VRAMOptimizer` para limpar os caches do motor de texto ativo.
    * Requisito Funcional 35.3 (Isolamento de RAG): O sistema deve sinalizar ao adaptador do ChromaDB para trocar a "collection" ativa ou limpar o cache de contexto baseando-se no nome da nova campanha carregada.
* ÉPICO 38: GESTÃO DE EXCLUSÃO DE DADOS (DELETE SAVE & PRESETS)
    * História de Usuário: Como jogador, quero poder excluir campanhas antigas e presets não utilizados para liberar espaço no meu HD e manter minha interface organizada, garantindo que nenhum dado residual (como memórias no RAG) seja esquecido.
    * Requisito Funcional 38.1 (Comando de Exclusão de Save): Implementar o comando `/save -delete [nome_do_save]` ou `/save -d [nome_do_save]`. O sistema deve ler o arquivo de save para descobrir o nome da campanha, deletar a *collection* correspondente no ChromaDB e, por fim, excluir o arquivo `.json` ou `.sqlite` local.
    * Requisito Funcional 38.2 (Comando de Exclusão de Preset): Implementar o comando separado `/save -deletepreset [nome_da_entidade]` ou `/save -dp [nome_da_entidade]`. O sistema deve buscar e excluir exclusivamente o arquivo da entidade na pasta `/Global_Library`.
    * Requisito Funcional 38.3 (Segurança e Orquestração): A exclusão de um save não deve apagar os presets exportados. Além disso, o sistema deve impedir a exclusão de um save caso a campanha vinculada a ele seja a que está atualmente carregada na sessão ativa (proteção de contexto).
---

## PARTE 2: REQUISITOS FUNCIONAIS (MECÂNICAS, LÓGICA DE USUÁRIO E UI)

### FASE 4: Setup, Presets e Arquitetura de Campanha (Depende do BD/Memória) [CONCLUÍDO]
* ÉPICO 14: ASSISTENTE DE CRIAÇÃO DE CAMPANHA (THE WIZARD)
    * História de Usuário: Como jogador, quero um guia visual e textual para configurar minha ficha, NPCs e o "esqueleto" da história, para que o mundo seja coerente desde o primeiro turno.
    * Requisito Funcional 14.1 (Criação Dinâmica e Preenchimento Assistido): Todos os campos do setup de campanha são opcionais para o usuário. O jogador pode preencher o que desejar, e o sistema deve analisar os dados parciais. A IA (LLM) assumirá a responsabilidade de gerar e preencher exclusivamente os campos que foram deixados em branco, respeitando o contexto dos dados já fornecidos.
    * Requisito Funcional 14.2 (Formulários de Atributos): Cada entidade criada deve possuir campos obrigatórios no estado final: Aparência, Personalidade, Poder/Habilidade, Benefícios e Malefícios.
    * Requisito Funcional 14.3 (Roteiro de Pontos de Trama): Implementar um sistema de "Milestones" (Marcos).
* ÉPICO 15: INTEGRAÇÃO VISUAL NO SETUP
    * História de Usuário: Como mestre, quero associar imagens aos meus itens e locais durante a criação para que a IA de imagem saiba o que replicar.
    * Requisito Funcional 15.1 (Vínculo de Asset): Permitir o upload ou apontamento de caminho local para imagens de referência em cada formulário de criação.
    * Requisito Funcional 15.2 (Preview de Contexto): Exibir a imagem ao lado da ficha do personagem/item para confirmação visual do "Atlas Local".
* ÉPICO 23: SISTEMA DE PRESETS MODULARES (NESTED PRESETS)
    * História de Usuário: Como jogador, quero salvar os componentes da minha campanha de forma independente para que eu possa "reciclar" um guerreiro medieval em um cenário futurista sem esforço.
    * Requisito Funcional 23.1 (Hierarquia de Presets): Implementar salvamento em árvore (Campaign_Preset -> NPC_Presets, World_Settings, Plot_Milestones).
    * Requisito Funcional 23.2 (Cross-Campaign Loading): Permitir a importação individual de arquivos de preset.
    * Requisito Funcional 23.3 (Auto-save de Template): Ao finalizar o "Wizard" de New Game, o sistema deve gerar automaticamente um arquivo .template que congela o estado inicial.
* ÉPICO 24: BIBLIOTECA DE COMPONENTES REUTILIZÁVEIS
    * História de Usuário: Como mestre, quero uma galeria de presets salvos para que eu possa popular uma nova campanha rapidamente apenas selecionando itens de uma lista.
    * Requisito Funcional 24.1 (Global Assets): Criar uma pasta /Global_Library onde presets de personagens e locais ficam disponíveis para qualquer nova campanha iniciada.
* ÉPICO 25: CONTROLE DE TEMAS E RESTRIÇÕES (CONTENT GATING)
    * História de Usuário: Como usuário, quero definir explicitamente quais temas são permitidos ou banidos para que a IA não gere conteúdo indesejado ou desconfortável.
    * Requisito Funcional 25.1 (Switches de Temas Sensíveis): Implementar toggles (On/Off) no setup da campanha para Violência Extrema (Gore) e Conteúdo Erótico (NSFW).
    * Requisito Funcional 25.2 (Blacklist de Conceitos): Campo de texto para "Temas Banidos". Qualquer menção a esses temas deve disparar um aviso no log e forçar uma regeneração automática (/regen) silenciosa.
    * Requisito Funcional 25.3 (Hard-Prompting de Restrição): As restrições e temas desativados devem ser injetados com prioridade máxima (Negative Prompts/System Constraints) no início de cada chamada à LLM e ao gerador de imagens.

### FASE 5: Processamento de Input e Lógica Core (Depende do Setup e IA) [CONCLUÍDO]
* ÉPICO 8: PROCESSADOR DE INPUT MULTIMODAL (BLOCOS)
    * História de Usuário: Como jogador, quero separar minhas falas, ações e comandos de sistema em blocos distintos para que a IA processe cada um com a "intenção" correta.
    * Requisito Funcional 8.1 (Identificadores de Bloco): Implementar suporte a prefixos especiais: `>` (Ação), `"` (Fala), `$` (Trapaça/Override) e `#` (Feedback).
    * Requisito Funcional 8.2 (Preservação de Ordem): O motor de prompt deve concatenar os blocos de 'Falas' e 'Ações' na ordem exata em que foram digitados pelo usuário, compondo o bloco narrativo.
    * Requisito Funcional 8.3 (Independência de Blocos de Sistema): Blocos de `$` (Trapaça) e `#` (Feedback) devem ser extraídos da narrativa e injetados separadamente no "System Prompt" ou instruções de contexto adicionais.
* ÉPICO 37: ROTEADOR CENTRAL DE COMANDOS (COMMAND DISPATCHER)
    * História de Usuário: Como sistema, preciso de um ponto único (Front Controller) que intercepte os comandos do jogador (iniciados por `/`) e os direcione para os módulos corretos, evitando verificações redundantes no fluxo principal e mantendo o código escalável.
    * Requisito Funcional 37.1 (Interceptação e Parse): O sistema deve verificar se o input bruto começa com `/`. Se sim, deve quebrar os argumentos e identificar o Caso de Uso alvo.
    * Requisito Funcional 37.2 (Delegação Dinâmica): Direcionar `/load` para o `LoadManager`, `/save -e` para o `InGameEntityExport` e `/save` padrão para o `SaveManager`.
    * Requisito Funcional 37.3 (Padronização de Retorno): Devolver um objeto padronizado informando se o comando foi tratado, qual a mensagem de feedback e se o estado do jogo foi alterado (útil para o `/load`).
    para analise futura: 'Agora, quando formos criar a rota principal de chat no FastAPI, o código do controlador será maravilhosamente simples:' '# Pseudo-código do nosso futuro endpoint de chat
@router.post("/chat")
async def process_turn(request: ChatRequest):
    
    # 1. Tenta rotear como comando de sistema
    cmd_response = await command_dispatcher.dispatch(request.text, current_state)
    
    if cmd_response.is_command:
        # Se for comando (ex: /save), devolve a mensagem e NÃO chama a IA
        return {"response": cmd_response.message, "state": cmd_response.new_state}
        
    # 2. Se não for comando, segue o fluxo normal do jogo (Fase 5 -> IA)
    parsed_input = input_processor.parse_raw_input(request.text)
    # ... chama o RAG, chama a LLM ...'
* ÉPICO 9: SISTEMA DE TAGGING DE ENTIDADES (@MAPPING)
    * História de Usuário: Como jogador, quero marcar entidades (NPCs, Objetos, Locais) no meu texto para que o sistema force a recuperação de dados específicos do RAG ou do Atlas Local.
    * Requisito Funcional 9.1 (Menção Direta): Uso do caractere @ para disparar uma busca imediata no banco de dados.
    * Requisito Funcional 9.2 (Pipeline de Injeção de Contexto): O script detecta a tag, pausa a construção, busca a descrição e insere "escondida" no prompt.
    * Requisito Funcional 9.3 (Integridade de Sequência): Garantir que a IA receba o contexto na ordem correta da frase no buffer de memória.
* ÉPICO 10: ACESSO MANUAL AO RAG (THE FORCED RECALL)
    * História de Usuário: Como jogador, quero poder forçar a IA a lembrar de algo específico sem precisar esperar que ela decida pesquisar.
    * Requisito Funcional 10.1 (Comando de Memória): Implementar o caractere/comando `*` para busca profunda no RAG (ex: `* o acordo com o rei`).
    * Tarefa 10.2: Criar uma função que ignore a "similaridade semântica" padrão e faça uma busca por "exact match" no banco vetorial.
* ÉPICO 16: INJEÇÃO DIRETA DE CONTEXTO E RAG (THE OVERRIDE)
    * História de Usuário: Como administrador do jogo, quero alterar as propriedades de um objeto ou personagem instantaneamente via chat.
    * Requisito Funcional 16.1 (Sintaxe de Injeção): Implementar o prefixo `/insert` como comando de escrita direta no banco de dados/RAG.
    * Requisito Funcional 16.2 (Atualização de Memória): Ao receber o comando, sobrescrever/adicionar os novos parâmetros e limpar o cache de contexto da GPU.
    * Requisito Funcional 16.3 (Acesso Direto ao RAG): O comando +: @entidade sem parâmetros adicionais deve abrir um log rápido do que o RAG sabe sobre aquela entidade.
* ÉPICO 33: LIMITAÇÃO DE INPUT E CONFIGURAÇÕES DE HARDWARE (.ENV)
    * História de Usuário: Como administrador do sistema, quero que os limites de hardware (como VRAM total e limite de caracteres por turno) sejam configuráveis externamente, para evitar sobrecarga de memória (OOM - Out of Memory) e prevenir que o jogador envie textos excessivamente longos que quebrem a janela de contexto da IA.
    * Requisito Funcional 33.1 (Variáveis de Ambiente): O sistema deve ler configurações dinâmicas a partir de um ficheiro `.env` (ex: `TOTAL_VRAM_GB`, `MAX_INPUT_CHARACTERS`). Nenhum destes valores deve estar *hard-coded* no código-fonte.
    * Requisito Funcional 33.2 (Validação de Input): O Processador de Input deve rejeitar a requisição e lançar um erro estruturado se o texto bruto do jogador ultrapassar o `MAX_INPUT_CHARACTERS` definido.
    para analise futura: 'Quando formos escrever o Controlador (FastAPI), envolveremos a chamada do parse_raw_input num bloco try/except ValueError:. Se o jogador exagerar, o backend devolve um alerta HTTP 400 amigável com a mensagem de erro da exceção, impedindo o RAG e a IA de gastarem processamento.'

### FASE 6: Controle Narrativo e Estados (Depende do Input)
* ÉPICO 7: SISTEMA DE FEEDBACK DO JOGADOR
    * História de Usuário: Como usuário, quero poder corrigir a IA e que ela aprenda com meus feedbacks imediatamente.
    * Tarefa 7.1: Criar arquivo preferences.json para armazenar correções de tom e mecânicas.
    * Tarefa 7.2: Implementar rotina de injeção automática de "Feedback Recente" no topo do contexto da LLM.
* ÉPICO 11: SISTEMA DE DESFAZER DINÂMICO (UNDO/REWRITE)
    * História de Usuário: Como jogador, quero poder desfazer uma ação indesejada e reescrever o futuro, para que a história siga exatamente como eu planejei.
    * Requisito Funcional 11.1 (Sintaxe de Reversão): Implementar o comando << como gatilho de "rollback".
    * Requisito Funcional 11.2 (Buffer de Descarte): O sistema deve manter os últimos 5 estados em arquivos temporários .json no SSD.
    * Requisito Funcional 11.3 (Sobrescrita de Fluxo): Ao enviar um novo input após um <<, deletar a ramificação descartada e iniciar a nova narrativa a partir do ponto restaurado.
* ÉPICO 17: SISTEMA DE REGENERAÇÃO UNITÁRIA (REGEN)
    * História de Usuário: Como jogador, quero poder pedir que a IA reescreva sua última resposta ou gere uma nova imagem sem alterar meu input.
    * Requisito Funcional 17.1 (Regerar Texto): Implementar o comando `/regen -text` (ou `/regen -t`) e botão de interface que descarta a última resposta da LLM e dispara uma nova inferência com o exato mesmo contexto e input.
    * Requisito Funcional 17.2 (Regerar Imagem): Implementar o comando `/regen -img` (ou `/regen -i`) e botão de interface.  O sistema deve manter o texto da IA, mas disparar uma nova chamada ao ComfyUI.
    * Requisito Funcional 17.3 (Preservação de Input): Diferente do << (Undo), o regen não apaga o input do usuário, apenas substitui o nó de saída no histórico do chat.
* ÉPICO 32: SISTEMA DE CONSULTA AO MESTRE (ORACLE MODE)
    * História de Usuário: Como jogador, quero tirar dúvidas sobre o cenário ou regras sem avançar o tempo da história ou gerar imagens desnecessárias, para manter a consistência do meu próximo turno.
    * Requisito Funcional 32.1 (Bloqueio de Contexto Narrativo): Implementar o caractere `?` para tirar dúvidas sem avançar o turno (ex: `? qual é a fraqueza de goblins`). Ao ser acionado, o sistema congela o buffer de chat atual e impede que a resposta da IA seja escrita no arquivo de histórico da campanha.
    * Requisito Funcional 32.2 (Processamento de Baixo Custo): A consulta deve desativar o pipeline de imagem (ComfyUI) e focar apenas na recuperação de dados do RAG ou Atlas Local para responder.
    * Requisito Funcional 32.3 (Preservação de Turno): Após a resposta da IA, a interface deve restaurar exatamente o estado do input do jogador, permitindo que ele continue sua jogada original com a nova informação.
* ÉPICO 36: EXTRAÇÃO DE PRESETS EM TEMPO REAL (IN-GAME EXPORT) [CONCLUÍDO]
    * História de Usuário: Como mestre/jogador, quero poder salvar personagens, objetos ou locais criados espontaneamente pela IA durante a campanha, para reutilizá-los em outras aventuras no futuro.
    * Requisito Funcional 36.1 (Comando de Extração): Implementar o comando `/save -entity @tag` ou a sua forma abreviada `/save -e @tag`. O sistema deve isolar a requisição e não avançar o tempo da narrativa.
    * Requisito Funcional 36.2 (Recuperação RAG): O sistema deve consultar o banco vetorial (ChromaDB) e o buffer de contexto em busca de menções e descrições prévias da `@tag`.
    * Requisito Funcional 36.3 (Formatação por IA): A LLM deve receber os fragmentos de memória e formatar a entidade no padrão estruturado `EntityAttributes` (JSON). Se for um objeto/local, a IA deve adaptar criativamente os campos (ex: 'personality' vira 'comportamento mágico/atmosfera').
    * Requisito Funcional 36.4 (Persistência Automática): O resultado final validado deve ser salvo automaticamente na `/Global_Library` pelo `PresetRepository`.
    para analise futura: 'No seu controlador principal (no FastAPI), quando o usuário enviar uma mensagem, você vai fazer um parser inicial:' 'if message.startswith("!save --entity"):
    resposta = await in_game_entity_export_usecase.execute_extraction(message)
    # Exibe a resposta na tela do jogador sem avançar o turno da história'

### FASE 7: Interface de Usuário (HUD e UX) (Depende da Lógica e Estados)
* ÉPICO 20: SISTEMA DE AUTOCOMPLETE INTELIGENTE (@MAPPING)
    * História de Usuário: Como jogador, quero que a interface sugira personagens e locais enquanto eu digito, para evitar erros de digitação que quebrariam o RAG ou o Atlas Local.
    * Requisito Funcional 20.1 (Gatilho de Menção): Ao digitar @, o sistema deve abrir um menu flutuante (dropdown) com a lista de entidades indexadas.
    * Requisito Funcional 20.2 (Filtragem em Tempo Real): A lista deve ser filtrada conforme o usuário continua digitando.
    * Requisito Funcional 20.3 (Seleção Rápida): Suporte às teclas Tab ou Enter para autocompletar o termo selecionado (latência zero).
* ÉPICO 21: RECUPERAÇÃO DE BUFFER PÓS-ROLLBACK (RE-EDIT)
    * História de Usuário: Como jogador, após dar um 'Desfazer' (<<), quero que meu input anterior volte para a caixa de texto para que eu possa editá-lo sem ter que digitar tudo de novo.
    * Requisito Funcional 21.1 (Buffer de Reescrita): Ao detectar o comando <<, executar o rollback e injetar o conteúdo do último User_Input descartado de volta na área de edição.
    * Requisito Funcional 21.2 (Sugestão de Rollback): Ao digitar <<, mostrar um preview do input que será recuperado.
* ÉPICO 22: ATALHOS VISUAIS E SNIPPETS DE BLOCO
    * História de Usuário: Como jogador, quero botões e atalhos de teclado rápidos para inserir os blocos de 'Ação', 'Fala' ou 'Trapaça', para manter o ritmo da jogatina.
    * Requisito Funcional 22.1 (Quick-Actions): Implementar atalhos (ex: Ctrl + G para Fala, Ctrl + A para Ação) que inserem automaticamente os caracteres de bloco.
    * Requisito Funcional 22.2 (Interface Adaptativa): Exibir ícones discretos ao lado da caixa de input indicando qual "Modo de Bloco" está ativo no momento.
* ÉPICO 26: DASHBOARD DE STATUS E INVENTÁRIO (PLAYER HUD)
    * História de Usuário: Como jogador, quero visualizar meus atributos (Vida, Mana, Nível) e itens em uma interface auxiliar rápida para não precisar perguntar à IA o tempo todo.
    * Requisito Funcional 26.1 (Visualização de Atributos): Painel dinâmico com barras de status e lista de inventário.
    * Requisito Funcional 26.2 (Detalhamento de Entidades): Ao clicar em um item ou @NPC no HUD, abrir uma "Modal" (janela sobreposta) com Descrição, Personalidade e 'Marcos Narrativos'.
    * Requisito Funcional 26.3 (Ícones Otimizados): Suporte a ícones 64x64px com prioridade para arquivos locais em /UI/Icons/.
* ÉPICO 27: GERENCIADOR DE OBJETIVOS E INTENÇÕES (QUEST LOG)
    * História de Usuário: Como jogador, quero registrar minhas intenções e objetivos para que a história tenha um norte, mas sem que a IA dê spoilers ou force o cumprimento deles.
    * Requisito Funcional 27.1 (Diferenciação Intenção vs. Objetivo): Intenção (Curto prazo/Pensamento) e Objetivo de Campanha (Longo prazo).
    * Requisito Funcional 27.2 (Visão Subjetiva): Os textos de objetivos devem ser escritos e exibidos sob a perspectiva do personagem (conhecimento limitado).
    * Requisito Funcional 27.3 (Injeção Condicional de Contexto): O sistema de filtragem só deve injetar o objetivo no prompt da LLM se a @entidade relacionada estiver presente na cena atual.
* ÉPICO 28: CICLO DE VIDA DE OBJETIVOS
    * História de Usuário: Como jogador, quero que meus objetivos mudem de status (Concluído/Fracassado) para que a IA pare de considerá-los após o desfecho.
    * Requisito Funcional 28.1 (Trigger de Finalização): Ao detectar que um objetivo foi cumprido ou tornou-se impossível, mover o dado para o 'Histórico de Marcos' do RAG e remover do prompt ativo.
    * Requisito Funcional 28.2 (Persistência no Save): O estado do HUD e do Quest Log deve ser serializado dentro do arquivo de save manual/automático da campanha.
* ÉPICO 31: ATALHOS CONTEXTUAIS E CLICK-TO-TAG
    * História de Usuário: Como jogador, quero realizar ações comuns e marcar entidades clicando na interface, para agilizar meu combate e exploração sem digitar frases repetitivas.
    * Requisito Funcional 31.1 (Snippets de Ação): Ao abrir um bloco de "Ação", exibir botões flutuantes com verbos comuns.
    * Requisito Funcional 31.2 (Marcação por Clique): Ao clicar em qualquer elemento da Dashboard, injetar automaticamente a @tag correspondente no bloco de input ativo.
    * Requisito Funcional 31.3 (Input Zero-Type): Permitir o envio de comandos compostos apenas por cliques (Ex: [Ação] + [Atacar] + [@rival] -> Enviar).

### FASE 8: Cartografia e Features Meta-Narrativas (Depende do Jogo rodando)
* ÉPICO 29: DIÁRIO DE MARCOS NARRATIVOS (CHRONICLE LOG)
    * História de Usuário: Como jogador, quero uma lista simplificada dos grandes feitos e erros da minha campanha para revisar a história rapidamente.
    * Requisito Funcional 29.1 (Sumarização Automática): A LLM deve identificar eventos de alto impacto e extrair para um arquivo chronicle.md em tópicos.
    * Requisito Funcional 29.2 (Interface de Resumo): Exibição de uma timeline textual limpa, focada apenas em fatos consumados.
* ÉPICO 30: MAPA PROCEDURAL EVOLUTIVO (THE ATLAS)
    * História de Usuário: Como explorador, quero ver um mapa visual que se expande conforme viajo, mostrando a transição de biomas e ícones das cidades visitadas.
    * Requisito Funcional 30.1 (Geração de Tiles de Bioma): O background do mapa deve ser gerado por IA (Stable Diffusion) em "tiles" simplificados que representam a transição.
    * Requisito Funcional 30.2 (Ícones de Localidade Angulados): Gerar ícones estilo "visão de satélite angulada" para pontos de interesse e sobrepor ao mapa.
    * Requisito Funcional 30.3 (Trilha Narrativa): Conectar localidades visitadas com elementos visuais dinâmicos que indicam o caminho percorrido.
    * Requisito Funcional 30.4 (Navegação Visual): Implementar funcionalidade de Pan & Zoom na interface gráfica (Canvas/WebG) para exploração do mapa gerado.