# src/bvc_gestor/ui/widgets/clientes_widget.py
"""
Widget de gestión de clientes
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QToolBar,
    QStatusBar, QSplitter, QFrame, QGroupBox, QTextEdit,
    QDateEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTabWidget,
    QFormLayout, QScrollArea, QSizePolicy, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTimer, QSize
from PyQt6.QtGui import QIcon, QFont, QAction, QKeySequence, QShortcut, QIntValidator
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from ...core.app_state import AppState
from ...utils.logger import logger
from ...utils.validators_venezuela import (
    validar_cedula, validar_rif, validar_telefono_venezolano,
    formatear_telefono, extraer_tipo_identificacion
)
from ...utils.constants import TipoPersona, TipoDocumento, PerfilRiesgo
from ...database.engine import get_database
from ...database.repositories import RepositoryFactory
from ...database.models_sql import ClienteDB, CuentaDB

class ClientesTableWidget(QTableWidget):
    """Tabla personalizada para clientes"""
    
    # Señal emitida al seleccionar un cliente (ID)
    cliente_selected = pyqtSignal(str)  
    
    # Inicializar tabla de clientes
    def __init__(self): 
        super().__init__()
        self.setup_ui()
        self.selected_client_id = None
    
    # Configurar interfaz de la tabla
    def setup_ui(self): 
        """Configurar interfaz de la tabla"""
        # Configurar columnas
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Teléfono", "Email", 
            "Perfil Riesgo", "Capital ($)", "Estado"
        ])
        
        # Configurar propiedades de la tabla
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        
        # Ajustar ancho de columnas
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Tipo
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)           # Email
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Perfil
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Capital
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        
        # Conectar señal de selección
        self.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Estilo
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #2c5aa0;
                color: white;
            }
        """)
    
    def load_clientes(self, clientes: List[ClienteDB]):
        """Cargar clientes en la tabla"""
        self.setRowCount(0)  # Limpiar tabla
        
        for row, cliente in enumerate(clientes):
            self.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(cliente.id)
            id_item.setData(Qt.ItemDataRole.UserRole, cliente.id)
            self.setItem(row, 0, id_item)
            
            # Nombre
            nombre_item = QTableWidgetItem(cliente.nombre_completo)
            self.setItem(row, 1, nombre_item)
            
            # Tipo
            tipo_item = QTableWidgetItem(cliente.tipo_persona.value)
            self.setItem(row, 2, tipo_item)
            
            # Teléfono
            telefono_item = QTableWidgetItem(cliente.telefono_principal)
            self.setItem(row, 3, telefono_item)
            
            # Email
            email_item = QTableWidgetItem(cliente.email)
            self.setItem(row, 4, email_item)
            
            # Perfil de riesgo
            perfil_item = QTableWidgetItem(cliente.perfil_riesgo.value)
            self.setItem(row, 5, perfil_item)
            
            # Capital (usamos el límite de inversión como referencia)
            capital = float(cliente.limite_inversion_usd or 0)
            capital_item = QTableWidgetItem(f"${capital:,.2f}")
            capital_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row, 6, capital_item)
            
            # Estado
            estado_item = QTableWidgetItem("Activo" if cliente.activo else "Inactivo")
            estado_item.setForeground(Qt.GlobalColor.green if cliente.activo else Qt.GlobalColor.red)
            self.setItem(row, 7, estado_item)
    
    def get_selected_client_id(self) -> Optional[str]:
        """Obtener ID del cliente seleccionado"""
        selected_items = self.selectedItems()
        if selected_items:
            # El ID está en la columna 0
            for item in selected_items:
                if item.column() == 0:
                    return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def on_selection_changed(self):
        """Manejar cambio de selección"""
        client_id = self.get_selected_client_id()
        if client_id:
            self.selected_client_id = client_id
            self.cliente_selected.emit(client_id)

class ClienteFormWidget(QDialog):
    """Formulario para crear/editar clientes"""
    
    # Señales del formulario
    cliente_saved = pyqtSignal(dict)  # Guardar cliente
    form_cleared = pyqtSignal() # Borrar Datos del formulario
    
    # Inicializar formulario
    """def __init__(self, mode: str = "nuevo"):  # "nuevo" o "editar"
        super().__init__()
        self.mode = mode
        self.current_cliente_id = None
        self.setup_ui()
        self.setup_connections()"""

    def __init__(self, mode: str = "nuevo", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.current_cliente_id = None
        self.setup_ui()
        self.setup_connections()
        self.setWindowTitle("Nueva Orden Bursátil")
        self.resize(700, 600)
    
    # Configurar interfaz del formulario
    def setup_ui(self):
        """Configurar interfaz del formulario"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Título del formulario
        title = "Nuevo Cliente" if self.mode == "nuevo" else "Editar Cliente"
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c5aa0;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Área desplazable para formulario largo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_widget.setLayout(form_layout)
        
        # Pestañas para organizar el formulario
        tab_widget = QTabWidget()
        form_layout.addWidget(tab_widget)
        
        # Pestaña 1: Información básica
        basic_tab = QWidget()
        basic_layout = QFormLayout()
        basic_layout.setSpacing(10)
        basic_tab.setLayout(basic_layout)
        
        # Tipo de persona
        self.tipo_persona_combo = QComboBox()
        self.tipo_persona_combo.addItems([t.value for t in TipoPersona])
        self.tipo_persona_combo.currentTextChanged.connect(self.on_tipo_persona_changed)
        basic_layout.addRow("Tipo de Persona:", self.tipo_persona_combo)
        
        # Tipo de documento (se actualiza automáticamente)
        self.tipo_documento_label = QLabel()
        basic_layout.addRow("Tipo Documento:", self.tipo_documento_label)
        
        # Identificación
        self.identificacion_edit = QLineEdit()
        self.identificacion_edit.setPlaceholderText("V-12345678 o J-12345678-9")
        self.identificacion_edit.setMaxLength(12)
        basic_layout.addRow("Cédula/RIF:", self.identificacion_edit)
        
        # Nombre completo
        self.nombre_edit = QLineEdit()
        self.nombre_edit.setPlaceholderText("Nombre completo o razón social")
        self.nombre_edit.setMaxLength(40)
        basic_layout.addRow("Nombre Completo:", self.nombre_edit)
        
        # Fecha de nacimiento (solo para naturales)
        self.fecha_nacimiento_edit = QDateEdit()
        self.fecha_nacimiento_edit.setCalendarPopup(True)
        self.fecha_nacimiento_edit.setMaximumDate(QDate.currentDate())
        self.fecha_nacimiento_edit.setDisplayFormat("dd/MM/yyyy")
        basic_layout.addRow("Fecha Nacimiento:", self.fecha_nacimiento_edit)
        
        # Profesión/ocupación
        self.profesion_edit = QLineEdit()
        self.profesion_edit.setPlaceholderText("Profesión u ocupación del cliente")
        self.profesion_edit.setMaxLength(20)
        basic_layout.addRow("Profesión/Ocupación:", self.profesion_edit)
        
        tab_widget.addTab(basic_tab, "Información Básica")
        
        # Pestaña 2: Contacto
        contact_tab = QWidget()
        contact_layout = QFormLayout()
        contact_layout.setSpacing(10)
        contact_tab.setLayout(contact_layout)
        
        # Teléfono principal
        self.telefono_principal_edit = QLineEdit()
        self.telefono_principal_edit.setPlaceholderText("0414-1234567")
        self.telefono_principal_edit.setMaxLength(13)
        self.telefono_principal_edit.setValidator(QIntValidator())
        contact_layout.addRow("Teléfono Principal:", self.telefono_principal_edit)
        
        # Teléfono secundario
        self.telefono_secundario_edit = QLineEdit()
        self.telefono_secundario_edit.setPlaceholderText("0212-1234567 (Opcional)")
        self.telefono_secundario_edit.setMaxLength(13)
        self.telefono_secundario_edit.setValidator(QIntValidator())
        contact_layout.addRow("Teléfono Secundario:", self.telefono_secundario_edit)
        
        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("cliente@email.com")
        self.email_edit.setMaxLength(50)
        contact_layout.addRow("Email:", self.email_edit)
        
        # Dirección
        self.direccion_edit = QLineEdit()
        self.direccion_edit.setPlaceholderText("Calle, urbanización, edificio, apartamento")
        self.direccion_edit.setMaxLength(50)
        contact_layout.addRow("Dirección:", self.direccion_edit)
        
        # Ciudad
        self.ciudad_edit = QLineEdit()
        self.ciudad_edit.setPlaceholderText("Caracas")
        self.ciudad_edit.setMaxLength(20)
        contact_layout.addRow("Ciudad:", self.ciudad_edit)
        
        # Estado
        self.estado_edit = QLineEdit()
        self.estado_edit.setPlaceholderText("Distrito Capital")
        self.estado_edit.setMaxLength(20)
        contact_layout.addRow("Estado:", self.estado_edit)
        
        tab_widget.addTab(contact_tab, "Contacto")
        
        # Pestaña 3: Información financiera
        financial_tab = QWidget()
        financial_layout = QFormLayout()
        financial_layout.setSpacing(10)
        financial_tab.setLayout(financial_layout)
        
        # Perfil de riesgo
        self.perfil_riesgo_combo = QComboBox()
        self.perfil_riesgo_combo.addItems([p.value for p in PerfilRiesgo])
        financial_layout.addRow("Perfil de Riesgo:", self.perfil_riesgo_combo)
        
        # Límites de inversión
        financial_layout.addRow(QLabel("<b>Límites de Inversión</b>"))
        
        # Límite en USD
        self.limite_usd_spin = QDoubleSpinBox()
        self.limite_usd_spin.setRange(0, 10000000)
        self.limite_usd_spin.setPrefix("$ ")
        self.limite_usd_spin.setDecimals(2)
        financial_layout.addRow("Límite USD:", self.limite_usd_spin)
        
        # Límite en Bs
        self.limite_bs_spin = QDoubleSpinBox()
        self.limite_bs_spin.setRange(0, 100000000000)
        self.limite_bs_spin.setPrefix("Bs ")
        self.limite_bs_spin.setDecimals(2)
        financial_layout.addRow("Límite Bs:", self.limite_bs_spin)
        
        # Ingresos mensuales
        financial_layout.addRow(QLabel("<b>Ingresos Mensuales</b>"))
        
        self.ingresos_usd_spin = QDoubleSpinBox()
        self.ingresos_usd_spin.setRange(0, 1000000)
        self.ingresos_usd_spin.setPrefix("$ ")
        self.ingresos_usd_spin.setDecimals(2)
        financial_layout.addRow("Ingresos USD:", self.ingresos_usd_spin)
        
        self.ingresos_bs_spin = QDoubleSpinBox()
        self.ingresos_bs_spin.setRange(0, 10000000000)
        self.ingresos_bs_spin.setPrefix("Bs ")
        self.ingresos_bs_spin.setDecimals(2)
        financial_layout.addRow("Ingresos Bs:", self.ingresos_bs_spin)
        
        tab_widget.addTab(financial_tab, "Financiero")
        
        # Pestaña 4: Información bancaria
        bank_tab = QWidget()
        bank_layout = QFormLayout()
        bank_layout.setSpacing(10)
        bank_tab.setLayout(bank_layout)
        
        # Banco principal
        self.banco_edit = QLineEdit()
        self.banco_edit.setPlaceholderText("Banco de Venezuela, Banesco, etc.")
        self.banco_edit.setMaxLength(30)
        bank_layout.addRow("Banco Principal:", self.banco_edit)
        
        # Número de cuenta
        self.numero_cuenta_edit = QLineEdit()
        self.numero_cuenta_edit.setPlaceholderText("Número de cuenta bancaria")
        self.numero_cuenta_edit.setMaxLength(30)
        self.numero_cuenta_edit.setValidator(QIntValidator())
        bank_layout.addRow("Número de Cuenta:", self.numero_cuenta_edit)
        
        # Tipo de cuenta
        self.tipo_cuenta_combo = QComboBox()
        self.tipo_cuenta_combo.addItems(["Ahorros", "Corriente", "No especificado"])
        bank_layout.addRow("Tipo de Cuenta:", self.tipo_cuenta_combo)
        
        # Patrimonio declarado
        self.patrimonio_check = QCheckBox("¿Tiene patrimonio declarado?")
        self.patrimonio_check.stateChanged.connect(self.on_patrimonio_changed)
        bank_layout.addRow(self.patrimonio_check)
        
        # Monto patrimonio USD (inicialmente deshabilitado)
        self.patrimonio_usd_spin = QDoubleSpinBox()
        self.patrimonio_usd_spin.setRange(0, 10000000)
        self.patrimonio_usd_spin.setPrefix("$ ")
        self.patrimonio_usd_spin.setDecimals(2)
        self.patrimonio_usd_spin.setEnabled(False)
        bank_layout.addRow("Patrimonio USD:", self.patrimonio_usd_spin)
        
        # Monto patrimonio Bs
        self.patrimonio_bs_spin = QDoubleSpinBox()
        self.patrimonio_bs_spin.setRange(0, 100000000000)
        self.patrimonio_bs_spin.setPrefix("Bs ")
        self.patrimonio_bs_spin.setDecimals(2)
        self.patrimonio_bs_spin.setEnabled(False)
        bank_layout.addRow("Patrimonio Bs:", self.patrimonio_bs_spin)
        
        tab_widget.addTab(bank_tab, "Bancario")
        
        # Pestaña 5: Notas
        notes_tab = QWidget()
        notes_layout = QVBoxLayout()
        notes_tab.setLayout(notes_layout)
        
        self.notas_edit = QLineEdit()
        self.notas_edit.setPlaceholderText("Notas adicionales sobre el cliente...")
        self.notas_edit.setMaxLength(80)
        notes_layout.addWidget(self.notas_edit)
        
        tab_widget.addTab(notes_tab, "Notas")
        
        scroll_area.setWidget(form_widget)
        layout.addWidget(scroll_area)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.guardar_btn = QPushButton("💾 Guardar")
        self.guardar_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(self.guardar_btn)
        
        self.limpiar_btn = QPushButton("🗑️ Limpiar")
        self.limpiar_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        button_layout.addWidget(self.limpiar_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Configurar tamaño
        self.setMinimumWidth(500)
        
        # Actualizar tipo de documento inicial
        self.on_tipo_persona_changed(self.tipo_persona_combo.currentText())
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        self.guardar_btn.clicked.connect(self.guardar_cliente)
        self.limpiar_btn.clicked.connect(self.limpiar_formulario)
        
        # Validación en tiempo real
        self.identificacion_edit.textChanged.connect(self.validar_identificacion)
        self.telefono_principal_edit.textChanged.connect(self.validar_telefono)
        self.email_edit.textChanged.connect(self.validar_email)
    
    def on_tipo_persona_changed(self, tipo: str):
        """Manejar cambio en tipo de persona"""
        if tipo == TipoPersona.NATURAL.value:
            self.tipo_documento_label.setText(TipoDocumento.CEDULA.value)
            self.fecha_nacimiento_edit.setEnabled(True)
        else:
            self.tipo_documento_label.setText(TipoDocumento.RIF.value)
            self.fecha_nacimiento_edit.setEnabled(False)
    
    def on_patrimonio_changed(self, state: int):
        """Manejar cambio en checkbox de patrimonio"""
        enabled = state == Qt.CheckState.Checked.value
        self.patrimonio_usd_spin.setEnabled(enabled)
        self.patrimonio_bs_spin.setEnabled(enabled)
    
    def validar_identificacion(self):
        """Validar identificación en tiempo real"""
        identificacion = self.identificacion_edit.text().strip()
        tipo_persona = self.tipo_persona_combo.currentText()
        
        if not identificacion:
            self.identificacion_edit.setStyleSheet("")
            return
        
        if tipo_persona == TipoPersona.NATURAL.value:
            valido = validar_cedula(identificacion)
        else:
            valido = validar_rif(identificacion)
        
        if valido:
            self.identificacion_edit.setStyleSheet("border: 2px solid #28a745;")
        else:
            self.identificacion_edit.setStyleSheet("border: 2px solid #dc3545;")
    
    def validar_telefono(self):
        """Validar teléfono en tiempo real"""
        telefono = self.telefono_principal_edit.text().strip()
        
        if not telefono:
            self.telefono_principal_edit.setStyleSheet("")
            return
        
        if validar_telefono_venezolano(telefono):
            self.telefono_principal_edit.setStyleSheet("border: 2px solid #28a745;")
        else:
            self.telefono_principal_edit.setStyleSheet("border: 2px solid #dc3545;")
    
    def validar_email(self):
        """Validar email en tiempo real"""
        email = self.email_edit.text().strip()
        
        if not email:
            self.email_edit.setStyleSheet("")
            return
        
        if '@' in email and '.' in email:
            self.email_edit.setStyleSheet("border: 2px solid #28a745;")
        else:
            self.email_edit.setStyleSheet("border: 2px solid #dc3545;")
    
    def get_form_data(self) -> Dict[str, Any]:
        """Obtener datos del formulario"""
        datos = {
            'id': self.identificacion_edit.text().strip().upper(),
            'tipo_persona': self.tipo_persona_combo.currentText(),
            'tipo_documento': self.tipo_documento_label.text(),
            'nombre_completo': self.nombre_edit.text().strip(),
            'fecha_nacimiento': self.fecha_nacimiento_edit.date().toPyDate() if self.fecha_nacimiento_edit.isEnabled() else None,
            'profesion_ocupacion': self.profesion_edit.text().strip(),
            'telefono_principal': self.telefono_principal_edit.text().strip(),
            'telefono_secundario': self.telefono_secundario_edit.text().strip() or None,
            'email': self.email_edit.text().strip().lower(),
            'direccion': self.direccion_edit.text().strip(),
            'ciudad': self.ciudad_edit.text().strip(),
            'estado': self.estado_edit.text().strip(),
            'perfil_riesgo': self.perfil_riesgo_combo.currentText(),
            'limite_inversion_usd': float(self.limite_usd_spin.value()),
            'limite_inversion_bs': float(self.limite_bs_spin.value()),
            'ingresos_mensuales_usd': float(self.ingresos_usd_spin.value()) if self.ingresos_usd_spin.value() > 0 else None,
            'ingresos_mensuales_bs': float(self.ingresos_bs_spin.value()) if self.ingresos_bs_spin.value() > 0 else None,
            'banco_principal': self.banco_edit.text().strip() or None,
            'numero_cuenta': self.numero_cuenta_edit.text().strip() or None,
            'tipo_cuenta': self.tipo_cuenta_combo.currentText() if self.tipo_cuenta_combo.currentText() != "No especificado" else None,
            'tiene_patrimonio_declarado': self.patrimonio_check.isChecked(),
            'monto_patrimonio_usd': float(self.patrimonio_usd_spin.value()) if self.patrimonio_check.isChecked() else None,
            'monto_patrimonio_bs': float(self.patrimonio_bs_spin.value()) if self.patrimonio_check.isChecked() else None,
            'notas': self.notas_edit.text().strip() or None,
            'activo': True
        }
        return datos
    
    def validar_formulario(self) -> tuple[bool, str]:
        """Validar todos los campos del formulario"""
        datos = self.get_form_data()
        
        # Validar campos obligatorios
        campos_obligatorios = [
            ('id', 'Identificación'),
            ('nombre_completo', 'Nombre completo'),
            ('telefono_principal', 'Teléfono principal'),
            ('email', 'Email'),
            ('direccion', 'Dirección'),
            ('ciudad', 'Ciudad'),
            ('estado', 'Estado')
        ]
        
        for campo, nombre in campos_obligatorios:
            if not datos[campo]:
                return False, f"El campo '{nombre}' es obligatorio"
        
        # Validar identificación
        if datos['tipo_persona'] == TipoPersona.NATURAL.value:
            if not validar_cedula(datos['id']):
                return False, "Cédula inválida"
        else:
            if not validar_rif(datos['id']):
                return False, "RIF inválido"
        
        # Validar teléfono
        if not validar_telefono_venezolano(datos['telefono_principal']):
            return False, "Teléfono inválido"
        
        # Validar email básico
        if '@' not in datos['email'] or '.' not in datos['email']:
            return False, "Email inválido"
        
        return True, "OK"
    
    def guardar_cliente(self):
        """Guardar cliente desde formulario"""
        valido, mensaje = self.validar_formulario()
        
        if not valido:
            QMessageBox.warning(self, "Validación", mensaje)
            return
        
        datos = self.get_form_data()
        
        # Formatear teléfono
        datos['telefono_principal'] = formatear_telefono(datos['telefono_principal'])
        if datos['telefono_secundario']:
            datos['telefono_secundario'] = formatear_telefono(datos['telefono_secundario'])
        
        # Emitir señal con datos del cliente
        self.cliente_saved.emit(datos)
        
        # Limpiar formulario si es modo nuevo
        if self.mode == "nuevo":
            self.limpiar_formulario()
        
        QMessageBox.information(self, "Éxito", "Cliente guardado correctamente")
    
    def limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        self.identificacion_edit.clear()
        self.nombre_edit.clear()
        self.telefono_principal_edit.clear()
        self.telefono_secundario_edit.clear()
        self.email_edit.clear()
        self.direccion_edit.clear()
        self.ciudad_edit.clear()
        self.estado_edit.clear()
        self.profesion_edit.clear()
        self.banco_edit.clear()
        self.numero_cuenta_edit.clear()
        self.notas_edit.clear()
        
        # Restablecer valores por defecto
        self.tipo_persona_combo.setCurrentIndex(0)
        self.perfil_riesgo_combo.setCurrentIndex(1)  # Moderado
        self.fecha_nacimiento_edit.setDate(QDate.currentDate().addYears(-30))
        self.limite_usd_spin.setValue(0)
        self.limite_bs_spin.setValue(0)
        self.ingresos_usd_spin.setValue(0)
        self.ingresos_bs_spin.setValue(0)
        self.tipo_cuenta_combo.setCurrentIndex(2)  # No especificado
        self.patrimonio_check.setChecked(False)
        self.patrimonio_usd_spin.setValue(0)
        self.patrimonio_bs_spin.setValue(0)
        
        # Limpiar estilos de validación
        self.identificacion_edit.setStyleSheet("")
        self.telefono_principal_edit.setStyleSheet("")
        self.email_edit.setStyleSheet("")
        
        # Emitir señal
        self.form_cleared.emit()
    
    def cargar_cliente(self, cliente: ClienteDB):
        """Cargar datos de cliente en formulario"""
        self.current_cliente_id = cliente.id
        
        # Información básica
        self.identificacion_edit.setText(cliente.id)
        self.identificacion_edit.setEnabled(False)  # No se puede cambiar ID
        
        # Encontrar índice del tipo de persona
        tipo_index = self.tipo_persona_combo.findText(cliente.tipo_persona.value)
        if tipo_index >= 0:
            self.tipo_persona_combo.setCurrentIndex(tipo_index)
        
        self.nombre_edit.setText(cliente.nombre_completo)
        
        if cliente.fecha_nacimiento:
            self.fecha_nacimiento_edit.setDate(QDate(
                cliente.fecha_nacimiento.year,
                cliente.fecha_nacimiento.month,
                cliente.fecha_nacimiento.day
            ))
        
        if cliente.profesion_ocupacion:
            self.profesion_edit.setText(cliente.profesion_ocupacion)
        
        # Contacto
        self.telefono_principal_edit.setText(cliente.telefono_principal)
        
        if cliente.telefono_secundario:
            self.telefono_secundario_edit.setText(cliente.telefono_secundario)
        
        self.email_edit.setText(cliente.email)
        self.direccion_edit.setText(cliente.direccion)
        self.ciudad_edit.setText(cliente.ciudad)
        self.estado_edit.setText(cliente.estado)
        
        # Información financiera
        perfil_index = self.perfil_riesgo_combo.findText(cliente.perfil_riesgo.value)
        if perfil_index >= 0:
            self.perfil_riesgo_combo.setCurrentIndex(perfil_index)
        
        self.limite_usd_spin.setValue(float(cliente.limite_inversion_usd or 0))
        self.limite_bs_spin.setValue(float(cliente.limite_inversion_bs or 0))
        
        if cliente.ingresos_mensuales_usd:
            self.ingresos_usd_spin.setValue(float(cliente.ingresos_mensuales_usd))
        
        if cliente.ingresos_mensuales_bs:
            self.ingresos_bs_spin.setValue(float(cliente.ingresos_mensuales_bs))
        
        # Información bancaria
        if cliente.banco_principal:
            self.banco_edit.setText(cliente.banco_principal)
        
        if cliente.numero_cuenta:
            self.numero_cuenta_edit.setText(cliente.numero_cuenta)
        
        if cliente.tipo_cuenta:
            tipo_index = self.tipo_cuenta_combo.findText(cliente.tipo_cuenta)
            if tipo_index >= 0:
                self.tipo_cuenta_combo.setCurrentIndex(tipo_index)
        
        self.patrimonio_check.setChecked(cliente.tiene_patrimonio_declarado)
        
        if cliente.monto_patrimonio_usd:
            self.patrimonio_usd_spin.setValue(float(cliente.monto_patrimonio_usd))
        
        if cliente.monto_patrimonio_bs:
            self.patrimonio_bs_spin.setValue(float(cliente.monto_patrimonio_bs))
        
        # Notas
        if cliente.notas:
            self.notas_edit.setText(cliente.notas)\

class ClientesWidget(QWidget):
    """Widget principal de gestión de clientes"""
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.db_session = None
        self.cliente_repo = None
        self.current_cliente_id = None
        self.setup_ui()
        self.setup_connections()
        self.load_clientes()
        logger.info("ClientesWidget inicializado")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Barra de herramientas
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        
        # Acciones de la barra de herramientas
        self.nuevo_action = QAction("➕ Nuevo", self)
        self.nuevo_action.setToolTip("Nuevo cliente")
        
        self.editar_action = QAction("✏️ Editar", self)
        self.editar_action.setToolTip("Editar cliente seleccionado")
        self.editar_action.setEnabled(False)
        
        self.eliminar_action = QAction("🗑️ Eliminar", self)
        self.eliminar_action.setToolTip("Eliminar cliente seleccionado")
        self.eliminar_action.setEnabled(False)
        
        self.exportar_action = QAction("📤 Exportar", self)
        self.exportar_action.setToolTip("Exportar clientes a Excel")
        
        self.refresh_action = QAction("🔄 Actualizar", self)
        self.refresh_action.setToolTip("Actualizar lista de clientes")
        
        toolbar.addAction(self.nuevo_action)
        toolbar.addAction(self.editar_action)
        toolbar.addAction(self.eliminar_action)
        toolbar.addSeparator()
        toolbar.addAction(self.exportar_action)
        toolbar.addSeparator()
        toolbar.addAction(self.refresh_action)
        
        # Barra de búsqueda
        toolbar.addWidget(QLabel("   Buscar:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Nombre, cédula, email...")
        self.search_edit.setMaximumWidth(300)
        toolbar.addWidget(self.search_edit)
        
        main_layout.addWidget(toolbar)
        
        # Splitter para dividir tabla y formulario
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Tabla de clientes
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Título de tabla
        table_title = QLabel("📋 Lista de Clientes")
        table_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #495057;
                margin-bottom: 10px;
            }
        """)
        left_layout.addWidget(table_title)
        
        # Tabla de clientes
        self.clientes_table = ClientesTableWidget()
        left_layout.addWidget(self.clientes_table)
        
        # Contador de clientes
        self.contador_label = QLabel("Total: 0 clientes")
        self.contador_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        left_layout.addWidget(self.contador_label)
        
        splitter.addWidget(left_panel)
        
        # Panel derecho: Formulario y detalles
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Pestañas para formulario y detalles
        self.right_tabs = QTabWidget()
        
        # Pestaña 1: Formulario
        self.form_widget = ClienteFormWidget(mode="nuevo")
        self.right_tabs.addTab(self.form_widget, "📝 Formulario")
        
        # Pestaña 2: Detalles del cliente
        self.detalles_widget = QWidget()
        detalles_layout = QVBoxLayout()
        self.detalles_widget.setLayout(detalles_layout)
        
        self.detalles_label = QLabel("👤 Seleccione un cliente para ver sus detalles")
        self.detalles_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detalles_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
                font-style: italic;
                margin-top: 50px;
            }
        """)
        detalles_layout.addWidget(self.detalles_label)
        
        self.right_tabs.addTab(self.detalles_widget, "👤 Detalles")
        
        right_layout.addWidget(self.right_tabs)
        
        splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        splitter.setSizes([500, 300])
        
        main_layout.addWidget(splitter, 1)  # Factor de expansión 1
        
        # Barra de estado inferior
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Listo")
        main_layout.addWidget(self.status_bar)
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Acciones de toolbar
        self.nuevo_action.triggered.connect(self.nuevo_cliente)
        self.editar_action.triggered.connect(self.editar_cliente)
        self.eliminar_action.triggered.connect(self.eliminar_cliente)
        self.exportar_action.triggered.connect(self.exportar_clientes)
        self.refresh_action.triggered.connect(self.load_clientes)
        
        # Búsqueda
        self.search_edit.textChanged.connect(self.buscar_clientes)
        
        # Tabla
        self.clientes_table.cliente_selected.connect(self.on_cliente_selected)
        
        # Formulario
        self.form_widget.cliente_saved.connect(self.guardar_cliente_desde_form)
        self.form_widget.form_cleared.connect(self.on_form_cleared)
        
        # Atajos de teclado
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.nuevo_cliente)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.guardar_cliente_desde_form)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(lambda: self.search_edit.setFocus())
        QShortcut(QKeySequence("F5"), self).activated.connect(self.load_clientes)
    
    def obtener_sesion_db(self):
        """Obtener sesión de base de datos"""
        if self.db_session is None:
            self.db_session = get_database().get_session()
            self.cliente_repo = RepositoryFactory.get_repository(self.db_session, 'cliente')
        return self.db_session
    
    def load_clientes(self):
        """Cargar clientes desde base de datos"""
        try:
            self.obtener_sesion_db()
            
            # Obtener todos los clientes
            clientes = self.cliente_repo.get_all()
            
            # Cargar en tabla
            self.clientes_table.load_clientes(clientes)
            
            # Actualizar contador
            total = len(clientes)
            activos = len([c for c in clientes if c.activo])
            self.contador_label.setText(f"Total: {total} clientes ({activos} activos)")
            
            self.status_bar.showMessage(f"Cargados {total} clientes", 3000)
            logger.info(f"Cargados {total} clientes")
            
        except Exception as e:
            logger.error(f"Error cargando clientes: {e}")
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los clientes: {str(e)}")
    
    def buscar_clientes(self):
        """Buscar clientes por texto"""
        query = self.search_edit.text().strip()
        
        if not query:
            self.load_clientes()
            return
        
        try:
            self.obtener_sesion_db()
            
            # Buscar usando el repositorio
            resultados = self.cliente_repo.search(query)
            
            # Cargar resultados en tabla
            self.clientes_table.load_clientes(resultados)
            
            # Actualizar contador
            self.contador_label.setText(f"Encontrados: {len(resultados)} clientes")
            
            self.status_bar.showMessage(f"Búsqueda: '{query}' - {len(resultados)} resultados", 3000)
            
        except Exception as e:
            logger.error(f"Error buscando clientes: {e}")
    
    def on_cliente_selected(self, cliente_id: str):
        """Manejar selección de cliente en tabla"""
        self.current_cliente_id = cliente_id
        
        # Habilitar acciones de editar/eliminar
        self.editar_action.setEnabled(True)
        self.eliminar_action.setEnabled(True)
        
        # Cargar detalles del cliente
        self.cargar_detalles_cliente(cliente_id)
        
        # Cambiar a pestaña de detalles
        self.right_tabs.setCurrentIndex(1)
    
    def cargar_detalles_cliente(self, cliente_id: str):
        """Cargar detalles del cliente seleccionado"""
        try:
            self.obtener_sesion_db()
            
            cliente = self.cliente_repo.get(cliente_id)
            if not cliente:
                return
            
            # Crear widget de detalles
            self.actualizar_widget_detalles(cliente)
            
        except Exception as e:
            logger.error(f"Error cargando detalles del cliente: {e}")
    
    def actualizar_widget_detalles(self, cliente: ClienteDB):
        """Actualizar widget de detalles con información del cliente"""
        # Limpiar widget actual
        while self.detalles_widget.layout().count():
            item = self.detalles_widget.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Crear scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        detalles_container = QWidget()
        detalles_layout = QVBoxLayout()
        detalles_container.setLayout(detalles_layout)
        
        # Título
        title_label = QLabel(f"👤 {cliente.nombre_completo}")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c5aa0;
                margin-bottom: 20px;
            }
        """)
        detalles_layout.addWidget(title_label)
        
        # Información en grupos
        grupos = [
            ("📋 Información Básica", [
                f"<b>Identificación:</b> {cliente.id}",
                f"<b>Tipo:</b> {cliente.tipo_persona.value}",
                f"<b>Documento:</b> {cliente.tipo_documento.value}",
                f"<b>Fecha Registro:</b> {cliente.fecha_registro.strftime('%d/%m/%Y')}",
                f"<b>Estado:</b> {'🟢 Activo' if cliente.activo else '🔴 Inactivo'}"
            ]),
            
            ("📞 Contacto", [
                f"<b>Teléfono:</b> {cliente.telefono_principal}",
                f"<b>Teléfono Secundario:</b> {cliente.telefono_secundario or 'No especificado'}",
                f"<b>Email:</b> {cliente.email}",
                f"<b>Dirección:</b> {cliente.direccion}",
                f"<b>Ciudad/Estado:</b> {cliente.ciudad}, {cliente.estado}"
            ]),
            
            ("💰 Información Financiera", [
                f"<b>Perfil de Riesgo:</b> {cliente.perfil_riesgo.value}",
                f"<b>Límite Inversión USD:</b> ${float(cliente.limite_inversion_usd or 0):,.2f}",
                f"<b>Límite Inversión Bs:</b> Bs {float(cliente.limite_inversion_bs or 0):,.2f}",
                f"<b>Ingresos Mensuales USD:</b> ${float(cliente.ingresos_mensuales_usd or 0):,.2f}",
                f"<b>Ingresos Mensuales Bs:</b> Bs {float(cliente.ingresos_mensuales_bs or 0):,.2f}"
            ]),
            
            ("🏦 Información Bancaria", [
                f"<b>Banco Principal:</b> {cliente.banco_principal or 'No especificado'}",
                f"<b>Número de Cuenta:</b> {cliente.numero_cuenta or 'No especificado'}",
                f"<b>Tipo de Cuenta:</b> {cliente.tipo_cuenta or 'No especificado'}",
                f"<b>Patrimonio Declarado:</b> {'Sí' if cliente.tiene_patrimonio_declarado else 'No'}",
                f"<b>Monto Patrimonio USD:</b> ${float(cliente.monto_patrimonio_usd or 0):,.2f}" if cliente.tiene_patrimonio_declarado else "",
                f"<b>Monto Patrimonio Bs:</b> Bs {float(cliente.monto_patrimonio_bs or 0):,.2f}" if cliente.tiene_patrimonio_declarado else ""
            ])
        ]
        
        for grupo_titulo, items in grupos:
            grupo_frame = QFrame()
            grupo_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
            grupo_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 6px;
                    border: 1px solid #dee2e6;
                    padding: 15px;
                    margin-bottom: 15px;
                }
            """)
            
            grupo_layout = QVBoxLayout()
            grupo_frame.setLayout(grupo_layout)
            
            # Título del grupo
            grupo_label = QLabel(grupo_titulo)
            grupo_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #495057;
                    margin-bottom: 10px;
                }
            """)
            grupo_layout.addWidget(grupo_label)
            
            # Items del grupo
            for item in items:
                if item:  # Solo agregar si no está vacío
                    item_label = QLabel(item)
                    item_label.setStyleSheet("""
                        QLabel {
                            font-size: 14px;
                            color: #6c757d;
                            margin-left: 10px;
                            margin-bottom: 5px;
                        }
                    """)
                    item_label.setTextFormat(Qt.TextFormat.RichText)
                    grupo_layout.addWidget(item_label)
            
            detalles_layout.addWidget(grupo_frame)
        
        # Notas
        if cliente.notas:
            notas_frame = QFrame()
            notas_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
            notas_frame.setStyleSheet("""
                QFrame {
                    background-color: #fff3cd;
                    border-radius: 6px;
                    border: 1px solid #ffeaa7;
                    padding: 15px;
                }
            """)
            
            notas_layout = QVBoxLayout()
            notas_frame.setLayout(notas_layout)
            
            notas_label = QLabel("📝 Notas")
            notas_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #856404;
                    margin-bottom: 10px;
                }
            """)
            notas_layout.addWidget(notas_label)
            
            notas_content = QLabel(cliente.notas)
            notas_content.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #856404;
                    margin-left: 10px;
                }
            """)
            notas_content.setWordWrap(True)
            notas_layout.addWidget(notas_content)
            
            detalles_layout.addWidget(notas_frame)
        
        # Espaciador
        detalles_layout.addStretch()
        
        scroll_area.setWidget(detalles_container)
        self.detalles_widget.layout().addWidget(scroll_area)
    
    def nuevo_cliente(self):
        dialog = ClienteFormWidget(self)
        dialog.setWindowTitle("➕ Nuevo Cliente")
        dialog.resize(600, 800)
        dialog.exec()
        
        """Crear nuevo cliente"""
        # Cambiar a pestaña de formulario
        self.right_tabs.setCurrentIndex(0)
        
        # Limpiar formulario
        self.form_widget.limpiar_formulario()
        
        # Cambiar a modo nuevo
        self.form_widget.mode = "nuevo"
        
        # Enfocar campo de identificación
        self.form_widget.identificacion_edit.setFocus()
        
        self.status_bar.showMessage("Modo: Nuevo cliente. Complete el formulario.")
    
    def editar_cliente(self):
        """Editar cliente seleccionado"""
        if not self.current_cliente_id:
            return
        
        try:
            self.obtener_sesion_db()
            
            # Obtener cliente
            cliente = self.cliente_repo.get(self.current_cliente_id)
            if not cliente:
                QMessageBox.warning(self, "Error", "Cliente no encontrado")
                return
            
            # Cambiar a pestaña de formulario
            self.right_tabs.setCurrentIndex(0)
            
            # Cambiar a modo editar
            self.form_widget.mode = "editar"
            
            # Cargar datos en formulario
            self.form_widget.cargar_cliente(cliente)
            
            self.status_bar.showMessage(f"Editando cliente: {cliente.nombre_completo}")
            
        except Exception as e:
            logger.error(f"Error editando cliente: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo cargar el cliente: {str(e)}")
    
    def eliminar_cliente(self):
        """Eliminar cliente seleccionado"""
        if not self.current_cliente_id:
            return
        
        # Confirmación
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro de eliminar al cliente con ID: {self.current_cliente_id}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            self.obtener_sesion_db()
            
            # Eliminar cliente
            if self.cliente_repo.delete(self.current_cliente_id):
                QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
                
                # Recargar lista
                self.load_clientes()
                
                # Limpiar selección
                self.current_cliente_id = None
                self.editar_action.setEnabled(False)
                self.eliminar_action.setEnabled(False)
                
                # Volver a formulario nuevo
                self.nuevo_cliente()
                
                self.status_bar.showMessage("Cliente eliminado", 3000)
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el cliente")
                
        except Exception as e:
            logger.error(f"Error eliminando cliente: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el cliente: {str(e)}")
    
    def guardar_cliente_desde_form(self, datos: Dict[str, Any]):
        """Guardar cliente desde datos del formulario"""
        try:
            self.obtener_sesion_db()
            
            if self.form_widget.mode == "nuevo":
                # Verificar si el cliente ya existe
                cliente_existente = self.cliente_repo.get(datos['id'])
                if cliente_existente:
                    QMessageBox.warning(self, "Error", "Ya existe un cliente con esta identificación")
                    return
                
                # Crear nuevo cliente
                cliente = ClienteDB(**datos)
                resultado = self.cliente_repo.create(cliente)
                
                if resultado:
                    # Crear cuenta automáticamente para el cliente
                    self.crear_cuenta_automatica(cliente.id)
                    
                    QMessageBox.information(self, "Éxito", "Cliente creado correctamente")
                    self.status_bar.showMessage("Cliente creado", 3000)
                else:
                    QMessageBox.warning(self, "Error", "No se pudo crear el cliente")
                    return
                    
            else:  # Modo editar
                cliente = self.cliente_repo.get(datos['id'])
                if not cliente:
                    QMessageBox.warning(self, "Error", "Cliente no encontrado")
                    return
                
                # Actualizar campos
                for key, value in datos.items():
                    if key != 'id' and hasattr(cliente, key):
                        setattr(cliente, key, value)
                
                # Guardar cambios
                self.db_session.commit()
                QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
                self.status_bar.showMessage("Cliente actualizado", 3000)
            
            # Recargar lista de clientes
            self.load_clientes()
            
            # Si estamos editando, volver a detalles
            if self.form_widget.mode == "editar" and self.current_cliente_id:
                self.cargar_detalles_cliente(self.current_cliente_id)
                self.right_tabs.setCurrentIndex(1)
            
        except Exception as e:
            logger.error(f"Error guardando cliente: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo guardar el cliente: {str(e)}")
    
    def crear_cuenta_automatica(self, cliente_id: str):
        """Crear cuenta automática para nuevo cliente"""
        try:
            cuenta_repo = RepositoryFactory.get_repository(self.db_session, 'cuenta')
            
            # Generar número de cuenta único
            import random
            numero_cuenta = f"CTA-{cliente_id}-{random.randint(1000, 9999)}"
            
            cuenta = CuentaDB(
                cliente_id=cliente_id,
                numero_cuenta=numero_cuenta,
                tipo_cuenta="Individual",
                moneda_base="USD",
                saldo_disponible_usd=0.00,
                saldo_disponible_bs=0.00,
                estado="Activa"
            )
            
            cuenta_repo.create(cuenta)
            logger.info(f"Cuenta automática creada: {numero_cuenta} para cliente {cliente_id}")
            
        except Exception as e:
            logger.error(f"Error creando cuenta automática: {e}")
            # No mostrar error al usuario, es opcional
    
    def exportar_clientes(self):
        """Exportar clientes a Excel"""
        try:
            from openpyxl import Workbook
            from datetime import datetime
            import os
            
            self.obtener_sesion_db()
            
            # Obtener todos los clientes
            clientes = self.cliente_repo.get_all()
            
            if not clientes:
                QMessageBox.information(self, "Exportar", "No hay clientes para exportar")
                return
            
            # Crear archivo Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "Clientes"
            
            # Encabezados
            headers = [
                "ID", "Nombre Completo", "Tipo Persona", "Tipo Documento",
                "Teléfono", "Email", "Dirección", "Ciudad", "Estado",
                "Perfil Riesgo", "Límite USD", "Límite Bs",
                "Ingresos USD", "Ingresos Bs", "Banco", "Cuenta",
                "Patrimonio Declarado", "Patrimonio USD", "Patrimonio Bs",
                "Fecha Registro", "Activo"
            ]
            ws.append(headers)
            
            # Datos
            for cliente in clientes:
                row = [
                    cliente.id,
                    cliente.nombre_completo,
                    cliente.tipo_persona.value,
                    cliente.tipo_documento.value,
                    cliente.telefono_principal,
                    cliente.email,
                    cliente.direccion,
                    cliente.ciudad,
                    cliente.estado,
                    cliente.perfil_riesgo.value,
                    float(cliente.limite_inversion_usd or 0),
                    float(cliente.limite_inversion_bs or 0),
                    float(cliente.ingresos_mensuales_usd or 0),
                    float(cliente.ingresos_mensuales_bs or 0),
                    cliente.banco_principal or "",
                    cliente.numero_cuenta or "",
                    "Sí" if cliente.tiene_patrimonio_declarado else "No",
                    float(cliente.monto_patrimonio_usd or 0),
                    float(cliente.monto_patrimonio_bs or 0),
                    cliente.fecha_registro.strftime("%d/%m/%Y %H:%M"),
                    "Sí" if cliente.activo else "No"
                ]
                ws.append(row)
            
            # Guardar archivo
            export_dir = "data/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{export_dir}/clientes_export_{timestamp}.xlsx"
            wb.save(filename)
            
            QMessageBox.information(
                self, "Exportación exitosa",
                f"Clientes exportados correctamente:\n{filename}"
            )
            
            self.status_bar.showMessage(f"Exportado a: {filename}", 5000)
            logger.info(f"Clientes exportados a: {filename}")
            
        except Exception as e:
            logger.error(f"Error exportando clientes: {e}")
            QMessageBox.critical(self, "Error", f"No se pudieron exportar los clientes: {str(e)}")
    
    def on_form_cleared(self):
        """Manejar limpieza del formulario"""
        self.status_bar.showMessage("Formulario listo para nuevo cliente")
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.db_session:
            self.db_session.close()