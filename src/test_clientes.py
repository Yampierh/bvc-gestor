import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from bvc_gestor.ui.views.clientes_view import ClientesView
from bvc_gestor.controllers.clientes_controller import ClientesController
from bvc_gestor.database import engine
from bvc_gestor.database.models_sql import Base
def probal_modulo_clientes():
    # 1. Crear las tablas en la base de datos (si no existen)
    # Esto usa la estructura pro que definimos basada en apertura.py
    Base.metadata.create_all(bind=engine)
    
    app = QApplication(sys.argv)
    
    # 2. Configurar la ventana de prueba
    window = QMainWindow()
    window.setWindowTitle("BVC-GESTOR | Prueba de Módulo Clientes")
    window.resize(1100, 700)
    window.setStyleSheet("background-color: #161925;") # Fondo Dark Premium

    # 3. Instanciar Vista y Controlador
    vista = ClientesView()
    controlador = ClientesController(vista)
    
    window.setCentralWidget(vista)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    probal_modulo_clientes()