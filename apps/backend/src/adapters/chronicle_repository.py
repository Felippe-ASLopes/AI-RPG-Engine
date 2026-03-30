from pathlib import Path
from src.infrastructure.config import AppConfig

class LocalChronicleRepository:
    """Adaptador para ler e escrever o Chronicle Log (Épico 29)."""
    
    def __init__(self, base_path: Path = AppConfig.PROJECT_ROOT / "data" / "campaigns"):
        self.base_path = base_path

    def _get_file_path(self, campaign_name: str) -> Path:
        safe_name = "".join(c if c.isalnum() else "_" for c in campaign_name).lower()
        campaign_dir = self.base_path / safe_name
        campaign_dir.mkdir(parents=True, exist_ok=True)
        return campaign_dir / "chronicle.md"

    def append_milestones(self, campaign_name: str, milestones: str):
        if not milestones.strip():
            return
            
        file_path = self._get_file_path(campaign_name)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(milestones.strip() + "\n")

    def read_chronicle(self, campaign_name: str) -> str:
        file_path = self._get_file_path(campaign_name)
        if not file_path.exists():
            return "Nenhum marco heroico foi registrado nesta campanha ainda."
            
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()