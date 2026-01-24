# src/bvc_gestor/ui/dialogs/nueva_compra_dialog.py
"""
Dialog wizard de 3 pasos para crear orden de compra
Paso 1: Selección de inversor y cuenta
Paso 2: Detalles de la operación
Paso 3: Confirmación y validación de saldo
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QFrame,
    QStackedWidget, QGridLayout, QDateEdit, QMessageBox,
QCompleter, QWidget, QRadioButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QDoubleValidator, QIntValidator
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from ..dialogs.solicitud_deposito_dialog import SolicitudDepositoDialog


logger = logging.getLogger(__name__)


class NuevaCompraDialog(QDialog):
    """
    Dialog wizard para crear orden de compra
    
    Flujo:
    1. Seleccionar inversor, cuenta bursátil y cuenta bancaria
    2. Ingresar detalles: ticker, cantidad, precio, tipo
    3. Confirmar y verificar saldo
    """
    
    # Señal emitida cuando se crea la orden exitosamente
    orden_creada = pyqtSignal(int)  # orden_id
    
    def __init__(self, service=None, controller=None, inversor_id=None, parent=None):
        super().__init__(parent)
        self.service = service
        self.controller = controller
        
        # Estado inicial
        self.inversor_id = inversor_id
        self.paso_actual = 0
        
        # Datos del formulario
        self.datos_orden = {
            'cliente_id': None,
            'cuenta_bursatil_id': None,
            'cuenta_bancaria_id': None,
            'ticker': None,
            'activo_id': None,
            'cantidad': 0,
            'precio_limite': None,
            'tipo_orden': 'MERCADO',
            'fecha_vencimiento': None,
        }
        
        # Datos calculados
        self.precio_actual = Decimal('0.00')
        self.comisiones = {}
        self.monto_total = Decimal('0.00')
        self.saldo_disponible = Decimal('0.00')
        
        self.setup_ui()
        self.setup_validators()
        
        # Si viene con inversor pre-seleccionado
        if inversor_id:
            self.pre_seleccionar_inversor(inversor_id)
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        self.setWindowTitle("Nueva Orden de Compra")
        self.setMinimumSize(800, 1000)
        self.setModal(True)
    
        # =====================================================
        # 1. CREAR SCROLL AREA
        # =====================================================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # =====================================================
        # 2. CREAR WIDGET CONTENEDOR PRINCIPAL
        # =====================================================
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # =====================================================
        # 3. HEADER (igual que antes)
        # =====================================================
        header = self.create_header()
        main_layout.addWidget(header)
        
        # =====================================================
        # 4. INDICADOR DE PASOS
        # =====================================================
        steps_indicator = self.create_steps_indicator()
        main_layout.addWidget(steps_indicator)
        
        # =====================================================
        # 5. STACK DE PASOS
        # =====================================================
        self.stack = QStackedWidget()
        self.paso1 = self.create_paso1()
        self.paso2 = self.create_paso2()
        self.paso3 = self.create_paso3()
        
        self.stack.addWidget(self.paso1)
        self.stack.addWidget(self.paso2)
        self.stack.addWidget(self.paso3)
        
        main_layout.addWidget(self.stack, 1)
        
        # =====================================================
        # 6. BOTONES DE NAVEGACIÓN
        # =====================================================
        buttons_layout = self.create_navigation_buttons()
        main_layout.addLayout(buttons_layout)
        
        # =====================================================
        # 7. AGREGAR WIDGET AL SCROLL AREA
        # =====================================================
        scroll_area.setWidget(main_widget)
        
        # =====================================================
        # 8. ESTABLECER EL SCROLL AREA COMO LAYOUT PRINCIPAL
        # =====================================================
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes
        dialog_layout.addWidget(scroll_area)
        
        self.setObjectName("scroll_area")

    
    # =====================================================
    # HEADER Y NAVEGACIÓN
    # =====================================================
    
    def create_header(self):
        """Header con título"""
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Nueva Orden de Compra")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        
        self.subtitle = QLabel("Paso 1 de 3: Selección de cuentas")
        self.subtitle.setStyleSheet("font-size: 14px; color: #888888;")
        
        layout.addWidget(title)
        layout.addWidget(self.subtitle)
        
        return frame
    
    def create_steps_indicator(self):
        """Indicador visual de pasos"""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setSpacing(10)
        
        self.step_labels = []
        
        for i, (numero, titulo) in enumerate([
            ("1", "Cuentas"),
            ("2", "Detalles"),
            ("3", "Confirmación")
        ]):
            step_widget = QWidget()
            step_layout = QHBoxLayout(step_widget)
            step_layout.setContentsMargins(0, 0, 0, 0)
            step_layout.setSpacing(8)
            
            # Círculo con número
            circle = QLabel(numero)
            circle.setFixedSize(32, 32)
            circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            circle.setStyleSheet("""
                background-color: #2D2D2D;
                color: #888888;
                border-radius: 16px;
                font-weight: bold;
                font-size: 14px;
            """)
            
            # Texto
            text = QLabel(titulo)
            text.setStyleSheet("color: #888888; font-size: 13px;")
            
            step_layout.addWidget(circle)
            step_layout.addWidget(text)
            step_layout.addStretch()
            
            self.step_labels.append((circle, text))
            layout.addWidget(step_widget)
            
            # Separador (excepto el último)
            if i < 2:
                separator = QLabel("→")
                separator.setStyleSheet("color: #444444; font-size: 16px;")
                layout.addWidget(separator)
        
        layout.addStretch()
        self.actualizar_indicador_pasos()
        
        return frame
    
    def create_navigation_buttons(self):
        """Botones Anterior, Siguiente, Cancelar"""
        layout = QHBoxLayout()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("secondaryButton")
        self.btn_cancelar.setMinimumHeight(45)
        self.btn_cancelar.clicked.connect(self.reject)
        
        layout.addWidget(self.btn_cancelar)
        layout.addStretch()
        
        self.btn_anterior = QPushButton("← Anterior")
        self.btn_anterior.setObjectName("secondaryButton")
        self.btn_anterior.setMinimumHeight(45)
        self.btn_anterior.setEnabled(False)
        self.btn_anterior.clicked.connect(self.ir_paso_anterior)
        
        self.btn_siguiente = QPushButton("Siguiente →")
        self.btn_siguiente.setObjectName("primaryButton")
        self.btn_siguiente.setMinimumHeight(45)
        self.btn_siguiente.clicked.connect(self.ir_paso_siguiente)
        
        layout.addWidget(self.btn_anterior)
        layout.addWidget(self.btn_siguiente)
        
        return layout
    
    # =====================================================
    # PASO 1: SELECCIÓN DE CUENTAS
    # =====================================================
    
    def create_paso1(self):
        """Paso 1: Inversor, cuenta bursátil y cuenta bancaria"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Frame con formulario
        form_frame = QFrame()
        form_frame.setObjectName("Card")
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        
        row = 0
        
        # Inversor
        label_inversor = QLabel("Inversor:")
        label_inversor.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.combo_inversor = QComboBox()
        self.combo_inversor.setObjectName("form_combo")
        self.combo_inversor.setMinimumHeight(45)
        self.combo_inversor.currentIndexChanged.connect(self.on_inversor_changed)
        
        form_layout.addWidget(label_inversor, row, 0)
        form_layout.addWidget(self.combo_inversor, row, 1)
        row += 1
        
        # Cuenta Bursátil
        label_cuenta_bursatil = QLabel("Cuenta Bursátil:")
        label_cuenta_bursatil.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        self.combo_cuenta_bursatil = QComboBox()
        self.combo_cuenta_bursatil.setObjectName("form_combo")
        self.combo_cuenta_bursatil.setMinimumHeight(45)
        self.combo_cuenta_bursatil.currentIndexChanged.connect(self.on_cuenta_bursatil_changed)
        
        form_layout.addWidget(label_cuenta_bursatil, row, 0)
        form_layout.addWidget(self.combo_cuenta_bursatil, row, 1)
        row += 1
        
        # Cuenta Bancaria
        label_cuenta_bancaria = QLabel("Cuenta Bancaria:")
        label_cuenta_bancaria.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        label_cuenta_bancaria_help = QLabel("(Para depósitos/retiros)")
        label_cuenta_bancaria_help.setStyleSheet("color: #888888; font-size: 12px;")
        
        self.combo_cuenta_bancaria = QComboBox()
        self.combo_cuenta_bancaria.setObjectName("form_combo")
        self.combo_cuenta_bancaria.setMinimumHeight(45)
        
        cuenta_bancaria_layout = QVBoxLayout()
        cuenta_bancaria_layout.addWidget(label_cuenta_bancaria)
        cuenta_bancaria_layout.addWidget(label_cuenta_bancaria_help)
        
        form_layout.addLayout(cuenta_bancaria_layout, row, 0)
        form_layout.addWidget(self.combo_cuenta_bancaria, row, 1)
        row += 1
        
        # Saldo disponible (info)
        self.label_saldo = QLabel("Saldo disponible: Bs. 0.00")
        self.label_saldo.setStyleSheet("""
            background-color: #2D2D2D;
            color: #4CAF50;
            padding: 12px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
        """)
        form_layout.addWidget(self.label_saldo, row, 0, 1, 2)
        
        layout.addWidget(form_frame)
        layout.addStretch()
        
        return widget
    
    # =====================================================
    # PASO 2: DETALLES DE LA OPERACIÓN
    # =====================================================
    
    def create_paso2(self):
        """Paso 2: Ticker, cantidad, precio, tipo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Frame con formulario
        form_frame = QFrame()
        form_frame.setObjectName("Card")
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        
        row = 0
        
        # Ticker con autocomplete
        label_ticker = QLabel("Ticker / Activo:")
        label_ticker.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.input_ticker = QLineEdit()
        self.input_ticker.setObjectName("form_input")
        self.input_ticker.setMinimumHeight(45)
        self.input_ticker.setPlaceholderText("Ej: BPV, BOD, CORP...")
        self.input_ticker.textChanged.connect(self.on_ticker_changed)
        
        # Autocomplete (TODO: cargar desde BD)
        self.ticker_completer = QCompleter(["BPV", "BOD", "CORP", "BNC", "VENEZUELA"])
        self.ticker_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.input_ticker.setCompleter(self.ticker_completer)
        
        # Label con info del activo
        self.label_activo_info = QLabel("")
        self.label_activo_info.setStyleSheet("color: #888888; font-size: 12px;")
        
        ticker_layout = QVBoxLayout()
        ticker_layout.addWidget(self.input_ticker)
        ticker_layout.addWidget(self.label_activo_info)
        
        form_layout.addWidget(label_ticker, row, 0)
        form_layout.addLayout(ticker_layout, row, 1)
        row += 1
        
        # Cantidad
        label_cantidad = QLabel("Cantidad de Acciones:")
        label_cantidad.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.input_cantidad = QLineEdit()
        self.input_cantidad.setObjectName("form_input")
        self.input_cantidad.setMinimumHeight(45)
        self.input_cantidad.setPlaceholderText("0")
        self.input_cantidad.textChanged.connect(self.on_cantidad_changed)
        
        form_layout.addWidget(label_cantidad, row, 0)
        form_layout.addWidget(self.input_cantidad, row, 1)
        row += 1
        
        # Tipo de Orden
        label_tipo = QLabel("Tipo de Orden:")
        label_tipo.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        tipo_container = QWidget()
        tipo_layout = QHBoxLayout(tipo_container)
        tipo_layout.setContentsMargins(0, 0, 0, 0)
        
        self.radio_mercado = QRadioButton("A Mercado")
        self.radio_mercado.setChecked(True)
        self.radio_mercado.toggled.connect(self.on_tipo_orden_changed)
        
        self.radio_limite = QRadioButton("Límite")
        self.radio_limite.toggled.connect(self.on_tipo_orden_changed)
        
        tipo_layout.addWidget(self.radio_mercado)
        tipo_layout.addWidget(self.radio_limite)
        tipo_layout.addStretch()
        
        form_layout.addWidget(label_tipo, row, 0)
        form_layout.addWidget(tipo_container, row, 1)
        row += 1
        
        # Precio Límite (solo si es orden límite)
        label_precio = QLabel("Precio Límite:")
        label_precio.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.input_precio_limite = QLineEdit()
        self.input_precio_limite.setObjectName("form_input")
        self.input_precio_limite.setMinimumHeight(45)
        self.input_precio_limite.setPlaceholderText("0.00")
        self.input_precio_limite.setEnabled(False)
        self.input_precio_limite.textChanged.connect(self.on_precio_changed)
        
        form_layout.addWidget(label_precio, row, 0)
        form_layout.addWidget(self.input_precio_limite, row, 1)
        row += 1
        
        # Vigencia
        label_vigencia = QLabel("Vigencia:")
        label_vigencia.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.date_vigencia = QDateEdit()
        self.date_vigencia.setObjectName("form_date")
        self.date_vigencia.setMinimumHeight(45)
        self.date_vigencia.setCalendarPopup(True)
        self.date_vigencia.setDate(QDate.currentDate().addDays(30))
        self.date_vigencia.setDisplayFormat("dd/MM/yyyy")
        
        form_layout.addWidget(label_vigencia, row, 0)
        form_layout.addWidget(self.date_vigencia, row, 1)
        
        layout.addWidget(form_frame)
        layout.addStretch()
        
        return widget
    
    # =====================================================
    # PASO 3: CONFIRMACIÓN Y SALDO
    # =====================================================
    
    def create_paso3(self):
        """Paso 3: Resumen, cálculo de comisiones y validación de saldo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Resumen de la operación
        resumen_frame = QFrame()
        resumen_frame.setObjectName("Card")
        resumen_layout = QVBoxLayout(resumen_frame)
        resumen_layout.setContentsMargins(30, 20, 30, 20)
        
        title_resumen = QLabel("Resumen de la Operación")
        title_resumen.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        resumen_layout.addWidget(title_resumen)
        
        self.label_resumen = QLabel()
        self.label_resumen.setWordWrap(True)
        self.label_resumen.setStyleSheet("color: #E0E0E0; line-height: 1.6;")
        resumen_layout.addWidget(self.label_resumen)
        
        layout.addWidget(resumen_frame)
        
        # Calculadora de comisiones
        calc_frame = self.create_calculadora_comisiones()
        layout.addWidget(calc_frame)
        
        # Validación de saldo
        saldo_frame = self.create_validacion_saldo()
        layout.addWidget(saldo_frame)
        
        layout.addStretch()
        
        return widget
    
    def create_calculadora_comisiones(self):
        """Widget con cálculo detallado de comisiones"""
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)
        
        title = QLabel("Cálculo de Comisiones")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)
        
        # Grid con cálculos
        grid = QGridLayout()
        grid.setSpacing(8)
        
        self.calc_labels = {}
        
        items = [
            ("subtotal", "Subtotal (Cantidad × Precio):"),
            ("corretaje", "Comisión Corretaje (0.5%):"),
            ("bvc", "Comisión BVC (0.05%):"),
            ("cvv", "Comisión CVV (0.05%):"),
            ("iva", "IVA (16%):"),
        ]
        
        row = 0
        for key, label_text in items:
            label = QLabel(label_text)
            label.setStyleSheet("color: #B0B0B0;")
            
            value = QLabel("Bs. 0.00")
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            value.setStyleSheet("color: #E0E0E0; font-weight: 500;")
            
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
            
            self.calc_labels[key] = value
            row += 1
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #444444; max-height: 1px;")
        grid.addWidget(separator, row, 0, 1, 2)
        row += 1
        
        # Total
        total_label = QLabel("TOTAL A PAGAR:")
        total_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 16px;")
        
        self.calc_total = QLabel("Bs. 0.00")
        self.calc_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.calc_total.setStyleSheet("color: #FF6B00; font-weight: bold; font-size: 18px;")
        
        grid.addWidget(total_label, row, 0)
        grid.addWidget(self.calc_total, row, 1)
        
        layout.addLayout(grid)
        
        return frame
    
    def create_validacion_saldo(self):
        """Widget de validación de saldo"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Label de estado
        self.label_estado_saldo = QLabel()
        self.label_estado_saldo.setWordWrap(True)
        self.label_estado_saldo.setMinimumHeight(60)
        self.label_estado_saldo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_estado_saldo)
        
        # Botón solicitar depósito (oculto por defecto)
        self.btn_solicitar_deposito = QPushButton("Solicitar Depósito")
        self.btn_solicitar_deposito.setObjectName("secondaryButton")
        self.btn_solicitar_deposito.setMinimumHeight(45)
        self.btn_solicitar_deposito.hide()
        self.btn_solicitar_deposito.clicked.connect(self.abrir_solicitud_deposito)
        
        layout.addWidget(self.btn_solicitar_deposito)
        
        return frame
    
    # =====================================================
    # VALIDATORS
    # =====================================================
    
    def setup_validators(self):
        """Configurar validadores para inputs numéricos"""
        # Validador para cantidad (solo enteros)
        cantidad_validator = QIntValidator(1, 999999999)
        self.input_cantidad.setValidator(cantidad_validator)
        
        # Validador para precio (decimales)
        precio_validator = QDoubleValidator(0.01, 999999999.99, 2)
        precio_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.input_precio_limite.setValidator(precio_validator)
    
    # =====================================================
    # NAVEGACIÓN ENTRE PASOS
    # =====================================================
    
    def ir_paso_siguiente(self):
        """Avanza al siguiente paso"""
        if self.paso_actual == 0:
            if not self.validar_paso1():
                return
            self.paso_actual = 1
            self.stack.setCurrentIndex(1)
            self.subtitle.setText("Paso 2 de 3: Detalles de la operación")
            self.btn_anterior.setEnabled(True)
            
        elif self.paso_actual == 1:
            if not self.validar_paso2():
                return
            self.paso_actual = 2
            self.stack.setCurrentIndex(2)
            self.subtitle.setText("Paso 3 de 3: Confirmación")
            self.btn_siguiente.setText("Crear Orden")
            self.actualizar_resumen()
            self.calcular_comisiones()
            self.validar_saldo()
            
        elif self.paso_actual == 2:
            # Crear la orden
            self.crear_orden()
        
        self.actualizar_indicador_pasos()
    
    def ir_paso_anterior(self):
        """Retrocede al paso anterior"""
        if self.paso_actual == 1:
            self.paso_actual = 0
            self.stack.setCurrentIndex(0)
            self.subtitle.setText("Paso 1 de 3: Selección de cuentas")
            self.btn_anterior.setEnabled(False)
            
        elif self.paso_actual == 2:
            self.paso_actual = 1
            self.stack.setCurrentIndex(1)
            self.subtitle.setText("Paso 2 de 3: Detalles de la operación")
            self.btn_siguiente.setText("Siguiente →")
        
        self.actualizar_indicador_pasos()
    
    def actualizar_indicador_pasos(self):
        """Actualiza el indicador visual de pasos"""
        for i, (circle, text) in enumerate(self.step_labels):
            if i < self.paso_actual:
                # Paso completado
                circle.setStyleSheet("""
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 16px;
                    font-weight: bold;
                    font-size: 14px;
                """)
                text.setStyleSheet("color: #4CAF50; font-size: 13px;")
            elif i == self.paso_actual:
                # Paso actual
                circle.setStyleSheet("""
                    background-color: #FF6B00;
                    color: white;
                    border-radius: 16px;
                    font-weight: bold;
                    font-size: 14px;
                """)
                text.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: bold;")
            else:
                # Paso pendiente
                circle.setStyleSheet("""
                    background-color: #2D2D2D;
                    color: #888888;
                    border-radius: 16px;
                    font-weight: bold;
                    font-size: 14px;
                """)
                text.setStyleSheet("color: #888888; font-size: 13px;")
    
    # =====================================================
    # VALIDACIONES
    # =====================================================
    
    def validar_paso1(self) -> bool:
        """Valida que se hayan seleccionado las cuentas"""
        if not self.combo_inversor.currentData():
            QMessageBox.warning(self, "Campo requerido", "Debe seleccionar un inversor")
            return False
        
        if not self.combo_cuenta_bursatil.currentData():
            QMessageBox.warning(self, "Campo requerido", "Debe seleccionar una cuenta bursátil")
            return False
        
        if not self.combo_cuenta_bancaria.currentData():
            QMessageBox.warning(self, "Campo requerido", "Debe seleccionar una cuenta bancaria")
            return False
        
        # Guardar datos
        self.datos_orden['cliente_id'] = self.combo_inversor.currentData()
        self.datos_orden['cuenta_bursatil_id'] = self.combo_cuenta_bursatil.currentData()
        self.datos_orden['cuenta_bancaria_id'] = self.combo_cuenta_bancaria.currentData()
        
        return True
    
    def validar_paso2(self) -> bool:
        """Valida los detalles de la operación"""
        if not self.input_ticker.text().strip():
            QMessageBox.warning(self, "Campo requerido", "Debe ingresar un ticker")
            return False
        
        if not self.input_cantidad.text() or int(self.input_cantidad.text() or 0) <= 0:
            QMessageBox.warning(self, "Campo inválido", "Debe ingresar una cantidad mayor a cero")
            return False
        
        if self.radio_limite.isChecked():
            if not self.input_precio_limite.text() or float(self.input_precio_limite.text() or 0) <= 0:
                QMessageBox.warning(self, "Campo inválido", "Debe ingresar un precio límite")
                return False
        
        # Guardar datos
        self.datos_orden['ticker'] = self.input_ticker.text().strip().upper()
        self.datos_orden['cantidad'] = int(self.input_cantidad.text())
        self.datos_orden['tipo_orden'] = 'LIMITE' if self.radio_limite.isChecked() else 'MERCADO'
        
        if self.radio_limite.isChecked():
            self.datos_orden['precio_limite'] = Decimal(self.input_precio_limite.text())
        else:
            self.datos_orden['precio_limite'] = None
        
        self.datos_orden['fecha_vencimiento'] = self.date_vigencia.date().toPyDate()
        
        return True
    
    # =====================================================
    # EVENTOS
    # =====================================================
    
    def on_inversor_changed(self, index):
        """Cuando cambia el inversor"""
        inversor_id = self.combo_inversor.currentData()
        if inversor_id:
            self.cargar_cuentas_bursatiles(inversor_id)
            self.cargar_cuentas_bancarias(inversor_id)
    
    def on_cuenta_bursatil_changed(self, index):
        """Cuando cambia la cuenta bursátil"""
        cuenta_id = self.combo_cuenta_bursatil.currentData()
        if cuenta_id:
            self.cargar_saldo_disponible(cuenta_id)
    
    
    def on_cantidad_changed(self, text):
        """Cuando cambia la cantidad"""
        pass  # Se recalcula en paso 3
    
    def on_tipo_orden_changed(self):
        """Cuando cambia el tipo de orden"""
        es_limite = self.radio_limite.isChecked()
        self.input_precio_limite.setEnabled(es_limite)
    
    def on_precio_changed(self, text):
        """Cuando cambia el precio"""
        pass  # Se recalcula en paso 3
    
    # =====================================================
    # CARGA DE DATOS
    # =====================================================
    
    def pre_seleccionar_inversor(self, inversor_id: int):
        """Pre-selecciona un inversor"""
        # TODO: Implementar con datos reales
        pass
    
    def cargar_inversores(self):
        """Carga lista de inversores usando formatter"""
        try:
            if self.controller:
                # Usar el método formateado del controller
                inversores = self.controller.obtener_inversores_formateados()
                
                self.combo_inversor.clear()
                self.combo_inversor.addItem("Seleccione...", None)
                
                for inv in inversores:
                    self.combo_inversor.addItem(inv['texto'], inv['id'])
                
                logger.info(f"Cargados {len(inversores)} inversores formateados")
                return
            
            # Fallback si no hay controller
            self.cargar_inversores_prueba()
            
        except Exception as e:
            logger.error(f"Error al cargar inversores: {e}")
            self.cargar_inversores_prueba()

    def cargar_cuentas_bursatiles(self, cliente_id: int):
        """Carga cuentas bursátiles desde el controller"""
        try:
            self.combo_cuenta_bursatil.clear()
            self.combo_cuenta_bursatil.addItem("Seleccione...", None)
            
            if not self.controller:
                logger.warning("No hay controller, usando datos de prueba")
                self.cargar_cuentas_bursatiles_prueba()
                return
            
            cuentas = self.controller.obtener_cuentas_bursatiles_cliente(cliente_id)
            
            if not cuentas:
                logger.info(f"Cliente {cliente_id} no tiene cuentas bursátiles")
                QMessageBox.information(
                    self,
                    "Sin Cuentas",
                    "El cliente seleccionado no tiene cuentas bursátiles activas."
                )
                return
            
            for cuenta in cuentas:
                texto = f"{cuenta['casa_bolsa_nombre']} - {cuenta['numero']}"
                if cuenta.get('default'):
                    texto += " ⭐"
                self.combo_cuenta_bursatil.addItem(texto, cuenta['id'])
            
            logger.info(f"Cargadas {len(cuentas)} cuentas bursátiles para cliente {cliente_id}")
            
        except Exception as e:
            logger.error(f"Error al cargar cuentas bursátiles: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudieron cargar las cuentas bursátiles:\n{str(e)}"
            )
    
    def cargar_cuentas_bancarias(self, cliente_id: int):
        """Carga cuentas bancarias usando formatter"""
        try:
            if self.controller:
                cuentas = self.controller.obtener_cuentas_bancarias_formateadas(cliente_id)
                
                self.combo_cuenta_bancaria.clear()
                self.combo_cuenta_bancaria.addItem("Seleccione...", None)
                
                for cuenta in cuentas:
                    self.combo_cuenta_bancaria.addItem(cuenta['texto'], cuenta['id'])
                
                logger.info(f"Cargadas {len(cuentas)} cuentas bancarias formateadas")
                return
            
            self.cargar_cuentas_bancarias_prueba()
            
        except Exception as e:
            logger.error(f"Error al cargar cuentas bancarias: {e}")
            self.cargar_cuentas_bancarias_prueba()
    
    def cargar_saldo_disponible(self, cuenta_id: int):
        """Carga saldo disponible desde la base de datos"""
        try:
            if not self.controller:
                logger.warning("No hay controller, usando datos de prueba")
                self.saldo_disponible = Decimal('25000.00')
                self.label_saldo.setText(f"Saldo disponible: Bs. {self.saldo_disponible:,.2f}")
                return
            
            # Necesitas agregar un método en el controller para obtener saldo
            # Por ahora uso una función temporal
            saldo = self.controller.obtener_saldo_cuenta(cuenta_id)
            self.saldo_disponible = saldo
            
            # Formatear con separadores de miles
            formatted_saldo = f"Bs. {saldo:,.2f}"
            self.label_saldo.setText(f"Saldo disponible: {formatted_saldo}")
            
            # Si estamos en paso 3, validar saldo de nuevo
            if self.paso_actual == 2:
                self.validar_saldo()
                
        except Exception as e:
            logger.error(f"Error al cargar saldo: {e}")
            self.saldo_disponible = Decimal('0.00')
            self.label_saldo.setText("Saldo disponible: No disponible")
    
    
    def cargar_tickers_autocomplete(self):
        """Carga tickers para autocompletar desde la base de datos"""
        try:
            if not self.controller:
                logger.warning("No hay controller, usando datos de prueba")
                self.ticker_completer.setModel(['BPV', 'BOD', 'CORP', 'BNC', 'VENEZUELA'])
                return
            
            # Agrega este método al controller si no existe
            tickers = self.controller.obtener_tickers_disponibles()
            self.ticker_completer.setModel(tickers)
            
        except Exception as e:
            logger.error(f"Error al cargar tickers: {e}")
    
    
    def on_ticker_changed(self, text):
        """Cuando cambia el ticker - ahora busca precio real"""
        if len(text) >= 2:
            try:
                if self.controller:
                    # Buscar precio del activo
                    precio = self.controller.obtener_precio_activo(text.upper())
                    if precio:
                        self.precio_actual = precio
                        self.label_activo_info.setText(f"Precio actual: Bs. {precio:,.2f}")
                    else:
                        self.label_activo_info.setText(f"Ticker no encontrado")
                        self.precio_actual = Decimal('0.00')
            except Exception as e:
                logger.error(f"Error al buscar precio: {e}")
                self.label_activo_info.setText("Error al buscar precio")
                self.precio_actual = Decimal('0.00')
    
    
    # Métodos de prueba (para compatibilidad)
    def cargar_inversores_prueba(self):
        self.combo_inversor.clear()
        self.combo_inversor.addItem("Seleccione...", None)
        self.combo_inversor.addItem("Juan Pérez (V-12345678)", 1)
        self.combo_inversor.addItem("María González (V-87654321)", 2)
    
    def cargar_cuentas_bursatiles_prueba(self):
        self.combo_cuenta_bursatil.clear()
        self.combo_cuenta_bursatil.addItem("Seleccione...", None)
        self.combo_cuenta_bursatil.addItem("Casa de Bolsa XYZ - CB-001234", 1)
        self.combo_cuenta_bursatil.addItem("Valores ABC - CB-005678", 2)
    
    def cargar_cuentas_bancarias_prueba(self):
        self.combo_cuenta_bancaria.clear()
        self.combo_cuenta_bancaria.addItem("Seleccione...", None)
        self.combo_cuenta_bancaria.addItem("Banco Provincial - 0108-****-1234", 1)
        self.combo_cuenta_bancaria.addItem("Banco Mercantil - 0105-****-5678", 2)
    
    def crear_orden(self):
        """Crea la orden usando el controller"""
        try:
            if not self.controller:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No hay controller disponible para crear la orden."
                )
                return
            
            # Preparar datos para el controller
            datos_orden = {
                'cliente_id': self.datos_orden['cliente_id'],
                'cuenta_bursatil_id': self.datos_orden['cuenta_bursatil_id'],
                'cuenta_bancaria_id': self.datos_orden['cuenta_bancaria_id'],
                'ticker': self.datos_orden['ticker'],
                'cantidad': self.datos_orden['cantidad'],
                'precio_limite': self.datos_orden['precio_limite'],
                'tipo_orden': self.datos_orden['tipo_orden'],
                'monto_total': self.monto_total,
                'comisiones_total': self.comisiones.get('total', Decimal('0'))
            }
            
            # Llamar al controller
            resultado = self.controller.crear_orden_compra(datos_orden)
            
            if resultado['exito']:
                QMessageBox.information(
                    self,
                    "Orden Creada",
                    f"La orden de compra #{resultado['orden_id']} ha sido creada exitosamente.\n\n"
                    f"Ticker: {self.datos_orden['ticker']}\n"
                    f"Cantidad: {self.datos_orden['cantidad']:,}\n"
                    f"Total: Bs. {self.monto_total:,.2f}\n\n"
                    f"{resultado.get('mensaje', '')}"
                )
                
                self.orden_creada.emit(resultado['orden_id'])
                self.accept()
                
            else:
                if resultado.get('requiere_deposito'):
                    # Mostrar opción para solicitar depósito
                    faltante = resultado.get('monto_faltante', Decimal('0'))
                    respuesta = QMessageBox.question(
                        self,
                        "Saldo Insuficiente",
                        f"{resultado['mensaje']}\n\n"
                        f"Monto faltante: Bs. {faltante:,.2f}\n\n"
                        f"¿Desea solicitar un depósito ahora?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if respuesta == QMessageBox.StandardButton.Yes:
                        self.abrir_solicitud_deposito(faltante)
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"No se pudo crear la orden:\n{resultado.get('mensaje', 'Error desconocido')}"
                    )
            
        except Exception as e:
            logger.error(f"Error al crear orden: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"Error al crear la orden:\n{str(e)}"
            )    
    # =====================================================
    # CÁLCULOS
    # =====================================================
    
    def actualizar_resumen(self):
        """Actualiza el resumen de la operación"""
        resumen = f"""
        <b>Inversor:</b> {self.combo_inversor.currentText()}<br>
        <b>Cuenta Bursátil:</b> {self.combo_cuenta_bursatil.currentText()}<br>
        <b>Cuenta Bancaria:</b> {self.combo_cuenta_bancaria.currentText()}<br>
        <br>
        <b>Activo:</b> {self.datos_orden['ticker']}<br>
        <b>Cantidad:</b> {self.datos_orden['cantidad']:,} acciones<br>
        <b>Tipo de Orden:</b> {self.datos_orden['tipo_orden']}<br>
        """
        
        if self.datos_orden['precio_limite']:
            resumen += f"<b>Precio Límite:</b> Bs. {self.datos_orden['precio_limite']:,.2f}<br>"
        
        resumen += f"<b>Vigencia:</b> {self.datos_orden['fecha_vencimiento'].strftime('%d/%m/%Y')}"
        
        self.label_resumen.setText(resumen)
    
    def calcular_comisiones(self):
        """Calcula todas las comisiones"""
        # Precio a usar
        if self.datos_orden['precio_limite']:
            precio = self.datos_orden['precio_limite']
        else:
            precio = self.precio_actual
        
        cantidad = Decimal(str(self.datos_orden['cantidad']))
        
        # Subtotal
        subtotal = cantidad * precio
        
        # Comisiones (TODO: obtener de configuración)
        comision_corretaje = subtotal * Decimal('0.005')  # 0.5%
        comision_bvc = subtotal * Decimal('0.0005')       # 0.05%
        comision_cvv = subtotal * Decimal('0.0005')       # 0.05%
        
        # IVA sobre comisiones
        total_comisiones = comision_corretaje + comision_bvc + comision_cvv
        iva = total_comisiones * Decimal('0.16')  # 16%
        
        # Total
        total = subtotal + total_comisiones + iva
        
        # Guardar
        self.comisiones = {
            'subtotal': subtotal,
            'corretaje': comision_corretaje,
            'bvc': comision_bvc,
            'cvv': comision_cvv,
            'iva': iva,
            'total': total
        }
        
        self.monto_total = total
        
        # Actualizar UI
        self.calc_labels['subtotal'].setText(f"Bs. {subtotal:,.2f}")
        self.calc_labels['corretaje'].setText(f"Bs. {comision_corretaje:,.2f}")
        self.calc_labels['bvc'].setText(f"Bs. {comision_bvc:,.2f}")
        self.calc_labels['cvv'].setText(f"Bs. {comision_cvv:,.2f}")
        self.calc_labels['iva'].setText(f"Bs. {iva:,.2f}")
        self.calc_total.setText(f"Bs. {total:,.2f}")
    
    def validar_saldo(self):
        """Valida si hay saldo suficiente"""
        if self.saldo_disponible >= self.monto_total:
            # Saldo suficiente
            self.label_estado_saldo.setStyleSheet("""
                background-color: rgba(76, 175, 80, 0.2);
                color: #4CAF50;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #4CAF50;
                font-weight: bold;
            """)
            self.label_estado_saldo.setText(
                f"✓ Fondos suficientes\n"
                f"Saldo disponible: Bs. {self.saldo_disponible:,.2f}\n"
                f"Total requerido: Bs. {self.monto_total:,.2f}"
            )
            self.btn_solicitar_deposito.hide()
            self.btn_siguiente.setEnabled(True)
            
        else:
            # Saldo insuficiente
            faltante = self.monto_total - self.saldo_disponible
            
            self.label_estado_saldo.setStyleSheet("""
                background-color: rgba(244, 67, 54, 0.2);
                color: #F44336;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #F44336;
                font-weight: bold;
            """)
            self.label_estado_saldo.setText(
                f"✗ Saldo insuficiente\n"
                f"Disponible: Bs. {self.saldo_disponible:,.2f}\n"
                f"Necesario: Bs. {self.monto_total:,.2f}\n"
                f"Faltante: Bs. {faltante:,.2f}"
            )
            self.btn_solicitar_deposito.show()
            self.btn_siguiente.setEnabled(False)
    
    # =====================================================
    # ACCIONES FINALES
    # =====================================================
    
    def abrir_solicitud_deposito(self):
        """Abre dialog de solicitud de depósito"""
        faltante = self.monto_total - self.saldo_disponible
        
        QMessageBox.information(
            self,
            "Solicitar Depósito",
            f"Se abrirá el formulario de solicitud de depósito.\n\n"
            f"Monto sugerido: Bs. {faltante:,.2f}\n\n"
        )
        
        dialog = SolicitudDepositoDialog(
            parent=self,
            controller=self.controller,
            inversor_id=self.inversor_id,
            cuenta_bancaria_id=cuenta_id,
            monto_sugerido=faltante,
        )
        
        dialog.deposito_solicitado.connect(self.on_deposito_solicitado)
        dialog.exec()
    
    def on_deposito_solicitado(self, datos):
        # Mostrar mensaje de confirmación
        QMessageBox.information(
            self,
            "Depósito Solicitado",
            f"Se ha registrado una solicitud de depósito por Bs. {datos['monto']:,.2f}\n\n"
            "Una vez procesado, el saldo estará disponible para completar la orden."
        )
    
    # =====================================================
    # OVERRIDE
    # =====================================================
    
    def showEvent(self, event):
        """Al mostrar el dialog"""
        super().showEvent(event)
        # Cargar datos iniciales
        self.cargar_inversores()
        
        if self.inversor_id:
            # Pre-seleccionar si viene con inversor
            for i in range(self.combo_inversor.count()):
                if self.combo_inversor.itemData(i) == self.inversor_id:
                    self.combo_inversor.setCurrentIndex(i)
                    break