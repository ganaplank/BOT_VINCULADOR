"""
Sistema de logging estruturado para o Bot Vinculador.
Fornece logging consistente e rastreável.
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

# Criar pasta de logs se não existir
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Nome do arquivo de log com data/hora
LOG_FILE = LOGS_DIR / f"bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


class LogFormatter(logging.Formatter):
    """Formatter customizado com cores para terminal"""
    
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m",     # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        if sys.stdout.isatty():  # Terminal suporta cores
            color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configura o sistema de logging.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger("bot_vinculador")
    logger.setLevel(level)
    
    # Limpar handlers existentes
    logger.handlers.clear()
    
    # Formato do log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Handler para arquivo
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Erro ao criar handler de arquivo: {e}", file=sys.stderr)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = LogFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Logger global
logger = setup_logging()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Obtém logger com namespace específico"""
    if name:
        return logging.getLogger(f"bot_vinculador.{name}")
    return logger
