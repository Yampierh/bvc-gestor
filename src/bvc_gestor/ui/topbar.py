# src/bvc_gestor/ui/topbar.py
"""
Barra superior con controles de usuario - MIGRADO
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont
import logging

from ..core.app_state import AppState
from ..utils.logger import logger
from .styles import get_style_manager  # Importar StyleManager

class NotificationBadge(QLabel):
    """Badge para notificaciones - MIGRADO"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.count = 0
        self.setObjectName("notification-badge")  # NUEVO: ID para CSS
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz"""
        self.setFixedSize(20, 20)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # ❌ REMOVER setStyleSheet() hardcodeado
        self.hide()
    
    def set_count(self, count: int):
        """Establecer contador de notificaciones"""
        self.count = count
        if count > 0:
            self.setText(str(count) if count <= 99 else "99+")
            self.show()
        else:
            self.hide()

class Topbar(QWidget):
    """Barra superior con controles - MIGRADO"""
    
    # Señales
    theme_toggled = pyqtSignal()
    refresh_clicked = pyqtSignal()
    notifications_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    profile_clicked = pyqtSignal()
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.style_manager = get_style_manager()  # NUEVO: StyleManager
        self.setObjectName("topbar")  # NUEVO: ID para CSS
        self.setup_ui()
        self.setup_connections()
        self.start_timers()
        self.apply_styles()  # NUEVO: Aplicar estilos
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        self.setFixedHeight(60)
        # ❌ REMOVER setStyleSheet() hardcodeado aquí
        
        # Layout principal
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Título de la aplicación
        self.title_label = QLabel("BVC-GESTOR")
        self.title_label.setObjectName("topbar-title")  # NUEVO: ID para CSS
        layout.addWidget(self.title_label)
        
        # Espaciador
        layout.addStretch(1)
        
        # Fecha y hora
        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("topbar-datetime")  # NUEVO: ID para CSS
        layout.addWidget(self.datetime_label)
        
        # Botón de refrescar
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Refrescar datos")
        self.refresh_btn.setFixedSize(40, 40)
        self.refresh_btn.setProperty("class", "icon-button topbar-button")  # NUEVO: Clases CSS
        layout.addWidget(self.refresh_btn)
        
        # Botón de tema
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setToolTip("Cambiar tema")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.setProperty("class", "icon-button topbar-button")  # NUEVO: Clases CSS
        layout.addWidget(self.theme_btn)
        
        # Botón de notificaciones
        self.notifications_btn = QPushButton("🔔")
        self.notifications_btn.setToolTip("Notificaciones")
        self.notifications_btn.setFixedSize(40, 40)
        self.notifications_btn.setProperty("class", "icon-button topbar-button")  # NUEVO: Clases CSS
        layout.addWidget(self.notifications_btn)
        
        # Badge de notificaciones
        self.notification_badge = NotificationBadge(self.notifications_btn)
        self.notification_badge.move(25, 5)
        self.notification_badge.set_count(3)  # Placeholder
        
        # Botón de configuración
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setToolTip("Configuración")
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setProperty("class", "icon-button topbar-button")  # NUEVO: Clases CSS
        layout.addWidget(self.settings_btn)
        
        # Perfil de usuario
        self.profile_btn = QPushButton("👤")
        self.profile_btn.setToolTip("Perfil de usuario")
        self.profile_btn.setFixedSize(40, 40)
        self.profile_btn.setProperty("class", "icon-button topbar-button")  # NUEVO: Clases CSS
        layout.addWidget(self.profile_btn)
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        self.refresh_btn.clicked.connect(self.refresh_clicked)
        self.theme_btn.clicked.connect(self.theme_toggled)
        self.notifications_btn.clicked.connect(self.notifications_clicked)
        self.settings_btn.clicked.connect(self.settings_clicked)
        self.profile_btn.clicked.connect(self.profile_clicked)
    
    def apply_styles(self):
        """Aplicar estilos usando StyleManager"""
        self.style_manager.apply_stylesheet(self)
        self.update_theme_icon()
    
    def start_timers(self):
        """Iniciar timers para actualizaciones"""
        # Timer para fecha y hora
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # Actualizar cada segundo
        self.update_datetime()
    
    def update_datetime(self):
        """Actualizar fecha y hora"""
        current_datetime = QDateTime.currentDateTime()
        datetime_str = current_datetime.toString("dd/MM/yyyy hh:mm AP")
        self.datetime_label.setText(datetime_str)
    
    def update_theme_icon(self):
        """Actualizar icono del tema según estado"""
        if self.app_state.modo_oscuro:
            self.theme_btn.setText("☀️")
            self.theme_btn.setToolTip("Cambiar a tema claro")
        else:
            self.theme_btn.setText("🌙")
            self.theme_btn.setToolTip("Cambiar a tema oscuro")
    
    def theme_toggled_handler(self):
        """Manejador para cambio de tema"""
        self.update_theme_icon()
        self.theme_toggled.emit()
    
    def on_theme_changed(self):
        """Manejar cambio de tema desde MainWindow"""
        self.update_theme_icon()
        self.apply_styles()