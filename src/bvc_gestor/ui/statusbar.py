# src/bvc_gestor/ui/statusbar.py
"""
Barra de estado personalizada - MIGRADO
"""
from PyQt6.QtWidgets import QStatusBar, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QFont
import logging

from ..core.app_state import AppState
from ..utils.logger import logger
from ..database.engine import get_database
from .styles import get_style_manager  # Importar StyleManager

class StatusBar(QStatusBar):
    """Barra de estado personalizada"""
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.style_manager = get_style_manager()  # NUEVO: StyleManager
        self.message_timeout = 3000  # 3 segundos para mensajes temporales
        self.setObjectName("app-statusbar")  # NUEVO: ID para CSS
        self.setup_ui()
        self.start_timers()
        self.apply_styles()  # NUEVO: Aplicar estilos
        logger.info("Barra de estado inicializada")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        self.clearMessage()
        
        # Widget personalizado
        self.status_widget = QWidget()
        self.status_widget.setObjectName("status-widget")  # NUEVO: ID para CSS
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(20)
        self.status_widget.setLayout(layout)
        
        # Indicadores de estado
        self.db_status_label = QLabel("🔴 DB: Desconectada")
        self.db_status_label.setObjectName("status-db")  # NUEVO: ID para CSS
        self.db_status_label.setToolTip("Estado de la base de datos")
        layout.addWidget(self.db_status_label)
        
        self.user_label = QLabel("👤 Usuario: Anónimo")
        self.user_label.setObjectName("status-user")  # NUEVO: ID para CSS
        self.user_label.setToolTip("Usuario actual")
        layout.addWidget(self.user_label)
        
        self.changes_label = QLabel("💾 Cambios: Guardados")
        self.changes_label.setObjectName("status-changes")  # NUEVO: ID para CSS
        self.changes_label.setToolTip("Estado de los cambios")
        layout.addWidget(self.changes_label)
        
        # Espaciador
        layout.addStretch(1)
        
        # Versión
        self.version_label = QLabel("v1.0")
        self.version_label.setObjectName("status-version")  # NUEVO: ID para CSS
        layout.addWidget(self.version_label)
        
        # Agregar widget a la barra de estado
        self.addPermanentWidget(self.status_widget, 1)
    
    def apply_styles(self):
        """Aplicar estilos usando StyleManager"""
        self.style_manager.apply_stylesheet(self)
    
    def start_timers(self):
        """Iniciar timers para actualizaciones"""
        # Timer para actualizar estado
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Actualizar cada 5 segundos
        
        # Actualizar estado inicial
        self.update_status()
    
    def update_status(self):
        """Actualizar estado de la aplicación"""
        try:
            # Estado de base de datos
            db_engine = get_database()
            if db_engine.test_connection():
                self.db_status_label.setText("🟢 DB: Conectada")
                self.db_status_label.setProperty("data-status", "connected")  # NUEVO: Atributo data
                self.app_state.base_datos_conectada = True
            else:
                self.db_status_label.setText("🔴 DB: Desconectada")
                self.db_status_label.setProperty("data-status", "disconnected")  # NUEVO: Atributo data
                self.app_state.base_datos_conectada = False
            
            # Usuario actual
            if self.app_state.usuario_actual:
                self.user_label.setText(f"👤 Usuario: {self.app_state.usuario_actual}")
            else:
                self.user_label.setText("👤 Usuario: Anónimo")
            
            # Cambios pendientes
            if self.app_state.cambios_pendientes:
                self.changes_label.setText("💾 Cambios: Pendientes")
                self.changes_label.setProperty("data-status", "pending")  # NUEVO: Atributo data
            else:
                self.changes_label.setText("💾 Cambios: Guardados")
                self.changes_label.setProperty("data-status", "saved")  # NUEVO: Atributo data
            
            # Actualizar última actualización
            self.app_state.ultima_actualizacion = QDateTime.currentDateTime()
            
            # Re-aplicar estilos para que los cambios de propiedades tomen efecto
            self.apply_styles()
            
        except Exception as e:
            logger.error(f"Error actualizando estado: {e}")
            self.db_status_label.setText("🔴 DB: Error")
            self.db_status_label.setProperty("data-status", "error")
    
    def show_message(self, message: str, timeout: int = None):
        """
        Mostrar mensaje en la barra de estado
        
        Args:
            message: Texto del mensaje
            timeout: Tiempo en milisegundos (None para permanente)
        """
        if timeout is None:
            timeout = self.message_timeout
        
        super().showMessage(message, timeout)
        
        # Log del mensaje
        if "Error" in message or "error" in message.lower():
            logger.error(f"StatusBar: {message}")
        elif "Advertencia" in message or "warning" in message.lower():
            logger.warning(f"StatusBar: {message}")
        else:
            logger.info(f"StatusBar: {message}")
    
    def clear_message(self):
        """Limpiar mensaje actual"""
        super().clearMessage()
    
    def set_user(self, username: str):
        """Establecer usuario actual"""
        self.app_state.usuario_actual = username
        self.user_label.setText(f"👤 Usuario: {username}")
    
    def set_changes_pending(self, pending: bool):
        """Establecer estado de cambios pendientes"""
        self.app_state.cambios_pendientes = pending
        self.update_status()
    
    def on_theme_changed(self):
        """Manejar cambio de tema"""
        self.apply_styles()