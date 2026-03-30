from src.domain.command_response import CommandResponse
from src.infrastructure.logger import get_logger

logger = get_logger("DISPATCHER")

class CommandDispatcherUseCase:
    """
    Épico 37: Roteador Central de Comandos.
    Intercepta strings iniciadas por '/' e roteia para os módulos corretos utilizando Pattern Matching.
    """
    def __init__(self, save_manager, load_manager, entity_export, direct_injection, delete_manager, undo_manager, regen_manager, quest_manager, hud_manager, chronicle_manager, map_manager, web_search_manager):
        self.save_manager = save_manager
        self.load_manager = load_manager
        self.entity_export = entity_export
        self.direct_injection = direct_injection
        self.delete_manager = delete_manager
        self.undo_manager = undo_manager
        self.regen_manager = regen_manager
        self.quest_manager = quest_manager
        self.hud_manager = hud_manager
        self.chronicle_manager = chronicle_manager
        self.map_manager = map_manager
        self.web_search_manager = web_search_manager

    async def dispatch(self, raw_input: str, current_state) -> CommandResponse:
        text = raw_input.strip()

        # INTERCEPTAÇÃO DO ÉPICO 11
        if text == "<<":
            if not current_state:
                return CommandResponse(is_command=True, message="[SISTEMA] Nenhuma campanha ativa.")
                
            msg, new_state, restored_input = await self.undo_manager.execute_undo(current_state.campaign_name)
            return CommandResponse(
                is_command=True, 
                message=msg, 
                new_state=new_state, 
                restored_input=restored_input # Retorna ao HUD
            )
        
        # 1. Verificação rápida: É um comando de sistema?
        if not text.startswith("/"):
            return CommandResponse(is_command=False)

        parts = text.split()
        root_command = parts[0].lower()
        
        logger.info(f"Comando de sistema interceptado: {root_command}")

        # 2. Roteamento utilizando o switch-case do Python (match-case)
        match root_command:
            
            case "/load":
                msg, new_state = await self.load_manager.execute_load(text)
                return CommandResponse(is_command=True, message=msg, new_state=new_state)

            case "/save":
                # Verifica se há flags adicionais no comando /save
                if len(parts) > 1:
                    flag = parts[1].lower()
                    
                    # Extração de Entidade
                    if flag in ["-e", "-entity"]:
                        msg = await self.entity_export.execute_extraction(text)
                        return CommandResponse(is_command=True, message=msg)
                    
                    # Módulo de Exclusão (Saves e Presets)
                    elif flag in ["-delete", "-d", "-deletepreset", "-dp"]:
                        msg = self.delete_manager.execute_delete(text, current_state)
                        return CommandResponse(is_command=True, message=msg)
                
                # Se não bateu com nenhuma das flags acima (ou se foi só "/save meujogo"), 
                # roda o save de progresso normal
                msg = self.save_manager.execute_save(text, current_state)
                return CommandResponse(is_command=True, message=msg)

            case "/insert":
                msg = self.direct_injection.execute_injection(text)
                return CommandResponse(is_command=True, message=msg)

            case "/regen":
                if self.regen_manager:
                    msg, new_state, regen_type = self.regen_manager.execute_regen(text, current_state)
                    return CommandResponse(
                        is_command=True, 
                        message=msg, 
                        new_state=new_state, 
                        regen_type=regen_type # Sinal para a API
                    )
                else:
                    return CommandResponse(is_command=True, message="[ERRO] Regen Manager não configurado.")

            case "/quest":
                if self.quest_manager:
                    msg = self.quest_manager.execute_command(text, current_state)
                    # new_state = current_state pois o objeto já foi mutado em memória
                    return CommandResponse(is_command=True, message=msg, new_state=current_state)
                else:
                    return CommandResponse(is_command=True, message="[ERRO] Quest Manager não configurado.")

            case "/hud":
                if self.hud_manager:
                    msg = self.hud_manager.execute_command(text, current_state)
                    return CommandResponse(is_command=True, message=msg, new_state=current_state)
                else:
                    return CommandResponse(is_command=True, message="[ERRO] Hud Manager não configurado.")

            case "/chronicle":
                if self.chronicle_manager:
                    msg = await self.chronicle_manager.execute_command(text, current_state)
                    return CommandResponse(is_command=True, message=msg, new_state=current_state)
                else:
                    return CommandResponse(is_command=True, message="[ERRO] Chronicle Manager não configurado.")

            case "/map":
                if self.map_manager:
                    msg = self.map_manager.execute_command(text, current_state)
                    return CommandResponse(is_command=True, message=msg, new_state=current_state)
                else:
                    return CommandResponse(is_command=True, message="[ERRO] Map Manager não configurado.")

            # NOVO: Roteamento do Épico 6 (Web Search)
            case "/search":
                if self.web_search_manager:
                    msg = await self.web_search_manager.execute_command(text, current_state)
                    return CommandResponse(is_command=True, message=msg, new_state=current_state)
                else:
                    return CommandResponse(is_command=True, message="[ERRO] Web Search Manager não configurado.")

            case _: # O underline (_) funciona como o 'default' num switch-case padrão
                logger.warning(f"Comando desconhecido: {root_command}")
                return CommandResponse(
                    is_command=True, 
                    message=f"[SISTEMA] Comando desconhecido: '{root_command}'. Digite /help para listar comandos válidos."
                )