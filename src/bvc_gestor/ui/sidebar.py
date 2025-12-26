# src/bvc_gestor/ui/sidebar.py
"""
Barra lateral de navegación
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon
import logging

from ..utils.logger import logger

class SidebarButton(QPushButton):
    """Botón personalizado para la sidebar"""
    
    def __init__(self, text: str, icon_name: str = "", parent=None):
        super().__init__(parent)
        self.text = text
        self.icon_name = icon_name
        self.active = False
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz del botón"""
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(50)
        
        # Layout horizontal para icono y texto
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Texto
        self.setText(self.text)
        
        # Estilo básico
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                text-align: left;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #2c5aa0;
                color: white;
            }
        """)
    
    def set_active(self, active: bool):
        """Establecer estado activo"""
        self.active = active
        self.setChecked(active)
        
        # Actualizar estilo según estado
        if active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2c5aa0;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 15px;
                    text-align: left;
                    font-weight: 600;
                    font-size: 14px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 8px;
                    padding: 10px 15px;
                    text-align: left;
                    font-weight: 500;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)

class Sidebar(QWidget):
    """Barra lateral de navegación"""
    
    # Señales
    dashboard_clicked = pyqtSignal()
    clientes_clicked = pyqtSignal()
    ordenes_clicked = pyqtSignal()
    portafolio_clicked = pyqtSignal()
    reportes_clicked = pyqtSignal()
    config_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.buttons = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        self.setFixedWidth(220)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        self.setLayout(layout)
        
        # Logo/título
        title_label = QLabel("BVC-GESTOR")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c5aa0;
                padding: 10px;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title_label)
        
        # Separador
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #dee2e6;")
        layout.addWidget(separator)
        layout.addSpacing(10)
        
        # Botones de navegación
        nav_buttons = [
            ("dashboard", "📊 Dashboard", self.dashboard_clicked),
            ("clientes", "👥 Clientes", self.clientes_clicked),
            ("ordenes", "💼 Órdenes", self.ordenes_clicked),
            ("portafolio", "📈 Portafolio", self.portafolio_clicked),
            ("reportes", "📋 Reportes", self.reportes_clicked),
            ("config", "⚙️ Configuración", self.config_clicked),
        ]
        
        for btn_id, btn_text, signal in nav_buttons:
            button = SidebarButton(btn_text)
            button.clicked.connect(signal)
            layout.addWidget(button)
            self.buttons[btn_id] = button
        
        # Espaciador para empujar contenido hacia arriba
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Versión
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                padding: 5px;
            }
        """)
        layout.addWidget(version_label)
    
    def set_active_button(self, button_id: str):
        """Establecer botón activo"""
        for btn_id, button in self.buttons.items():
            button.set_active(btn_id == button_id)
    
    def resizeEvent(self, event):
        """Manejar cambio de tamaño"""
        super().resizeEvent(event)
        # Mantener ancho fijo
        self.setFixedWidth(220)