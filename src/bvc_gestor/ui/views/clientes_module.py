# src/bvc_gestor/ui/views/clientes_module.py
from PyQt6.QtWidgets import QStackedWidget
from .clientes_list_view import ClientesListView
from .clientes_detail_view import ClienteDetalleView
from ...controllers.clientes_controller import ClientesController

class ClientesModule(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Instanciar las Vistas
        self.view_lista = ClientesListView()
        self.view_detalle = ClienteDetalleView()
        
        # 2. Agregarlas al Stack
        self.addWidget(self.view_lista)   # Index 0
        self.addWidget(self.view_detalle) # Index 1
        
        # 3. Instanciar el Controlador (Él maneja la lógica de intercambio)
        self.controller = ClientesController(self)
        
        