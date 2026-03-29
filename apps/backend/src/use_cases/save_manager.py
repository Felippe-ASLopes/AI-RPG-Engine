from src.domain.save_state import SaveState
from src.adapters.save_repository import JsonSaveRepository
from src.infrastructure.logger import get_logger

logger = get_logger("SAVE_MANAGER")

class SaveManager:
    """
    Gerencia a lógica do Épico 12: Criação de Snapshots manuais da narrativa.
    """
    def __init__(self, repository: JsonSaveRepository):
        self.repository = repository

    def execute_save(self, command: str, current_state: SaveState) -> str:
        """
        Interpreta o comando do terminal e aciona a persistência.
        Ex: '!save final_boss' ou '!save --overwrite final_boss'
        """
        parts = command.strip().split()
        
        if len(parts) < 2 or parts[0] != "!save":
            logger.debug("Comando de save mal formatado.")
            return "Erro: Formato inválido. Use !save [nome] ou !save --overwrite [nome]."
        
        overwrite = "--overwrite" in parts
        # O nome do arquivo será a última palavra do comando
        filename = parts[-1]
        
        success = self.repository.save(filename, current_state, overwrite)
        
        if success:
            return f"[SISTEMA] Progresso salvo com sucesso como '{filename}'."
        else:
            return f"[SISTEMA] Falha ao salvar. O arquivo '{filename}' já existe. Adicione --overwrite para substituir."