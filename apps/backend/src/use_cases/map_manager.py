import re
from typing import Optional
from src.domain.save_state import SaveState
from src.domain.map_state import MapNode, MapConnection
from src.infrastructure.logger import get_logger

logger = get_logger("MAP_MANAGER")

class MapManagerUseCase:
    """
    Orquestra o Épico 30: Mapa Procedural e Trilha Narrativa.
    Responsável por gerir a topologia do mundo no backend.
    """
    def __init__(self, image_adapter=None):
        self.image_adapter = image_adapter # No futuro: chamará o ComfyUI

    def execute_command(self, command: str, current_state: SaveState) -> str:
        if not current_state:
            return "[SISTEMA] Nenhuma campanha ativa."

        parts = command.strip().split()
        if len(parts) < 3 or parts[0] != "/map":
            return '[SISTEMA] Formato inválido. Use /map discover "Nome" "Bioma" ou /map travel "Nome".'

        action = parts[1].lower()

        # FLUXO 1: DESCOBRIR NOVO LOCAL (/map discover "Nome" "Bioma")
        if action == "discover":
            # Extrai os textos entre aspas (espera 2 blocos: "Nome" "Bioma")
            matches = re.findall(r'"([^"]*)"', command)
            if len(matches) < 2:
                return '[SISTEMA] Deve informar o nome e o bioma entre aspas. Ex: /map discover "Caverna" "Gelo".'
            
            location_name = matches[0]
            biome_name = matches[1]

            # Verifica se já existe para evitar duplicados
            existing_node = next((n for n in current_state.atlas.nodes if n.name.lower() == location_name.lower()), None)
            if existing_node:
                return f"[SISTEMA] O local '{location_name}' já existe no Atlas."

            # Simulação de geração de imagens via ComfyUI (Requisitos 30.1 e 30.2)
            tile_path, icon_path = None, None
            if self.image_adapter:
                try:
                    logger.info(f"Gerando assets visuais (Tile e Ícone) para '{location_name}'...")
                    tile_path, icon_path = self.image_adapter.generate_map_assets(location_name, biome_name)
                except Exception as e:
                    logger.error(f"Erro na geração de assets do mapa: {e}")

            # Deslocamento básico para o frontend renderizar (Simulação simples de coordenadas)
            prev_x, prev_y = 0.0, 0.0
            if current_state.atlas.current_location_id:
                prev_node = next((n for n in current_state.atlas.nodes if n.id == current_state.atlas.current_location_id), None)
                if prev_node:
                    prev_x, prev_y = prev_node.x, prev_node.y

            new_node = MapNode(
                name=location_name, 
                biome=biome_name,
                x=prev_x + 10.0, # Incremento fictício para expandir o mapa visualmente
                y=prev_y + 5.0,
                tile_image_path=tile_path,
                icon_image_path=icon_path
            )
            
            current_state.atlas.nodes.append(new_node)
            
            # Requisito 30.3 (Trilha Narrativa): Se o jogador já estava noutro local, criar conexão
            if current_state.atlas.current_location_id:
                connection = MapConnection(
                    from_node_id=current_state.atlas.current_location_id,
                    to_node_id=new_node.id
                )
                current_state.atlas.connections.append(connection)
                logger.debug(f"Trilha narrativa criada de '{current_state.atlas.current_location_id}' para '{new_node.id}'.")

            # Atualiza a posição atual
            current_state.atlas.current_location_id = new_node.id
            logger.info(f"Local descoberto: {location_name} ({biome_name}).")
            return f"[SISTEMA] Novo local descoberto e mapeado: '{location_name}'."

        # FLUXO 2: VIAJAR PARA LOCAL CONHECIDO (/map travel "Nome")
        elif action == "travel":
            match = re.search(r'"([^"]*)"', command)
            if not match:
                return '[SISTEMA] Informe o destino entre aspas. Ex: /map travel "Vila Inicial".'
            
            destination_name = match.group(1)
            target_node = next((n for n in current_state.atlas.nodes if n.name.lower() == destination_name.lower()), None)
            
            if not target_node:
                return f"[SISTEMA] O local '{destination_name}' não foi encontrado no seu Atlas."

            if current_state.atlas.current_location_id == target_node.id:
                return f"[SISTEMA] Já te encontras em '{destination_name}'."

            # Requisito 30.3: Registar a viagem na trilha
            if current_state.atlas.current_location_id:
                # Evita duplicar a mesma ligação exata de ida
                exists = any(
                    c.from_node_id == current_state.atlas.current_location_id and c.to_node_id == target_node.id 
                    for c in current_state.atlas.connections
                )
                if not exists:
                    current_state.atlas.connections.append(MapConnection(
                        from_node_id=current_state.atlas.current_location_id,
                        to_node_id=target_node.id
                    ))

            current_state.atlas.current_location_id = target_node.id
            logger.info(f"O jogador viajou para {destination_name}.")
            return f"[SISTEMA] Viajou para '{destination_name}'."

        return "[SISTEMA] Comando de mapa desconhecido."