from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QFrame)
from PyQt6.QtCore import Qt

class CarteraView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 1. CABECERA: Título y Selector de Cliente
        header = QHBoxLayout()
        title = QLabel("Portafolio de Inversiones")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        
        # Aquí irá el buscador de clientes más adelante
        self.lbl_cliente_actual = QLabel("Seleccione un cliente...")
        self.lbl_cliente_actual.setStyleSheet("color: #58a6ff; font-size: 16px; font-style: italic;")
        header.addStretch()
        header.addWidget(self.lbl_cliente_actual)
        layout.addLayout(header)

        # 2. RESUMEN FINANCIERO (Cards pequeñas)
        summary_layout = QHBoxLayout()
        self.card_total = self.create_mini_card("VALOR TOTAL", "0.00 Bs.", "#238636")
        self.card_profit = self.create_mini_card("GANANCIA / PÉRDIDA", "0.00 %", "#1f6feb")
        
        summary_layout.addWidget(self.card_total)
        summary_layout.addWidget(self.card_profit)
        layout.addLayout(summary_layout)

        # 3. TABLA DE POSICIONES (Estilo Profesional)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Símbolo", "Cantidad", "Precio Prom.", "Último Precio", "Rendimiento"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1c2128;
                color: #adbac7;
                border: 1px solid #30363d;
                border-radius: 8px;
                gridline-color: #30363d;
            }
            QHeaderView::section {
                background-color: #2d333b;
                color: #58a6ff;
                padding: 12px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

    def create_mini_card(self, label, value, color):
        card = QFrame()
        card.setStyleSheet(f"background-color: #1c2128; border-radius: 10px; border-top: 3px solid {color};")
        card_layout = QVBoxLayout(card)
        
        lbl_text = QLabel(label)
        lbl_text.setStyleSheet("color: #768390; font-size: 10px; font-weight: bold; border: none;")
        
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("color: white; font-size: 18px; font-weight: bold; border: none;")
        
        card_layout.addWidget(lbl_text)
        card_layout.addWidget(lbl_val)
        return card