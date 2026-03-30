import re
from src.domain.player_input import ParsedInput
from src.infrastructure.config import AppConfig
from src.infrastructure.logger import get_logger

logger = get_logger("INPUT_PROCESSOR")

class InputProcessorUseCase:
    """
    Analisa a string raw enviada pelo jogador, separa os blocos multimodais
    e prepara as injeções de contexto (Épico 8).
    """

    def __init__(self, max_chars: int = None):
        # Permite injeção de dependência para os testes, ou usa o .env por defeito
        self.max_chars = max_chars or AppConfig.MAX_INPUT_CHARACTERS

    def parse_raw_input(self, raw_text: str) -> ParsedInput:
        logger.debug(f"Iniciando parsing de input multimodal: '{raw_text[:30]}...'")
        
        # 1. VALIDAÇÃO DE HARDWARE (Épico 33)
        if len(raw_text) > self.max_chars:
            logger.warning(f"Input rejeitado: {len(raw_text)} caracteres excede o limite de {self.max_chars}.")
            raise ValueError(f"O seu texto ultrapassou o limite máximo de {self.max_chars} caracteres. Por favor, seja mais conciso para manter a performance da narrativa.")
        
        parsed = ParsedInput()
        
        # Se estiver vazio, retorna o objeto zerado
        if not raw_text.strip():
            return parsed

        # Regex para encontrar prefixos válidos (>, ", $, #, *) no início do texto ou após um espaço.
        # Captura o prefixo e todo o texto até o próximo prefixo ou fim da string.
        pattern = r'(?:^|\s)([\>\"\$#\*])\s*(.*?)(?=(?:\s[\>\"\$#\*])|$)'
        matches = re.findall(pattern, raw_text)

        # Fallback: Se o jogador não usou nenhum prefixo, assumimos como uma Ação genérica
        if not matches:
            logger.debug("Nenhum prefixo detectado. Assumindo input como [AÇÃO].")
            parsed.narrative_blocks.append(f"[AÇÃO] {raw_text.strip()}")
            return parsed

        # Processa cada bloco encontrado mantendo a ordem sequencial
        for prefix, content in matches:
            content = content.strip()
            if not content:
                continue

            if prefix == '>':
                parsed.narrative_blocks.append(f"[AÇÃO] {content}")
            elif prefix == '"':
                # Remove a aspa de fechamento caso o regex a tenha capturado no content
                clean_content = content.rstrip('"')
                # Reinsere as aspas perfeitamente para o contexto da LLM
                parsed.narrative_blocks.append(f'[FALA] "{clean_content}"')
            elif prefix == '$':
                parsed.system_overrides.append(content)
            elif prefix == '#':
                parsed.feedback_notes.append(content)
            elif prefix == '*': # Novo tipo de input para consultas forçadas ao RAG
                parsed.forced_queries.append(content)

        logger.info(f"Input processado: {len(parsed.narrative_blocks)} Narrativas, {len(parsed.system_overrides)} Trapaças, {len(parsed.feedback_notes)} Feedbacks.")
        return parsed

    def build_llm_payloads(self, parsed: ParsedInput) -> tuple[str, str]:
        """
        Gera as strings finais que serão enviadas à LLM.
        Retorna: (Texto do Jogador, Injeções de Sistema Adicionais)
        """
        # 1. Concatena a narrativa do jogador
        player_text = "\n".join(parsed.narrative_blocks)
        if not player_text and parsed.system_overrides:
             # Se o jogador enviou SÓ uma trapaça, precisamos avisar a IA para apenas continuar
             player_text = "[AÇÃO] (O jogador aguarda a continuação da cena)"

        # 2. Concatena as "Trapaças" ($) e "Feedbacks" (#) para injetar no System Prompt
        system_additions = []
        
        if parsed.system_overrides:
            overrides = "\n".join(f"- {o}" for o in parsed.system_overrides)
            system_additions.append(f"[FATOS IMPOSTOS PELO JOGADOR (TRAPAÇA - ACEITE COMO VERDADE)]\n{overrides}")
            
        if parsed.feedback_notes:
            feedbacks = "\n".join(f"- {f}" for f in parsed.feedback_notes)
            system_additions.append(f"[FEEDBACK DO JOGADOR PARA ESTE TURNO]\n{feedbacks}")

        system_text = "\n\n".join(system_additions)

        return player_text, system_text