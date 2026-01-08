# src/bvc_gestor/ui/views/clientes_detail_view.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, 
                             QScrollArea, QFrame, QGridLayout, QLineEdit, QComboBox, QPushButton)
from PyQt6.QtCore import pyqtSignal

class ClienteDetalleView(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Layout principal de la vista
        self.main_layout = QVBoxLayout(self) 
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 1. Header
        self.setup_header()

        # 2. Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.init_tab_general(), "Datos Fiscales")
        self.tabs.addTab(self.init_tab_financiera(), "Bancos y Cuentas")
        
        self.main_layout.addWidget(self.tabs)

        # 3. ACCIÓN: Botón de Guardar (El que faltaba)
        self.btn_save = QPushButton("Guardar Cambios")
        self.btn_save.setObjectName("primaryButton")
        self.btn_save.setFixedHeight(40)
        self.main_layout.addWidget(self.btn_save)

    def setup_header(self):
        header_frame = QFrame()
        header_frame.setObjectName("HeaderDetail")
        # El error de QLayout era porque intentamos meter el frame en sí mismo
        h_layout = QHBoxLayout(header_frame)
        
        btn_back = QPushButton("← Volver")
        btn_back.clicked.connect(self.back_clicked.emit)
        btn_back.setFixedWidth(100)
        
        self.lbl_nombre = QLabel("Cargando Cliente...")
        self.lbl_nombre.setStyleSheet("font-size: 22px; font-weight: bold;")
        
        h_layout.addWidget(btn_back)
        h_layout.addWidget(self.lbl_nombre)
        h_layout.addStretch()
        
        # Agregamos el frame al layout principal de la VISTA
        self.main_layout.addWidget(header_frame)

    def init_tab_general(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        form_layout = QGridLayout(container)
        
        # Definimos los campos como atributos de la clase (self.) 
        # para que el controlador pueda leerlos
        self.add_section_title(form_layout, "Identificación", 0)
        self.edit_rif = self.add_field(form_layout, "RIF:", 1, 0)
        self.edit_nombre = self.add_field(form_layout, "Nombre o Razón Social:", 1, 1)
        
        self.add_section_title(form_layout, "Contacto", 2)
        self.edit_email = self.add_field(form_layout, "Correo Electrónico:", 3, 0)
        self.edit_tlf = self.add_field(form_layout, "Teléfono Principal:", 3, 1)
        self.edit_dir = self.add_field(form_layout, "Dirección Fiscal:", 4, 0, colspan=2)
        self.edit_ciudad = self.add_field(form_layout, "Ciudad:", 5, 0)
        
        scroll.setWidget(container)
        return scroll

    def init_tab_financiera(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        
        bank_card = QFrame()
        bank_card.setObjectName("Card")
        bank_layout = QGridLayout(bank_card)
        
        self.add_section_title(bank_layout, "Configuración Bancaria", 0)
        self.combo_banco = self.add_combo(bank_layout, "Banco Asociado:", 1, 0)
        
        layout.addWidget(bank_card)
        layout.addStretch()
        return container

    # --- Helpers (Sin cambios, solo asegurar que devuelvan el widget) ---
    def add_section_title(self, layout, text, row):
        lbl = QLabel(text.upper())
        lbl.setStyleSheet("color: #FF6B00; font-weight: bold; font-size: 11px; margin: 10px 0;")
        layout.addWidget(lbl, row, 0, 1, 2)

    def add_field(self, layout, label_text, row, col, colspan=1):
        v_layout = QVBoxLayout()
        lbl = QLabel(label_text)
        edit = QLineEdit()
        v_layout.addWidget(lbl)
        v_layout.addWidget(edit)
        layout.addLayout(v_layout, row, col, 1, colspan)
        return edit

    def add_combo(self, layout, label_text, row, col):
        v_layout = QVBoxLayout()
        lbl = QLabel(label_text)
        combo = QComboBox()
        v_layout.addWidget(lbl)
        v_layout.addWidget(combo)
        layout.addLayout(v_layout, row, col)
        return combo