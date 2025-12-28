# src/bvc_gestor/ui/statusbar.py
"""
Barra de estado personalizada
"""
from PyQt6.QtWidgets import QStatusBar, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QFont
import logging

from ..core.app_state import AppState
from ..utils.logger import logger
from ..database.engine import get_database

class StatusBar(QStatusBar):
    """Barra de estado personalizada"""
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.message_timeout = 3000  # 3 segundos para mensajes temporales
        self.setup_ui()
        self.start_timers()
        logger.info("Barra de estado inicializada")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Estilo básico
        self.setStyleSheet("""
            QStatusBar {
                background-color: transparent;
                border-top: 1px solid #dee2e6;
                font-size: 12px;
                color: #6c757d;
            }
            QLabel {
                color: #6c757d;
                font-size: 12px;
            }
        """)
        
        # Eliminar widget por defecto
        self.clearMessage()
        
        # Widget personalizado
        self.status_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(20)
        self.status_widget.setLayout(layout)
        
        # Indicadores de estado
        self.db_status_label = QLabel("🔴 DB: Desconectada")
        self.db_status_label.setToolTip("Estado de la base de datos")
        layout.addWidget(self.db_status_label)
        
        self.user_label = QLabel("👤 Usuario: Anónimo")
        self.user_label.setToolTip("Usuario actual")
        layout.addWidget(self.user_label)
        
        self.changes_label = QLabel("💾 Cambios: Guardados")
        self.changes_label.setToolTip("Estado de los cambios")
        layout.addWidget(self.changes_label)
        
        # Espaciador
        layout.addStretch(1)
        
        # Versión
        self.version_label = QLabel("v1.0")
        layout.addWidget(self.version_label)
        
        # Agregar widget a la barra de estado
        self.addPermanentWidget(self.status_widget, 1)
    
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
                self.db_status_label.setStyleSheet("color: #198754;")
                self.app_state.base_datos_conectada = True
            else:
                self.db_status_label.setText("🔴 DB: Desconectada")
                self.db_status_label.setStyleSheet("color: #dc3545;")
                self.app_state.base_datos_conectada = False
            
            # Usuario actual
            if self.app_state.usuario_actual:
                self.user_label.setText(f"👤 Usuario: {self.app_state.usuario_actual}")
            else:
                self.user_label.setText("👤 Usuario: Anónimo")
            
            # Cambios pendientes
            if self.app_state.cambios_pendientes:
                self.changes_label.setText("💾 Cambios: Pendientes")
                self.changes_label.setStyleSheet("color: #ffc107; font-weight: bold;")
            else:
                self.changes_label.setText("💾 Cambios: Guardados")
                self.changes_label.setStyleSheet("color: #198754;")
            
            # Actualizar última actualización
            self.app_state.ultima_actualizacion = QDateTime.currentDateTime()
            
        except Exception as e:
            logger.error(f"Error actualizando estado: {e}")
            self.db_status_label.setText("🔴 DB: Error")
            self.db_status_label.setStyleSheet("color: #dc3545;")
    
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