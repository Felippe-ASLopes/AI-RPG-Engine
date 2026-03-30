import re
from src.domain.save_state import SaveState
from src.domain.player_hud import InventoryItem
from src.infrastructure.logger import get_logger

logger = get_logger("HUD_MANAGER")

class HudManagerUseCase:
    """
    Controla o Épico 26: Manipulação de Status e Inventário em memória.
    Estes comandos são geralmente enviados pelo Frontend (UI) de forma automatizada.
    """
    
    def execute_command(self, command: str, current_state: SaveState) -> str:
        if not current_state:
            return "[SISTEMA] Nenhuma campanha ativa."

        parts = command.strip().split()
        if len(parts) < 3 or parts[0] != "/hud":
            return "[SISTEMA] Formato inválido. Use /hud stat [atributo] [valor] ou /hud item [add/remove] [nome]."

        category = parts[1].lower()

        # FLUXO 1: STATUS (Vida, Mana, Level)
        # Ex: /hud stat hp 80
        if category in ["stat", "stats"]:
            attribute = parts[2].lower()
            try:
                value = int(parts[3])
            except (IndexError, ValueError):
                return "[SISTEMA] Valor numérico inválido para o status."

            if hasattr(current_state.stats, attribute):
                setattr(current_state.stats, attribute, value)
                logger.info(f"Status '{attribute}' atualizado para {value}.")
                return f"[SISTEMA] Status {attribute.upper()} atualizado para {value}."
            else:
                return f"[SISTEMA] Atributo desconhecido: {attribute}"

        # FLUXO 2: INVENTÁRIO (Adicionar, Remover)
        # Ex: /hud item add "Espada de Ferro" 1
        elif category == "item":
            action = parts[2].lower()
            
            # Extrai o nome do item entre aspas
            match = re.search(r'"([^"]*)"', command)
            if not match:
                return '[SISTEMA] O nome do item deve estar entre aspas duplas. Ex: "Poção".'
            
            item_name = match.group(1)

            if action == "add":
                # Tenta capturar a quantidade após as aspas, padrão é 1
                quantity = 1
                try:
                    remainder = command.split(f'"{item_name}"')[-1].strip()
                    if remainder:
                        quantity = int(remainder.split()[0])
                except ValueError:
                    pass 

                new_item = InventoryItem(name=item_name, quantity=quantity)
                current_state.inventory.append(new_item)
                logger.info(f"Item '{item_name}' (x{quantity}) adicionado ao inventário.")
                return f"[SISTEMA] Item '{item_name}' adicionado ao inventário."

            elif action in ["remove", "rm"]:
                item_to_remove = next((i for i in current_state.inventory if i.name.lower() == item_name.lower()), None)
                if item_to_remove:
                    current_state.inventory.remove(item_to_remove)
                    logger.info(f"Item '{item_name}' removido.")
                    return f"[SISTEMA] Item '{item_name}' removido do inventário."
                return f"[SISTEMA] Item '{item_name}' não encontrado no inventário."

        return "[SISTEMA] Comando de HUD desconhecido."