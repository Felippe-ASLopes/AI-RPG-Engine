import json
import time
from pathlib import Path
from src.domain.undo_snapshot import UndoSnapshot
from src.infrastructure.logger import get_logger
from src.infrastructure.config import AppConfig

logger = get_logger("UNDO_REPO")

class JsonUndoRepository:
    """
    Adaptador para gerenciar a fila rotativa de snapshots temporários no SSD.
    Mantém no máximo os últimos 5 turnos de descarte.
    """
    def __init__(self, base_data_path: Path = AppConfig.PROJECT_ROOT / "data"):
        self.temp_path = base_data_path
        self._ensure_directory()

    def _ensure_directory(self):
        self.temp_path.mkdir(parents=True, exist_ok=True)

    def _get_files_for_campaign(self, campaign_name: str) -> list[Path]:
        safe_name = "".join(c if c.isalnum() else "_" for c in campaign_name).lower()
        files = list(self.temp_path.glob(f"undo_buffer_{safe_name}_*.json"))
        # Ordena pelo arquivo mais antigo primeiro
        files.sort(key=lambda f: f.stat().st_mtime)
        return files

    def save_snapshot(self, campaign_name: str, snapshot: UndoSnapshot):
        safe_name = "".join(c if c.isalnum() else "_" for c in campaign_name).lower()
        files = self._get_files_for_campaign(campaign_name)

        # Regra de Negócio 11.2: Manter apenas os últimos 5 estados
        if len(files) >= 5:
            try:
                files[0].unlink()
                logger.debug("Removido snapshot mais antigo (limite de 5 alcançado).")
            except Exception as e:
                logger.error(f"Falha ao apagar snapshot antigo: {e}")

        # Utiliza timestamp para garantir ordem cronológica no nome do arquivo
        timestamp = int(time.time() * 1000)
        new_file = self.temp_path / f"undo_buffer_{safe_name}_{timestamp}.json"

        try:
            with open(new_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot.model_dump(), f, indent=4, ensure_ascii=False)
            logger.debug(f"Snapshot de Undo salvo com sucesso: {new_file.name}")
        except Exception as e:
            logger.error(f"Erro ao escrever snapshot temporário no disco: {e}")

    def pop_last_snapshot(self, campaign_name: str) -> UndoSnapshot | None:
        """Lê e exclui imediatamente o último estado salvo (Pop)."""
        files = self._get_files_for_campaign(campaign_name)
        
        if not files:
            logger.debug(f"Buffer de Undo vazio para a campanha '{campaign_name}'.")
            return None

        last_file = files[-1]
        try:
            with open(last_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            snapshot = UndoSnapshot(**data)
            last_file.unlink() 
            
            logger.info(f"Snapshot recuperado e deletado fisicamente: {last_file.name}")
            return snapshot
            
        except Exception as e:
            logger.error(f"Erro ao processar o último snapshot: {e}")
            return None