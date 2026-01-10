# src/bvc_gestor/ui/views/clientes_detail_view.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QFrame, QGridLayout, QLineEdit, 
                            QComboBox, QPushButton, QDateEdit, QRadioButton)
from PyQt6.QtCore import pyqtSignal, Qt, QDate

class ClienteDetalleView(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Barra Superior
        self.setup_toolbar()

        # 2. Área de Contenido con Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("ScrollArea")
        
        container = QWidget()
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(20, 0, 0, 0)
        self.content_layout.setSpacing(20)

        # --- SECCIONES (CARDS) ---
        self.setup_sections()

        scroll.setWidget(container)
        self.main_layout.addWidget(scroll)

    def setup_toolbar(self):
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(70)
        layout = QHBoxLayout(toolbar)
        
        btn_back = QPushButton("← Volver")
        btn_back.setFlat(True)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.back_clicked.emit)
        
        self.lbl_titulo = QLabel("Inversor")        
        self.btn_save = QPushButton("Guardar")
        self.btn_save.setObjectName("primaryButton")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setFixedWidth(100)
        self.btn_delete = QPushButton("Borrar")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setFixedWidth(100)
        
        layout.addWidget(btn_back)
        layout.addSpacing(20)
        layout.addWidget(self.lbl_titulo)
        layout.addStretch()
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_save)
        self.main_layout.addWidget(toolbar)

    def create_card(self, title):
        card = QFrame()
        card.setObjectName("Card")
        layout = QGridLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        title_lbl = QLabel(title.upper())
        layout.addWidget(title_lbl, 0, 0, 1, 4)
        
        return card, layout

    def setup_sections(self):
        # --- SECCIÓN 1: IDENTIDAD ---
        card1, lay1 = self.create_card("Identificación")
        
        self.edit_nombre = self.add_input(lay1, "Nombre Completo o Razón Social", 1, 0)
        self.edit_rif = self.add_input(lay1, "RIF / Cédula", 2, 0)
        self.combo_tipo_inversor = self.add_combo(lay1, "Tipo de Inversor", 2, 1)
        self.date_vence_rif = self.add_date(lay1, "Fecha de Vencimiento RIF", 2, 2)
        self.edit_email = self.add_input(lay1, "Correo Electrónico", 3, 0)
        self.edit_tlf = self.add_input(lay1, "Teléfono", 3, 1)
        self.edit_dir = self.add_input(lay1, "Dirección Fiscal", 4, 0)
        self.edit_ciudad = self.add_input(lay1, "Ciudad / Estado", 4, 1)
        
        self.content_layout.addWidget(card1)

        # --- SECCIÓN 2: Bancos ---
        card2, lay2 = self.create_card("Información Bancaria")


        # --- SECCIÓN 3: Cuenta bursatil ---
        card3, lay3 = self.create_card("Información de la Cuenta Bursátil")

        self.content_layout.addWidget(card3)
        self.content_layout.addStretch()

    # --- HELPERS PARA CREAR WIDGETS RÁPIDO ---
    def add_input(self, layout, label, row, col, colspan=1):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0,0,0,0)
        v.addWidget(QLabel(label))
        edit = QLineEdit()
        v.addWidget(edit)
        layout.addWidget(w, row, col, 1, colspan)
        return edit

    def add_combo(self, layout, label, row, col, colspan=1):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0,0,0,0)
        v.addWidget(QLabel(label))
        combo = QComboBox()
        v.addWidget(combo)
        layout.addWidget(w, row, col, 1, colspan)
        return combo
    

    def add_date(self, layout, label, row, col):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0,0,0,0)
        v.addWidget(QLabel(label))
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        v.addWidget(date_edit)
        layout.addWidget(w, row, col)
        return date_edit
    
    def obtener_datos_bancos(self):
        cuentas = []
        for i in range(self.v_lay.count()):
            widget = self.v_lay.itemAt(i).widget()
            if widget:
                combo = widget.findChild(QComboBox)
                edit = widget.findChild(QLineEdit)
                radio = widget.findChild(QRadioButton)
                if combo.currentData(): # Solo si seleccionó un banco
                    cuentas.append({
                        "id": combo.currentData(),
                        "numero": edit.text(),
                        "principal": radio.isChecked()
                    })
        return cuentas