import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QMessageBox, QGraphicsOpacityEffect
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtCore import pyqtSignal, QPropertyAnimation, QEasingCurve
from pathlib import Path

from ...utils.logger import logger
from ...ui.views import ClientesModule, DashboardView
from ...ui.widgets import SidebarWidget, HeaderWidget


class MainWindow(QMainWindow):
    
    app_closing = pyqtSignal()
    
    def __init__(self, app_state):
        super().__init__()
        self.setWindowTitle("PYME")
        self.app_state = app_state
        self.stacked_widget = None
        self.setup_ui()
        self.aplicar_estilo()

    def setup_ui(self):
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_main = QHBoxLayout(self.central_widget)
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.layout_main.setSpacing(0)

        
        self.sidebar = SidebarWidget()
        self.sidebar.setContentsMargins(0, 0, 0, 0)
        self.layout_main.addWidget(self.sidebar)
        
        
        self.right_container = QWidget()
        self.layout_right = QVBoxLayout(self.right_container) # Vertical
        self.layout_right.setContentsMargins(0, 0, 0, 0)
        self.layout_right.setSpacing(0)
        
        self.header = HeaderWidget()
        self.layout_right.addWidget(self.header)

        
        self.contenedor_paginas = QStackedWidget()
        self.layout_right.addWidget(self.contenedor_paginas)
        
        
        self.layout_main.addWidget(self.right_container)

        
        self.view_dashboard = DashboardView()
        self.view_clientes = ClientesModule()
        self.view_cartera = QWidget()
        self.view_transacciones = QWidget()
        self.view_configuracion = QWidget()  # Placeholder para Configuración
        
        self.contenedor_paginas.addWidget(self.view_dashboard) # Índice 0
        self.contenedor_paginas.addWidget(self.view_clientes)  # Índice 1
        self.contenedor_paginas.addWidget(self.view_cartera)   # Índice 2
        self.contenedor_paginas.addWidget(self.view_transacciones)   # Índice 3
        self.contenedor_paginas.addWidget(self.view_configuracion)   # Índice 4 (Configuración - placeholder)

        self.sidebar.pagina_cambiada.connect(self.cambiar_vista_con_fade)

        # Mostrar el Dashboard por defecto
        self.contenedor_paginas.setCurrentWidget(self.view_dashboard)

    def cambiar_vista_con_fade(self, index_destino):
        """Maneja la animación de desvanecimiento y actualiza el título"""
        if index_destino == self.contenedor_paginas.currentIndex():
            return

        # 1. Identificar widgets
        self.pag_actual = self.contenedor_paginas.currentWidget()
        self.pag_siguiente = self.contenedor_paginas.widget(index_destino)

        # 2. Configurar efectos
        self.efecto_salida = QGraphicsOpacityEffect(self.pag_actual)
        self.efecto_entrada = QGraphicsOpacityEffect(self.pag_siguiente)
        
        self.pag_actual.setGraphicsEffect(self.efecto_salida)
        self.pag_siguiente.setGraphicsEffect(self.efecto_entrada)

        # 3. Animación de Salida (Fade Out)
        self.anim_salida = QPropertyAnimation(self.efecto_salida, b"opacity")
        self.anim_salida.setDuration(250)
        self.anim_salida.setStartValue(1.0)
        self.anim_salida.setEndValue(0.0)
        self.anim_salida.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 4. Animación de Entrada (Fade In)
        self.anim_entrada = QPropertyAnimation(self.efecto_entrada, b"opacity")
        self.anim_entrada.setDuration(250)
        self.anim_entrada.setStartValue(0.0)
        self.anim_entrada.setEndValue(1.0)
        self.anim_entrada.setEasingCurve(QEasingCurve.Type.InCubic)

        # 5. Ejecución coordinada
        # Primero cambiamos el título del header
        titulos = {
            0: "Main Dashboard", 1: "Gestión de Inversores",
            2: "Cartera de Inversión", 3: "Historial de Transacciones",
            4: "Configuración"
        }
        self.header.update_title(titulos.get(index_destino, "PYME"))

        # Al terminar la salida, hacemos el switch real en el StackedWidget
        self.anim_salida.finished.connect(lambda: self.finalizar_transicion(index_destino))
        
        self.anim_salida.start()
        self.anim_entrada.start()

    def finalizar_transicion(self, index):
        """Cambia el index y limpia los efectos para ahorrar recursos"""
        self.contenedor_paginas.setCurrentIndex(index)
        # Es importante quitar el efecto al terminar para que el widget sea interactivo
        if self.contenedor_paginas.widget(index):
            self.contenedor_paginas.widget(index).setGraphicsEffect(None)
            
    def mostrar_clientes(self):
        # Cada vez que entramos, podemos forzar que inicie en la lista (index 0)
        self.view_clientes.setCurrentIndex(0)
        self.contenedor_paginas.setCurrentIndex(1)
        self.header.update_title("Gestión de Inversores") 
        # Opcional: refrescar la tabla al entrar
        self.view_clientes.controller.actualizar_tabla()

    def aplicar_estilo(self):
        ruta_qss = Path(__file__).parent.parent / "themes" / "styles.qss"
        if ruta_qss.exists():
            with open(ruta_qss, "r") as f:
                self.setStyleSheet(f.read())
                
    def closeEvent(self, event: QCloseEvent):
        """Maneja el evento de cierre de la ventana principal"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar Cierre",
            "¿Estás seguro de que deseas salir de la aplicación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            logger.info("Cerrando la aplicación.")
            self.app_closing.emit()
            event.accept()
        else:
            event.ignore()
