from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QDateEdit, QFrame)
from PyQt6.QtCore import QDate, Qt

class TransaccionesView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Contenedor del Ticket
        self.ticket_frame = QFrame()
        self.ticket_frame.setObjectName("ticketFrame")
        self.ticket_layout = QVBoxLayout(self.ticket_frame)
        self.ticket_layout.setSpacing(15)
        
        # Título del Ticket
        lbl_title = QLabel("NUEVA OPERACIÓN DE BOLSA")
        lbl_title.setObjectName("formTitle")
        self.ticket_layout.addWidget(lbl_title)

        # SECCIÓN 1: DATOS DE LA ORDEN
        self.add_section_title("Detalles de la Orden")
        self.combo_cliente = self.add_form_row("Cliente:", ["Seleccionar...", "Cliente A", "Cliente B"])
        self.combo_tipo = self.add_form_row("Tipo Operación:", ["COMPRA", "VENTA"])
        self.edit_simbolo = self.add_form_row("Símbolo/Ticker:", "Ej: TDV o MVZ.A")
        
        # SECCIÓN 2: VALORES FINANCIEROS
        self.add_section_title("Montos y Cantidades")
        self.edit_cantidad = self.add_form_row("Cantidad:", "0")
        self.edit_precio = self.add_form_row("Precio Unitario:", "0.00 Bs.")
        self.edit_comision = self.add_form_row("Comisión (%):", "1.0")

        # SECCIÓN 3: TIEMPO
        self.add_section_title("Fecha")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        # Reutilizamos el método para añadir la fila
        self.add_widget_row("Fecha Ejecución:", self.date_edit)

        # BOTÓN DE REGISTRO
        self.btn_registrar = QPushButton("REGISTRAR OPERACIÓN")
        self.btn_registrar.setObjectName("btnGuardar")
        self.ticket_layout.addWidget(self.btn_registrar)

        layout.addWidget(self.ticket_frame, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addStretch()

    def add_form_row(self, label_text, data):
        """Helper para crear filas de Combo o Input según los datos"""
        if isinstance(data, list):
            widget = QComboBox()
            widget.addItems(data)
        else:
            widget = QLineEdit()
            widget.setPlaceholderText(data)
        
        return self.add_widget_row(label_text, widget)

    def add_widget_row(self, label_text, widget):
        row_container = QWidget()
        row_layout = QHBoxLayout(row_container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(label_text)
        lbl.setObjectName("fieldLabel")
        lbl.setFixedWidth(150)
        
        row_layout.addWidget(lbl)
        row_layout.addWidget(widget)
        self.ticket_layout.addWidget(row_container)
        return widget

    def add_section_title(self, text):
        lbl = QLabel(text)
        lbl.setProperty("class", "sectionTitle")
        self.ticket_layout.addWidget(lbl)