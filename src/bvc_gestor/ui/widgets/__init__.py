# src/bvc_gestor/ui/widgets/__init__.py
"""
Widgets de la interfaz de usuario
"""
from .dashboard_widget import DashboardWidget
from .clientes_widget import ClientesWidget
from .ordenes_widget import OrdenesWidget

# Placeholder widgets para módulos en desarrollo
class PortafolioWidget:
    def __init__(self, app_state):
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        self.widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("📈 Módulo de Portafolio - En desarrollo")
        label.setStyleSheet("font-size: 18px; color: #6c757d;")
        layout.addWidget(label)
        self.widget.setLayout(layout)

class ReportesWidget:
    def __init__(self, app_state):
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        self.widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("📋 Módulo de Reportes - En desarrollo")
        label.setStyleSheet("font-size: 18px; color: #6c757d;")
        layout.addWidget(label)
        self.widget.setLayout(layout)

class ConfigWidget:
    def __init__(self, app_state):
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        self.widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("⚙️ Módulo de Configuración - En desarrollo")
        label.setStyleSheet("font-size: 18px; color: #6c757d;")
        layout.addWidget(label)
        self.widget.setLayout(layout)