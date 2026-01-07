from PyQt6.QtWidgets import (
QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
QLineEdit, QPushButton, QTableWidget, 
QTableWidgetItem, QHeaderView, QFrame, QFormLayout, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class ClientesView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # --- SECCIÓN IZQUIERDA: LISTA Y BÚSQUEDA ---
        left_panel = QVBoxLayout()
        
        # Buscador
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
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["RIF", "Nombre", "Estado"])
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

        # --- PANEL DERECHO: FORMULARIO DETALLADO ---
        form_container = QScrollArea()
        form_container.setObjectName("formContainer")
        form_container.setWidgetResizable(True)
        form_container.setFixedWidth(500)
        
        form_widget = QWidget()
        self.form_layout = QVBoxLayout(form_widget)
        self.form_layout.setSpacing(10)
        
        # Título
        lbl_form_title = QLabel("REGISTRO DE CLIENTE")
        lbl_form_title.setObjectName("formTitle")
        self.form_layout.addWidget(lbl_form_title)

        # SECCIÓN 1: IDENTIFICACIÓN BÁSICA
        self.add_section_title("Identificación")
        self.edit_rif = self.add_form_row("RIF:", "J-00000000-0")
        self.edit_nombre = self.add_form_row("Razón Social:", "Nombre de la empresa o persona")
        
        # Selector de Tipo con Label
        self.combo_tipo = self.add_combo_row("Tipo de Persona:", ["Natural", "Jurídica", "Gubernamental"])

        # SECCIÓN 2: LOCALIZACIÓN Y CONTACTO
        self.add_section_title("Dirección y Contacto")
        self.edit_direccion = self.add_form_row("Dirección Fiscal:", "Calle, Edificio, Oficina...")
        self.edit_ciudad = self.add_form_row("Ciudad/Estado:", "Ej: Caracas, Miranda")
        self.edit_correo = self.add_form_row("Email:", "ejemplo@correo.com")
        self.edit_tlf = self.add_form_row("Teléfono:", "+58...")

        # Botón de Acción
        self.btn_save = QPushButton("REGISTRAR CLIENTE EN SISTEMA")
        self.btn_save.setObjectName("btnGuardar")
        self.form_layout.addWidget(self.btn_save)
        
        self.form_layout.addStretch()
        form_container.setWidget(form_widget)
        layout.addWidget(form_container)

    def add_form_row(self, label_text, placeholder):
        """Crea una fila con Label e Input"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 5, 0, 5)

        lbl = QLabel(label_text)
        lbl.setObjectName("fieldLabel")
        lbl.setFixedWidth(120) # Ancho fijo para que todos los inputs queden alineados
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        
        row_layout.addWidget(lbl)
        row_layout.addWidget(edit)
        self.form_layout.addWidget(row_widget)
        return edit

    def add_combo_row(self, label_text, items):
        """Crea una fila con Label y ComboBox"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 5, 0, 5)

        lbl = QLabel(label_text)
        lbl.setObjectName("fieldLabel")
        lbl.setFixedWidth(120)

        combo = QComboBox()
        combo.addItems(items)
        
        row_layout.addWidget(lbl)
        row_layout.addWidget(combo)
        self.form_layout.addWidget(row_widget)
        return combo

    def add_section_title(self, text):
        lbl = QLabel(text)
        lbl.setProperty("class", "sectionTitle")
        self.form_layout.addWidget(lbl)