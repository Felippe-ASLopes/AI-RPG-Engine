import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# O arquivo de log único definido no Épico 18 e 19
load_dotenv()
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "session.log")

class Formatter(logging.Formatter):
    """
    Formatador customizado para cumprir o Requisito 18.2 com incremento de níveis: 
    [HH:MM:SS:ms] [MODULO] [NIVEL] Mensagem de Status
    """
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime("%H:%M:%S")
        return f"{s}:{int(record.msecs):03d}"

    def format(self, record):
        log_time = self.formatTime(record)
        module_name = record.name.upper()
        level_name = record.levelname
        
        msg = record.getMessage()
        
        # Incremento: Se o nível for ERROR ou CRITICAL, converte a mensagem inteira para maiúsculo
        if record.levelno >= logging.ERROR:
            msg = msg.upper()

        # Retorna o padrão final formatado
        return f"[{log_time}] [{module_name}] [{level_name}] {msg}"

class Logger:
    """
    Implementação do Padrão Singleton para garantir que o arquivo 
    session.log não sofra acessos concorrentes (Requisito 18.1).
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Requisito 19.1: Limpeza Automática. O session.log deve ser recriado.
        if os.path.exists(LOG_FILE_PATH):
            try:
                os.remove(LOG_FILE_PATH)
            except PermissionError:
                pass # Caso o arquivo esteja bloqueado por outro processo

        self.central_logger = logging.getLogger("logger")
        self.central_logger.setLevel(logging.DEBUG)
        self.central_logger.propagate = False

        formatter = Formatter()

        # Handler 1: Escrita em Arquivo (persistência para debug)
        file_handler = logging.FileHandler(LOG_FILE_PATH, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.central_logger.addHandler(file_handler)

        # Handler 2: Console (Requisito 19.2: Exibição Real-time)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO) # Info no console para não poluir muito
        self.central_logger.addHandler(console_handler)

    def get_logger(self, module_name: str) -> logging.Logger:
        # Retorna um logger configurado para um módulo específico.
        mod_logger = logging.getLogger(module_name)
        mod_logger.setLevel(logging.DEBUG)
        mod_logger.propagate = False
        
        if not mod_logger.hasHandlers():
            for handler in self.central_logger.handlers:
                mod_logger.addHandler(handler)
                
        return mod_logger

# Instância global para ser importada em qualquer parte do projeto
logger = Logger()

def get_logger(module_name: str) -> logging.Logger:
    """
    Função auxiliar para facilitar a importação.
    Exemplo: 
    logger = get_logger("API")
    logger.error("Falha ao conectar na porta 5001") 
    # Saída: [14:32:01:105] [API] [ERROR] FALHA AO CONECTAR NA PORTA 5001
    """
    return logger.get_logger(module_name)