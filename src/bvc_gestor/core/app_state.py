# src/bvc_gestor/core/app_state.py
"""
Estado global de la aplicación
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from ..utils.constants import DATA_DIR, CONFIG_DIR
from ..utils.logger import logger

@dataclass
class AppState:
    """Estado global de la aplicación"""
    
    # Usuario actual
    usuario_actual: Optional[str] = None
    rol_usuario: str = "Usuario"
    
    # Configuración
    configuracion: Dict[str, Any] = field(default_factory=dict)
    
    # Estado de la aplicación
    aplicacion_iniciada: bool = False
    modo_oscuro: bool = False
    base_datos_conectada: bool = False
    
    # Datos en memoria
    clientes_cargados: bool = False
    activos_cargados: bool = False
    
    # Estado de la sesión
    ultima_actualizacion: datetime = field(default_factory=datetime.now)
    cambios_pendientes: bool = False
    
    # Rutas importantes
    ruta_base_datos: Path = DATA_DIR / "database" / "bvc_gestor.db"
    ruta_configuracion: Path = CONFIG_DIR / "app_config.json"
    
    def __post_init__(self):
        """Inicializar estado después de creación"""
        self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """Cargar configuración desde archivo"""
        try:
            if self.ruta_configuracion.exists():
                with open(self.ruta_configuracion, 'r', encoding='utf-8') as f:
                    self.configuracion = json.load(f)
                    logger.info(f"Configuración cargada desde {self.ruta_configuracion}")
            else:
                # Configuración por defecto
                self.configuracion = {
                    'general': {
                        'nombre_aplicacion': 'BVC-GESTOR',
                        'version': '1.0.0',
                        'modo_oscuro': False,
                        'idioma': 'es',
                        'moneda_principal': 'USD'
                    },
                    'comisiones': {
                        'comision_base': 0.005,
                        'iva': 0.16,
                        'comision_minima': 1.0,
                        'comision_maxima': 1000.0
                    },
                    'backup': {
                        'auto_backup': True,
                        'frecuencia_backup': 'diario',
                        'max_backups_diarios': 7,
                        'max_backups_semanales': 4,
                        'max_backups_mensuales': 12
                    },
                    'reportes': {
                        'formato_predeterminado': 'PDF',
                        'ruta_guardado': str(REPORTS_DIR),
                        'incluir_logo': True,
                        'firma_digital': False
                    }
                }
                self.guardar_configuracion()
                logger.info("Configuración por defecto creada")
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {str(e)}")
            self.configuracion = {}
    
    def guardar_configuracion(self):
        """Guardar configuración a archivo"""
        try:
            # Asegurar que existe el directorio
            self.ruta_configuracion.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.ruta_configuracion, 'w', encoding='utf-8') as f:
                json.dump(self.configuracion, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuración guardada en {self.ruta_configuracion}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {str(e)}")
            return False
    
    def get_config(self, seccion: str, clave: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        try:
            return self.configuracion.get(seccion, {}).get(clave, default)
        except (KeyError, AttributeError):
            return default
    
    def set_config(self, seccion: str, clave: str, valor: Any):
        """Establecer valor de configuración"""
        if seccion not in self.configuracion:
            self.configuracion[seccion] = {}
        
        self.configuracion[seccion][clave] = valor
        self.cambios_pendientes = True
        self.guardar_configuracion()
    
    def actualizar_estado(self, **kwargs):
        """Actualizar múltiples propiedades del estado"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.ultima_actualizacion = datetime.now()
        self.cambios_pendientes = True
    
    def obtener_resumen(self) -> Dict[str, Any]:
        """Obtener resumen del estado de la aplicación"""
        return {
            'usuario': self.usuario_actual,
            'rol': self.rol_usuario,
            'aplicacion_iniciada': self.aplicacion_iniciada,
            'base_datos_conectada': self.base_datos_conectada,
            'clientes_cargados': self.clientes_cargados,
            'activos_cargados': self.activos_cargados,
            'modo_oscuro': self.modo_oscuro,
            'cambios_pendientes': self.cambios_pendientes,
            'ultima_actualizacion': self.ultima_actualizacion.isoformat()
        }
    
    def limpiar_estado(self):
        """Limpiar estado de la aplicación (para cierre)"""
        self.cambios_pendientes = False
        self.clientes_cargados = False
        self.activos_cargados = False
        self.aplicacion_iniciada = False
    
    def __str__(self):
        return f"AppState(usuario={self.usuario_actual}, db_conectada={self.base_datos_conectada})"