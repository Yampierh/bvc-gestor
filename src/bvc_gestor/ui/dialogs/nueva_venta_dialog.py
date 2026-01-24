# src/bvc_gestor/ui/dialogs/nueva_venta_dialog.py
"""
Dialog para crear orden de venta
Similar a compra pero con validación de posición disponible
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QFrame,
    QGridLayout, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class NuevaVentaDialog(QDialog):
    """
    Dialog para crear orden de venta
    
    Características:
    - Selección de posición del portafolio
    - Validación de cantidad disponible
    - Cálculo de G/P estimada
    - Cálculo de comisiones
    """
    
    orden_creada = pyqtSignal(int)  # orden_id
    
    def __init__(self, inversor_id=None, parent=None):
        super().__init__(parent)
        
        self.inversor_id = inversor_id
        
        # Datos
        self.posiciones_portafolio = []
        self.posicion_seleccionada = None
        self.precio_actual = Decimal('0.00')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz"""
        self.setWindowTitle("Nueva Orden de Venta")
        self.setMinimumSize(900, 700)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Selección de cuenta
        cuenta_frame = self.create_seccion_cuenta()
        layout.addWidget(cuenta_frame)
        
        # Tabla de portafolio
        portafolio_frame = self.create_seccion_portafolio()
        layout.addWidget(portafolio_frame, 1)
        
        # Detalles de venta
        detalles_frame = self.create_seccion_detalles()
        layout.addWidget(detalles_frame)
        
        # Calculadora
        calc_frame = self.create_calculadora()
        layout.addWidget(calc_frame)
        
        # Botones
        buttons_layout = self.create_buttons()
        layout.addLayout(buttons_layout)
        
    def create_header(self):
        """Header con título"""
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Nueva Orden de Venta")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        
        subtitle = QLabel("Seleccione la posición que desea vender")
        subtitle.setStyleSheet("font-size: 14px; color: #888888;")
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        return frame
    
    def create_seccion_cuenta(self):
        """Selección de inversor y cuenta"""
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QGridLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Inversor
        label_inversor = QLabel("Inversor:")
        label_inversor.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.combo_inversor = QComboBox()
        self.combo_inversor.setObjectName("form_combo")
        self.combo_inversor.setMinimumHeight(45)
        self.combo_inversor.currentIndexChanged.connect(self.on_inversor_changed)
        
        layout.addWidget(label_inversor, 0, 0)
        layout.addWidget(self.combo_inversor, 0, 1)
        
        # Cuenta Bursátil
        label_cuenta = QLabel("Cuenta Bursátil:")
        label_cuenta.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.combo_cuenta = QComboBox()
        self.combo_cuenta.setObjectName("form_combo")
        self.combo_cuenta.setMinimumHeight(45)
        self.combo_cuenta.currentIndexChanged.connect(self.on_cuenta_changed)
        
        layout.addWidget(label_cuenta, 0, 2)
        layout.addWidget(self.combo_cuenta, 0, 3)
        
        return frame
    
    def create_seccion_portafolio(self):
        """Tabla con posiciones del portafolio"""
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Posiciones Disponibles")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)
        
        # Tabla
        self.table_portafolio = QTableWidget()
        self.table_portafolio.setColumnCount(7)
        self.table_portafolio.setHorizontalHeaderLabels([
            "Ticker", "Nombre", "Cantidad", "Costo Promedio",
            "Precio Actual", "G/P", "Seleccionar"
        ])
        
        self.table_portafolio.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_portafolio.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_portafolio.verticalHeader().setVisible(False)
        self.table_portafolio.setMinimumHeight(250)
        
        layout.addWidget(self.table_portafolio)
        
        return frame
    
    def create_seccion_detalles(self):
        """Detalles de la venta"""
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QGridLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Ticker seleccionado (readonly)
        label_ticker = QLabel("Ticker:")
        label_ticker.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.label_ticker_sel = QLabel("-")
        self.label_ticker_sel.setStyleSheet("""
            color: #FF6B00;
            font-size: 18px;
            font-weight: bold;
        """)
        
        layout.addWidget(label_ticker, 0, 0)
        layout.addWidget(self.label_ticker_sel, 0, 1)
        
        # Cantidad disponible (readonly)
        label_disponible = QLabel("Cantidad Disponible:")
        label_disponible.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.label_disponible = QLabel("0")
        self.label_disponible.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
        
        layout.addWidget(label_disponible, 0, 2)
        layout.addWidget(self.label_disponible, 0, 3)
        
        # Cantidad a vender
        label_cantidad = QLabel("Cantidad a Vender:")
        label_cantidad.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.input_cantidad = QLineEdit()
        self.input_cantidad.setObjectName("form_input")
        self.input_cantidad.setMinimumHeight(45)
        self.input_cantidad.setPlaceholderText("0")
        self.input_cantidad.textChanged.connect(self.on_cantidad_changed)
        
        cantidad_validator = QIntValidator(1, 999999999)
        self.input_cantidad.setValidator(cantidad_validator)
        
        layout.addWidget(label_cantidad, 1, 0)
        layout.addWidget(self.input_cantidad, 1, 1)
        
        # Precio de venta estimado
        label_precio = QLabel("Precio de Venta:")
        label_precio.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        self.input_precio = QLineEdit()
        self.input_precio.setObjectName("form_input")
        self.input_precio.setMinimumHeight(45)
        self.input_precio.setPlaceholderText("0.00")
        self.input_precio.textChanged.connect(self.on_precio_changed)
        
        precio_validator = QDoubleValidator(0.01, 999999999.99, 2)
        self.input_precio.setValidator(precio_validator)
        
        layout.addWidget(label_precio, 1, 2)
        layout.addWidget(self.input_precio, 1, 3)
        
        return frame
    
    def create_calculadora(self):
        """Calculadora de comisiones y G/P"""
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Resumen de la Venta")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Monto bruto
        grid.addWidget(QLabel("Monto Bruto:"), 0, 0)
        self.label_bruto = QLabel("Bs. 0.00")
        self.label_bruto.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_bruto.setStyleSheet("color: #E0E0E0; font-weight: 500;")
        grid.addWidget(self.label_bruto, 0, 1)
        
        # Comisiones
        grid.addWidget(QLabel("Comisiones:"), 1, 0)
        self.label_comisiones = QLabel("Bs. 0.00")
        self.label_comisiones.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_comisiones.setStyleSheet("color: #E0E0E0; font-weight: 500;")
        grid.addWidget(self.label_comisiones, 1, 1)
        
        # Monto neto
        grid.addWidget(QLabel("Monto Neto a Recibir:"), 2, 0)
        self.label_neto = QLabel("Bs. 0.00")
        self.label_neto.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_neto.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 16px;")
        grid.addWidget(self.label_neto, 2, 1)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #444444;")
        grid.addWidget(separator, 3, 0, 1, 2)
        
        # G/P
        grid.addWidget(QLabel("Ganancia/Pérdida:"), 4, 0)
        self.label_gp = QLabel("Bs. 0.00")
        self.label_gp.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_gp.setStyleSheet("color: #888888; font-weight: bold; font-size: 16px;")
        grid.addWidget(self.label_gp, 4, 1)
        
        # Porcentaje
        grid.addWidget(QLabel("Rendimiento:"), 5, 0)
        self.label_rendimiento = QLabel("0.00%")
        self.label_rendimiento.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_rendimiento.setStyleSheet("color: #888888; font-weight: bold; font-size: 16px;")
        grid.addWidget(self.label_rendimiento, 5, 1)
        
        layout.addLayout(grid)
        
        return frame
    
    def create_buttons(self):
        """Botones de acción"""
        layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("secondaryButton")
        btn_cancelar.setMinimumHeight(45)
        btn_cancelar.clicked.connect(self.reject)
        
        self.btn_crear = QPushButton("Crear Orden de Venta")
        self.btn_crear.setObjectName("primaryButton")
        self.btn_crear.setMinimumHeight(45)
        self.btn_crear.setEnabled(False)
        self.btn_crear.clicked.connect(self.crear_orden)
        
        layout.addWidget(btn_cancelar)
        layout.addStretch()
        layout.addWidget(self.btn_crear)
        
        return layout
    
    # =====================================================
    # EVENTOS
    # =====================================================
    
    def on_inversor_changed(self, index):
        """Cuando cambia el inversor"""
        inversor_id = self.combo_inversor.currentData()
        if inversor_id:
            self.cargar_cuentas(inversor_id)
    
    def on_cuenta_changed(self, index):
        """Cuando cambia la cuenta"""
        cuenta_id = self.combo_cuenta.currentData()
        if cuenta_id:
            self.cargar_portafolio(cuenta_id)
    
    def on_cantidad_changed(self, text):
        """Cuando cambia la cantidad"""
        self.calcular_totales()
    
    def on_precio_changed(self, text):
        """Cuando cambia el precio"""
        self.calcular_totales()
    
    def seleccionar_posicion(self, row):
        """Cuando se selecciona una posición de la tabla"""
        # TODO: Obtener datos de la posición seleccionada
        ticker = self.table_portafolio.item(row, 0).text()
        cantidad_disp = int(self.table_portafolio.item(row, 2).text().replace(',', ''))
        costo_prom = Decimal(self.table_portafolio.item(row, 3).text().replace('Bs. ', '').replace(',', ''))
        precio_actual = Decimal(self.table_portafolio.item(row, 4).text().replace('Bs. ', '').replace(',', ''))
        
        self.posicion_seleccionada = {
            'ticker': ticker,
            'cantidad_disponible': cantidad_disp,
            'costo_promedio': costo_prom,
            'precio_actual': precio_actual
        }
        
        # Actualizar UI
        self.label_ticker_sel.setText(ticker)
        self.label_disponible.setText(f"{cantidad_disp:,}")
        self.input_precio.setText(str(precio_actual))
        self.input_cantidad.setEnabled(True)
        self.input_precio.setEnabled(True)
        
        logger.info(f"Posición seleccionada: {ticker}")
    
    # =====================================================
    # CARGA DE DATOS
    # =====================================================
    
    def cargar_inversores(self):
        """Carga inversores"""
        # TODO: Obtener de BD
        self.combo_inversor.clear()
        self.combo_inversor.addItem("Seleccione...", None)
        self.combo_inversor.addItem("Juan Pérez", 1)
        self.combo_inversor.addItem("María González", 2)
    
    def cargar_cuentas(self, cliente_id: int):
        """Carga cuentas del cliente"""
        # TODO: Obtener de BD
        self.combo_cuenta.clear()
        self.combo_cuenta.addItem("Casa de Bolsa XYZ - CB-001234", 1)
        self.combo_cuenta.addItem("Valores ABC - CB-005678", 2)
    
    def cargar_portafolio(self, cuenta_id: int):
        """Carga portafolio de la cuenta"""
        # TODO: Obtener de BD
        self.table_portafolio.setRowCount(0)
        
        # Datos de prueba
        posiciones = [
            ("BPV", "Banco Provincial", 500, 14.50, 15.50),
            ("BOD", "Banco Occidental", 300, 20.00, 22.75),
            ("CORP", "Corpoelec", 1000, 7.50, 8.25),
        ]
        
        for ticker, nombre, cant, costo, precio in posiciones:
            row = self.table_portafolio.rowCount()
            self.table_portafolio.insertRow(row)
            
            # Ticker
            self.table_portafolio.setItem(row, 0, QTableWidgetItem(ticker))
            
            # Nombre
            self.table_portafolio.setItem(row, 1, QTableWidgetItem(nombre))
            
            # Cantidad
            item_cant = QTableWidgetItem(f"{cant:,}")
            item_cant.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_portafolio.setItem(row, 2, item_cant)
            
            # Costo Promedio
            item_costo = QTableWidgetItem(f"Bs. {costo:,.2f}")
            item_costo.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_portafolio.setItem(row, 3, item_costo)
            
            # Precio Actual
            item_precio = QTableWidgetItem(f"Bs. {precio:,.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_portafolio.setItem(row, 4, item_precio)
            
            # G/P
            gp = (precio - costo) * cant
            item_gp = QTableWidgetItem(f"Bs. {gp:,.2f}")
            item_gp.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            color = "#4CAF50" if gp >= 0 else "#F44336"
            item_gp.setForeground(Qt.GlobalColor.green if gp >= 0 else Qt.GlobalColor.red)
            self.table_portafolio.setItem(row, 5, item_gp)
            
            # Botón Seleccionar
            btn_sel = QPushButton("Seleccionar")
            btn_sel.setObjectName("primaryButton")
            btn_sel.clicked.connect(lambda checked, r=row: self.seleccionar_posicion(r))
            self.table_portafolio.setCellWidget(row, 6, btn_sel)
    
    # =====================================================
    # CÁLCULOS
    # =====================================================
    
    def calcular_totales(self):
        """Calcula totales, comisiones y G/P"""
        if not self.posicion_seleccionada:
            return
        
        try:
            cantidad = int(self.input_cantidad.text() or 0)
            precio = Decimal(self.input_precio.text() or '0')
            
            if cantidad <= 0 or precio <= 0:
                return
            
            # Validar cantidad
            if cantidad > self.posicion_seleccionada['cantidad_disponible']:
                self.input_cantidad.setStyleSheet("border: 2px solid #F44336;")
                self.btn_crear.setEnabled(False)
                return
            else:
                self.input_cantidad.setStyleSheet("")
            
            # Monto bruto
            monto_bruto = Decimal(cantidad) * precio
            
            # Comisiones (igual que compra)
            comision_total = monto_bruto * Decimal('0.006')  # 0.6% total
            iva = comision_total * Decimal('0.16')
            total_comisiones = comision_total + iva
            
            # Monto neto
            monto_neto = monto_bruto - total_comisiones
            
            # G/P
            costo_total = self.posicion_seleccionada['costo_promedio'] * Decimal(cantidad)
            ganancia_perdida = monto_neto - costo_total
            rendimiento = (ganancia_perdida / costo_total) * 100 if costo_total > 0 else Decimal('0')
            
            # Actualizar UI
            self.label_bruto.setText(f"Bs. {monto_bruto:,.2f}")
            self.label_comisiones.setText(f"Bs. {total_comisiones:,.2f}")
            self.label_neto.setText(f"Bs. {monto_neto:,.2f}")
            
            # G/P con color
            signo = "+" if ganancia_perdida >= 0 else ""
            color = "#4CAF50" if ganancia_perdida >= 0 else "#F44336"
            
            self.label_gp.setText(f"Bs. {signo}{ganancia_perdida:,.2f}")
            self.label_gp.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
            
            self.label_rendimiento.setText(f"{signo}{rendimiento:.2f}%")
            self.label_rendimiento.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
            
            self.btn_crear.setEnabled(True)
            
        except (ValueError, Exception) as e:
            logger.error(f"Error en cálculos: {e}")
            self.btn_crear.setEnabled(False)
    
    # =====================================================
    # ACCIONES
    # =====================================================
    
    def crear_orden(self):
        """Crea la orden de venta"""
        try:
            # TODO: Llamar al controller
            orden_id = 456
            
            QMessageBox.information(
                self,
                "Orden Creada",
                f"La orden de venta #{orden_id} ha sido creada exitosamente.\n\n"
                f"Ticker: {self.posicion_seleccionada['ticker']}\n"
                f"Cantidad: {self.input_cantidad.text()}\n"
                f"Precio: Bs. {self.input_precio.text()}"
            )
            
            self.orden_creada.emit(orden_id)
            self.accept()
            
        except Exception as e:
            logger.error(f"Error al crear orden: {e}")
            QMessageBox.critical(self, "Error", f"Error al crear la orden:\n{str(e)}")
    
    def showEvent(self, event):
        """Al mostrar el dialog"""
        super().showEvent(event)
        self.cargar_inversores()
        
        if self.inversor_id:
            for i in range(self.combo_inversor.count()):
                if self.combo_inversor.itemData(i) == self.inversor_id:
                    self.combo_inversor.setCurrentIndex(i)
                    break