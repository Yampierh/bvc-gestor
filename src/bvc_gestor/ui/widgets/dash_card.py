from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class DashCard(QFrame):
    def __init__(self, titulo, valor, color_valor="#2ecc71"):
        super().__init__()
        self.setFixedSize(220, 100)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2b2b2b;
                border-radius: 12px;
                border: 1px solid #3d3d3d;
            }}
            QLabel {{ border: none; color: #888888; font-size: 11px; font-weight: bold; }}
            .monto {{ color: {color_valor}; font-size: 18px; }}
        """)
        layout = QVBoxLayout(self)
        self.lbl_titulo = QLabel(titulo.upper())
        self.lbl_valor = QLabel(valor)
        self.lbl_valor.setProperty("class", "monto")
        
        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_valor, 0, Qt.AlignmentFlag.AlignBottom)

    def update_value(self, nuevo_valor):
        self.lbl_valor.setText(nuevo_valor)