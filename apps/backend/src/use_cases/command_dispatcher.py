from src.domain.command_response import CommandResponse
from src.infrastructure.logger import get_logger

logger = get_logger("DISPATCHER")

class CommandDispatcherUseCase:
    """
    Épico 37: Roteador Central de Comandos.
    Intercepta strings iniciadas por '/' e roteia para os módulos corretos utilizando Pattern Matching.
    """
    def __init__(self, save_manager, load_manager, entity_export, direct_injection, delete_manager):
        self.save_manager = save_manager
        self.load_manager = load_manager
        self.entity_export = entity_export
        self.direct_injection = direct_injection
        self.delete_manager = delete_manager

    async def dispatch(self, raw_input: str, current_state) -> CommandResponse:
        text = raw_input.strip()
        
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

            case _: # O underline (_) funciona como o 'default' num switch-case padrão
                logger.warning(f"Comando desconhecido: {root_command}")
                return CommandResponse(
                    is_command=True, 
                    message=f"[SISTEMA] Comando desconhecido: '{root_command}'. Digite /help para listar comandos válidos."
                )