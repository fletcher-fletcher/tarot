import sys
from loguru import logger
from bot.config import settings


def setup_logger():
    """Configure logging"""
    logger.remove()
    
    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # File output
    logger.add(
        settings.DATA_DIR / "bot.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {name} - {message}",
        level="DEBUG"
    )
    
    return logger


def get_logger():
    """Get logger instance"""
    return logger


# Initialize logger
setup_logger()