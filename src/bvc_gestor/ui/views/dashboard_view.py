from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # 1. TÍTULO DE BIENVENIDA
        title = QLabel("Resumen de Mercado")
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        layout.addWidget(title)

        # 2. CONTENEDOR DE TARJETAS (KPIs)
        kpi_layout = QHBoxLayout()
        
        # Tarjeta Dólar BCV (Inspirado en tu lógica de bcv.py)
        self.card_dolar = self.create_kpi_card("💵 DÓLAR BCV", "---.-- Bs.", "#238636")
        # Tarjeta Clientes Totales (Inspirado en apertura.py)
        self.card_clientes = self.create_kpi_card("👥 CLIENTES", "0", "#1f6feb")
        # Tarjeta Operaciones Hoy
        self.card_ops = self.create_kpi_card("📊 OPS. HOY", "0", "#8957e5")

        kpi_layout.addWidget(self.card_dolar)
        kpi_layout.addWidget(self.card_clientes)
        kpi_layout.addWidget(self.card_ops)
        layout.addLayout(kpi_layout)

        # 3. ÁREA CENTRAL (ESPACIO PARA GRÁFICO)
        self.chart_frame = QFrame()
        self.chart_frame.setStyleSheet("""
            QFrame {
                background-color: #1c2128;
                border: 1px dashed #444c56;
                border-radius: 15px;
            }
        """)
        chart_label = QLabel("Área reservada para Gráfico de Rendimiento (Matplotlib/Plotly)")
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_label.setStyleSheet("color: #768390; border: none;")
        
        center_layout = QVBoxLayout(self.chart_frame)
        center_layout.addWidget(chart_label)
        
        layout.addWidget(self.chart_frame, stretch=1)

    def create_kpi_card(self, title, value, accent_color):
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1c2128;
                border-left: 5px solid {accent_color};
                border-radius: 8px;
            }}
        """)
        
        v_layout = QVBoxLayout(card)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #768390; font-size: 12px; font-weight: bold; border: none;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("color: white; font-size: 24px; font-weight: bold; border: none;")
        
        v_layout.addWidget(lbl_title)
        v_layout.addWidget(lbl_value)
        v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return card