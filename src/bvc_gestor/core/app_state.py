# src/bvc_gestor/core/app_state.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from ..utils.constants import DATA_DIR, CONFIG_DIR, REPORTS_DIR
from ..utils.logger import logger

@dataclass
class AppState:
    """Estado global de la aplicación con persistencia de configuración."""
    
    # Atributos de Identidad y Servicios
    user_id: int = 1
    db_session: Any = None
    portfolio_service: Any = None
    orden_service: Any = None
    
    # Atributos de Estado de Usuario
    usuario_actual: Optional[str] = None
    rol_usuario: str = "Usuario"
    
    # Configuración y Rutas
    configuracion: Dict[str, Any] = field(default_factory=dict)
    ruta_configuracion: Path = CONFIG_DIR / "app_config.json"
    
    # Flags de Estado
    aplicacion_iniciada: bool = False
    base_datos_conectada: bool = False
    cambios_pendientes: bool = False
    ultima_actualizacion: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Inicialización automática tras la creación de la instancia."""
        self.cargar_configuracion()

    def initialize_services(self, session):
        """Inicializa los servicios financieros inyectando la sesión de BD."""
        
        self.db_session = session
        self.base_datos_conectada = True
        logger.info("✓ Servicios de Negocio vinculados al AppState")

    def cargar_configuracion(self):
        """Carga el JSON de configuración o crea uno por defecto."""
        try:
            if self.ruta_configuracion.exists():
                with open(self.ruta_configuracion, 'r', encoding='utf-8') as f:
                    self.configuracion = json.load(f)
            else:
                self.configuracion = {'general': {'modo_oscuro': False, 'idioma': 'es'}}
                self.guardar_configuracion()
            logger.info(f"✓ Configuración gestionada en {self.ruta_configuracion}")
        except Exception as e:
            logger.error(f"Error en configuración: {e}")

    def guardar_configuracion(self):
        """Guarda la configuración actual en disco."""
        try:
            self.ruta_configuracion.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ruta_configuracion, 'w', encoding='utf-8') as f:
                json.dump(self.configuracion, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            return False