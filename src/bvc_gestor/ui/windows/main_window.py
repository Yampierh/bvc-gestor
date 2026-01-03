import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from pathlib import Path

from ...services.portfolio_service import PortfolioService
from ...database.engine import get_database
from ...core.app_state import AppState

class MainWindow(QMainWindow):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setup_ui()
        self.aplicar_estilo()

    def setup_ui(self):
        self.central = QWidget()
        self.central.setObjectName("MainContent")
        self.setCentralWidget(self.central)
        
        self.layout_principal = QHBoxLayout(self.central)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        # 1. Sidebar con ID para CSS
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(80)
        self.layout_principal.addWidget(self.sidebar)

        # 2. Área de Contenido
        self.container = QWidget()
        self.layout_contenido = QVBoxLayout(self.container)
        self.layout_contenido.setContentsMargins(30, 30, 30, 30)
        self.layout_contenido.setSpacing(25)
        
        # Grid de Tarjetas (DashCards con el nuevo estilo)
        self.grid_cards = QHBoxLayout()
        # ... añadir instancias de DashCard ...
        
        self.layout_principal.addWidget(self.container)

    def aplicar_estilo(self):
        ruta_qss = Path(__file__).parent.parent / "resources" / "styles.qss"
        if ruta_qss.exists():
            with open(ruta_qss, "r") as f:
                self.setStyleSheet(f.read())