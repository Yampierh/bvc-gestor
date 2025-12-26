# src/bvc_gestor/ui/widgets/__init__.py
"""
Widgets de la interfaz de usuario - Versión corregida
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

# Importar DashboardWidget real
from .dashboard_widget import DashboardWidget

# Placeholder widgets para otros módulos
class ClientesWidget(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout()
        label = QLabel("👥 Módulo de Clientes - En desarrollo")
        label.setStyleSheet("font-size: 18px; color: #6c757d;")
        layout.addWidget(label)
        self.setLayout(layout)

class OrdenesWidget(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout()
        label = QLabel("💼 Módulo de Órdenes - En desarrollo")
        label.setStyleSheet("font-size: 18px; color: #6c757d;")
        layout.addWidget(label)
        self.setLayout(layout)

class PortafolioWidget(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout()
        label = QLabel("📈 Módulo de Portafolio - En desarrollo")
        label.setStyleSheet("font-size: 18px; color: #6c757d;")
        layout.addWidget(label)
        self.setLayout(layout)

class ReportesWidget(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout()
        label = QLabel("📋 Módulo de Reportes - En desarrollo")
        label.setStyleSheet("font-size: 18px; color: #6c757d;")
        layout.addWidget(label)
        self.setLayout(layout)

class ConfigWidget(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout()
        label = QLabel("⚙️ Módulo de Configuración - En desarrollo")
        label.setStyleSheet("font-size: 18px; color: #6c757d;")
        layout.addWidget(label)
        self.setLayout(layout)

__all__ = [
    'DashboardWidget',
    'ClientesWidget',
    'OrdenesWidget',
    'PortafolioWidget',
    'ReportesWidget',
    'ConfigWidget'
]