# src/bvc_gestor/utils/logger.py
"""
Sistema de logging centralizado
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from ..utils.constants import DATA_DIR

class AppLogger:
    """Logger centralizado para la aplicación"""
    
    def __init__(self, name="BVC-GESTOR"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Crear directorio de logs si no existe
        logs_dir = DATA_DIR / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Formato de logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Handler para archivo (rotación diaria)
        log_file = logs_dir / f"bvc_gestor_{datetime.now().strftime('%Y%m')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Agregar handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def get_logger(self):
        return self.logger

# Singleton logger
_logger_instance = None

def get_logger(name="BVC-GESTOR"):
    """Obtener instancia del logger"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AppLogger(name)
    return _logger_instance.get_logger()

# Logger de acceso rápido
logger = get_logger()