"""
Módulo de Operaciones - REFACTORIZADO
Usa QStackedWidget para navegación interna.
Controller interno maneja toda la lógica.
"""

from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtCore import pyqtSignal
import logging

from .operaciones_dashboard import OperacionesDashboard
from .operaciones_list_view import OperacionesListView
from .portafolio_view import PortafolioView
from ...controllers.operaciones_controller import OperacionesController

logger = logging.getLogger(__name__)


class OperacionesModule(QStackedWidget):
    """
    Módulo completo de operaciones.
    
    Estructura:
    - Index 0: Dashboard (vista principal)
    - Index 1: Lista de operaciones
    - Index 2: Portafolio
    
    El controller interno maneja la navegación y la lógica de negocio.
    """
    
    # Señales públicas (para MainWindow)
    module_ready = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Crear las vistas
        self.view_dashboard = OperacionesDashboard()
        self.view_lista = OperacionesListView()
        self.view_portafolio = PortafolioView()
        
        # Agregar al stack
        self.addWidget(self.view_dashboard)   # Index 0
        self.addWidget(self.view_lista)       # Index 1
        self.addWidget(self.view_portafolio)  # Index 2
        
        # Crear controller INTERNO
        self.controller = OperacionesController(self)
        
        # Inicializar vista
        self.setCurrentIndex(0)
        self.controller.actualizar_dashboard()
        
        logger.info("✅ Módulo de Operaciones inicializado")
        self.module_ready.emit()
    
    def inicializar(self):
        """Inicializa el módulo (carga datos iniciales)"""
        self.controller.actualizar_dashboard()
    
    def get_controller(self):
        """Retorna el controller para acceso externo si es necesario"""
        return self.controller