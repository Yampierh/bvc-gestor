from PyQt6.QtWidgets import (
QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
QLineEdit, QPushButton, QTableWidget, 
QTableWidgetItem, QHeaderView, QFrame, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class ClientesView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- SECCIÓN IZQUIERDA: LISTA Y BÚSQUEDA ---
        left_panel = QVBoxLayout()
        
        # Buscador Pro
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Buscar cliente por RIF o Nombre...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #1e222d;
                color: white;
                border: 1px solid #3d4455;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        left_panel.addWidget(self.search_bar)

        # Tabla de Clientes
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["RIF", "Nombre", "Tipo", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1c26;
                color: #d1d1d1;
                gridline-color: #2d3245;
                border: none;
            }
            QHeaderView::section {
                background-color: #1e222d;
                color: #4a54ff;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        left_panel.addWidget(self.table)
        
        layout.addLayout(left_panel, stretch=2)

        # --- SECCIÓN DERECHA: FICHA DETALLADA (Inspirada en apertura.py) ---
        self.detail_panel = QFrame()
        self.detail_panel.setStyleSheet("""
            QFrame {
                background-color: #1e222d;
                border-radius: 12px;
                border: 1px solid #3d4455;
            }
            QLabel { color: #8a8f9d; border: none; }
            QLineEdit { 
                background-color: #2d3245; 
                color: white; 
                border: 1px solid #3d4455; 
                padding: 5px;
            }
        """)
        
        detail_layout = QVBoxLayout(self.detail_panel)
        title_detail = QLabel("FICHA MAESTRA DEL CLIENTE")
        title_detail.setStyleSheet("color: white; font-weight: bold; font-size: 16px; border: none;")
        detail_layout.addWidget(title_detail)

        # Formulario con tus campos de apertura.py
        form = QFormLayout()
        self.edit_rif = QLineEdit()
        self.edit_nombre = QLineEdit()
        self.edit_tipo = QLineEdit() # P o J
        self.edit_direccion = QLineEdit()
        self.edit_email = QLineEdit()
        
        form.addRow("RIF:", self.edit_rif)
        form.addRow("Nombre:", self.edit_nombre)
        form.addRow("Tipo (P/J):", self.edit_tipo)
        form.addRow("Dirección:", self.edit_direccion)
        form.addRow("Email:", self.edit_email)
        
        detail_layout.addLayout(form)
        
        # Botones de Acción
        btn_save = QPushButton("Guardar Cambios")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4a54ff;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #3a44ee; }
        """)
        detail_layout.addWidget(btn_save)
        detail_layout.addStretch()

        layout.addWidget(self.detail_panel, stretch=1)