from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QFrame, QLabel
from PyQt6.QtCore import Qt, pyqtSignal,QSize
from PyQt6.QtGui import QIcon
from pathlib import Path

class SidebarWidget(QFrame):
    pagina_cambiada = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Logo o título de la aplicación
        self.logo = QLabel("PYME")
        self.logo.setStyleSheet("font-size: 22px; ;color: white; font-weight: bold; margin: 20px 0;")
        
        # Botones de navegación
        self.btn_home = self.create_button("src/bvc_gestor/assets/icons/home.svg", "Dashboard", 0, "Dashboard")
        self.btn_clientes = self.create_button("src/bvc_gestor/assets/icons/groups.svg", "Inversores", 1, "Clientes")
        self.btn_operaciones = self.create_button("src/bvc_gestor/assets/icons/wallet.svg", "Operaciones", 2, "Operaciones")
        self.btn_transacciones = self.create_button("src/bvc_gestor/assets/icons/order_approve.svg", "Transacciones", 3, "Transacciones")
        self.btn_config = self.create_button("src/bvc_gestor/assets/icons/settings.svg", "Configuración", 4, "Configuración")
        layout.addWidget(self.logo)
        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_clientes)
        layout.addWidget(self.btn_operaciones)
        layout.addWidget(self.btn_transacciones)
        layout.addStretch() # Empuja el último botón hacia abajo
        layout.addWidget(self.btn_config)

        # Grupo de botones para que solo uno esté activo a la vez
        self.buttons = [self.btn_home, self.btn_clientes, self.btn_operaciones, self.btn_transacciones, self.btn_config]
        self.btn_home.setChecked(True)

    def create_button(self, icon_path, text, index, tooltip):
        
        icon = QIcon(icon_path)
        btn = QPushButton(text)
        btn.setIcon(icon)
        btn.setIconSize(QSize(24, 24))
        
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setToolTip(tooltip)
        btn.clicked.connect(lambda: self.pagina_cambiada.emit(index))
        return btn