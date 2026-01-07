import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget
from PyQt6.QtCore import Qt
from pathlib import Path

from ...services.portfolio_service import PortfolioService
from ...database.engine import get_database
from ...core.app_state import AppState
from ...controllers.clientes_controller import ClientesController
from ...ui.views import ClientesView, DashboardView, CarteraView, TransaccionesView
from ...ui.widgets.sidebar import SidebarWidget

class MainWindow(QMainWindow):
    def __init__(self, app_state):
        super().__init__()
        self.setWindowTitle("PYME")
        self.app_state = app_state
        self.stacked_widget = None
        self.setup_ui()
        self.aplicar_estilo()

    def setup_ui(self):
        # 1. Widget Central y Layout Principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_principal = QHBoxLayout(self.central_widget)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        # 2. Sidebar
        self.sidebar = SidebarWidget()
        self.layout_principal.addWidget(self.sidebar)

        # 3. El Contenedor de Páginas (QStackedWidget)
        self.contenedor_paginas = QStackedWidget()
        self.layout_principal.addWidget(self.contenedor_paginas)

        # 4. INSTANCIAR LAS VISTAS
        self.view_dashboard = DashboardView()
        self.view_clientes = ClientesView()
        self.view_cartera = CarteraView()
        self.view_transacciones = TransaccionesView()
        
        
        # Conectar la señal de cambio de página del sidebar
        self.sidebar.pagina_cambiada.connect(self.contenedor_paginas.setCurrentIndex)
        
        # 5. AGREGAR VISTAS AL CONTENEDOR
        # El orden en que se agregan define su índice (0, 1, 2...)
        self.contenedor_paginas.addWidget(self.view_dashboard) # Índice 0
        self.contenedor_paginas.addWidget(self.view_clientes)  # Índice 1
        self.contenedor_paginas.addWidget(self.view_cartera)   # Índice 2
        self.contenedor_paginas.addWidget(self.view_transacciones)   # Índice 3

        # Mostrar el Dashboard por defecto
        self.contenedor_paginas.setCurrentWidget(self.view_dashboard)

    def mostrar_clientes(self):
        """Método para cambiar a la vista de clientes"""
        self.contenedor_paginas.setCurrentWidget(self.view_clientes)
    def mostrar_dashboard(self):
        """Método para volver al inicio"""
        self.contenedor_paginas.setCurrentWidget(self.view_dashboard)

    def aplicar_estilo(self):
        ruta_qss = Path(__file__).parent.parent / "resources" / "styles.qss"
        if ruta_qss.exists():
            with open(ruta_qss, "r") as f:
                self.setStyleSheet(f.read())
