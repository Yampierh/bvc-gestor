# src/bvc_gestor/ui/sidebar.py
"""
Barra lateral de navegación - Versión migrada a StyleManager
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, 
    QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont
import logging

from ..core.app_state import AppState
from ..utils.logger import logger
from .styles import get_style_manager


class SidebarButton(QPushButton):
    """Botón personalizado para la sidebar"""
    
    clicked_signal = pyqtSignal(str)
    
    def __init__(self, button_id: str, text: str, parent=None):
        super().__init__(parent)
        self.button_id = button_id
        self.text = text
        self.active = False
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Configurar interfaz del botón"""
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(50)
        
        # Texto
        self.setText(self.text)
        
        # Identificadores para CSS
        self.setObjectName(f"sidebar_button_{self.button_id}")
        self.setProperty("class", "sidebar-button")
        
        # Tooltip
        tooltip_map = {
            'dashboard': 'Dashboard principal',
            'clientes': 'Gestión de clientes',
            'ordenes': 'Órdenes bursátiles',
            'portafolio': 'Portafolios de inversión',
            'reportes': 'Reportes y análisis',
            'config': 'Configuración del sistema'
        }
        self.setToolTip(tooltip_map.get(self.button_id, self.text))
    
    def setup_connections(self):
        """Configurar conexiones"""
        self.clicked.connect(lambda: self.clicked_signal.emit(self.button_id))
    
    def set_active(self, active: bool):
        """Establecer estado activo"""
        self.active = active
        self.setChecked(active)
        
        # Actualizar propiedad CSS
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
    
    def on_theme_changed(self, dark_mode: bool):
        """Manejar cambio de tema"""
        # El StyleManager se encarga de los estilos
        # Solo necesitamos actualizar propiedades si es necesario
        pass


class Sidebar(QWidget):
    """Barra lateral de navegación"""
    
    # Señales
    dashboard_clicked = pyqtSignal()
    clientes_clicked = pyqtSignal()
    ordenes_clicked = pyqtSignal()
    portafolio_clicked = pyqtSignal()
    reportes_clicked = pyqtSignal()
    config_clicked = pyqtSignal()
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.buttons = {}
        
        # Configurar identificador para CSS
        self.setObjectName("sidebar")
        
        self.setup_ui()
        self.setup_connections()
        
        logger.info("Sidebar inicializada")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Ancho fijo
        self.setFixedWidth(220)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        self.setLayout(layout)
        
        # Logo/Título
        title_widget = QWidget()
        title_layout = QVBoxLayout()
        title_widget.setLayout(title_layout)
        
        app_logo = QLabel("📈 PYME")
        app_logo.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #ffffff;
                padding: 0 20px;
                margin-bottom: 8px;
            }
        """)
        title_layout.addWidget(app_logo)
        
        app_subtitle = QLabel("Sistema de Gestión Bursátil")
        app_subtitle.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #b0b7c3;
                padding: 0 20px;
                margin-bottom: 24px;
            }
        """)
        title_layout.addWidget(app_subtitle)
        
        layout.addWidget(title_widget)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #2a3655; height: 1px; margin: 0 16px;")
        layout.addWidget(separator)
        
        # Botones de navegación
        nav_buttons = [
            ("dashboard", "📊 Dashboard"),
            ("clientes", "👥 Clientes"),
            ("ordenes", "💼 Órdenes"),
            ("portafolio", "📈 Portafolio"),
            ("reportes", "📋 Reportes"),
            ("config", "⚙️ Configuración"),
        ]
        
        for btn_id, btn_text in nav_buttons:
            button = SidebarButton(btn_id, btn_text)
            layout.addWidget(button)
            self.buttons[btn_id] = button
        
        # Espaciador para empujar contenido hacia arriba
        layout.addSpacerItem(QSpacerItem(20, 40, 
            QSizePolicy.Policy.Minimum, 
            QSizePolicy.Policy.Expanding))
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Mapear señales de botones
        signal_map = {
            'dashboard': self.dashboard_clicked,
            'clientes': self.clientes_clicked,
            'ordenes': self.ordenes_clicked,
            'portafolio': self.portafolio_clicked,
            'reportes': self.reportes_clicked,
            'config': self.config_clicked
        }
        
        for btn_id, button in self.buttons.items():
            button.clicked_signal.connect(signal_map[btn_id])
    
    def set_active_button(self, button_id: str):
        """Establecer botón activo"""
        for btn_id, button in self.buttons.items():
            button.set_active(btn_id == button_id)
    
    def on_theme_changed(self, dark_mode: bool):
        """Manejar cambio de tema"""
        # Actualizar propiedades CSS si es necesario
        for button in self.buttons.values():
            if hasattr(button, 'on_theme_changed'):
                button.on_theme_changed(dark_mode)
    
    def resizeEvent(self, event):
        """Manejar cambio de tamaño"""
        super().resizeEvent(event)
        # Mantener ancho fijo
        self.setFixedWidth(220)