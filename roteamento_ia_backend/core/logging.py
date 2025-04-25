from loguru import logger
import sys

logger.remove()

# Adiciona um handler no stdout, com formato e rotação diários
logger.add(
    sys.stdout,
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True
)

# (Opcional) arquivo de log com rotação
logger.add(
    "logs/roteamento_ia_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    rotation="00:00",
    retention="7 days",
    compression="zip"
)
