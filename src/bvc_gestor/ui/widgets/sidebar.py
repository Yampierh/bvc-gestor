from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

class SidebarWidget(QFrame):
    pagina_cambiada = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(70)
        self.setStyleSheet("""
            QFrame {
                background-color: #0d1117;
                border-right: 1px solid #30363d;
            }
            QPushButton {
                background-color: transparent;
                color: #8b949e;
                font-size: 22px;
                border-radius: 12px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #21262d;
                color: #58a6ff;
            }
            QPushButton:checked {
                background-color: #1f6feb;
                color: white;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Botones con iconos (puedes usar emojis por ahora o QIcon más tarde)
        self.btn_home = self.create_button("🏠", 0, "Dashboard")
        self.btn_clientes = self.create_button("👤", 1, "Clientes")
        self.btn_cartera = self.create_button("💼", 2, "Cartera/Inversiones")
        self.btn_transacciones = self.create_button("📊", 3, "Transacciones")
        self.btn_config = self.create_button("⚙️", 4, "Configuración")

        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_clientes)
        layout.addWidget(self.btn_cartera)
        layout.addWidget(self.btn_transacciones)
        layout.addStretch() # Empuja el último botón hacia abajo
        layout.addWidget(self.btn_config)

        # Grupo de botones para que solo uno esté activo a la vez
        self.buttons = [self.btn_home, self.btn_clientes, self.btn_cartera, self.btn_transacciones, self.btn_config]
        self.btn_home.setChecked(True)

    def create_button(self, icon, index, tooltip):
        btn = QPushButton(icon)
        btn.setCheckable(True)
        btn.setAutoExclusive(True) # Solo uno activo a la vez
        btn.setToolTip(tooltip)
        btn.clicked.connect(lambda: self.pagina_cambiada.emit(index))
        return btn