import os
from src.infrastructure.logger import Logger, get_logger, LOG_FILE_PATH

def test_logger_singleton():
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2

def test_logger_file_creation():
    log = get_logger("TEST")
    log.info("Teste de criação de arquivo")
    assert os.path.exists(LOG_FILE_PATH)

def test_logger_error_formatting():
    log = get_logger("TEST_ERR")
    log.error("erro em minusculo")
    
    with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "ERRO EM MINUSCULO" in content