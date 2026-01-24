"""
Dashboard de Operaciones - CORREGIDO
NO recibe controller en constructor.
Emite señales que el controller captura.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from datetime import datetime
import logging

from ...utils.formatters import DataFormatter

logger = logging.getLogger(__name__)


class OperacionesDashboard(QWidget):
    """
    Dashboard principal del módulo de operaciones.
    
    Signals:
        inversor_seleccionado: Emitido cuando se selecciona inversor (id)
        cuenta_bursatil_seleccionada: Emitido cuando se selecciona cuenta (id)
        cuenta_bancaria_seleccionada: Emitido cuando se selecciona cuenta (id)
        nueva_compra_clicked: Emitido cuando se clickea Nueva Compra
        nueva_venta_clicked: Emitido cuando se clickea Nueva Venta
        ver_portafolio_clicked: Emitido cuando se clickea Ver Portafolio
        ver_todas_operaciones_clicked: Emitido cuando se clickea Ver Todas
        actualizar_precios_clicked: Emitido cuando se clickea Actualizar Precios
    """
    
    # Señales
    inversor_seleccionado = pyqtSignal(int)
    cuenta_bursatil_seleccionada = pyqtSignal(int)
    cuenta_bancaria_seleccionada = pyqtSignal(int)
    nueva_compra_clicked = pyqtSignal()
    nueva_venta_clicked = pyqtSignal()
    ver_portafolio_clicked = pyqtSignal()
    ver_todas_operaciones_clicked = pyqtSignal()
    actualizar_precios_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Datos
        self.inversores = []
        self.cuentas_bursatiles = []
        self.cuentas_bancarias = []
        self.operaciones_recientes = []
        
        self.setup_ui()
        self.aplicar_estilos()
    
    def setup_ui(self):
        """Configura la interfaz del dashboard"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # --- HEADER CON SELECTORES ---
        header_frame = QFrame()
        header_frame.setObjectName("operacionesHeader")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("💼 Operaciones Bursátiles")
        title_label.setObjectName("operacionesTitle")
        header_layout.addWidget(title_label)
        
        # Selectores
        selectores_layout = QHBoxLayout()
        selectores_layout.setSpacing(15)
        
        # Selector de Inversor
        inversor_layout = QVBoxLayout()
        inversor_layout.setSpacing(5)
        
        lbl_inversor = QLabel("Inversor:")
        lbl_inversor.setObjectName("selectorLabel")
        
        self.combo_inversor = QComboBox()
        self.combo_inversor.setObjectName("selectorCombo")
        self.combo_inversor.setPlaceholderText("Seleccione un inversor")
        self.combo_inversor.currentIndexChanged.connect(self._on_inversor_changed)
        
        inversor_layout.addWidget(lbl_inversor)
        inversor_layout.addWidget(self.combo_inversor)
        selectores_layout.addLayout(inversor_layout, 1)
        
        # Selector de Casa de Bolsa
        bolsa_layout = QVBoxLayout()
        bolsa_layout.setSpacing(5)
        
        lbl_bolsa = QLabel("Casa de Bolsa:")
        lbl_bolsa.setObjectName("selectorLabel")
        
        self.combo_casa_bolsa = QComboBox()
        self.combo_casa_bolsa.setObjectName("selectorCombo")
        self.combo_casa_bolsa.setPlaceholderText("Seleccione casa de bolsa")
        self.combo_casa_bolsa.setEnabled(False)
        self.combo_casa_bolsa.currentIndexChanged.connect(self._on_casa_bolsa_changed)
        
        bolsa_layout.addWidget(lbl_bolsa)
        bolsa_layout.addWidget(self.combo_casa_bolsa)
        selectores_layout.addLayout(bolsa_layout, 1)
        
        # Selector de Cuenta Bancaria
        banco_layout = QVBoxLayout()
        banco_layout.setSpacing(5)
        
        lbl_banco = QLabel("Cuenta Bancaria:")
        lbl_banco.setObjectName("selectorLabel")
        
        self.combo_cuenta_bancaria = QComboBox()
        self.combo_cuenta_bancaria.setObjectName("selectorCombo")
        self.combo_cuenta_bancaria.setPlaceholderText("Seleccione cuenta bancaria")
        self.combo_cuenta_bancaria.setEnabled(False)
        self.combo_cuenta_bancaria.currentIndexChanged.connect(self._on_cuenta_bancaria_changed)
        
        banco_layout.addWidget(lbl_banco)
        banco_layout.addWidget(self.combo_cuenta_bancaria)
        selectores_layout.addLayout(banco_layout, 1)
        
        header_layout.addLayout(selectores_layout)
        layout.addWidget(header_frame)
        
        # --- METRIC CARDS ---
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        # Card: Valor Portafolio
        self.card_portafolio = self._crear_metric_card(
            "💼 Valor Portafolio",
            "Bs. 0.00",
            "Ver detalle →",
            "#2196F3"
        )
        self.card_portafolio.findChild(QLabel, "metricCardLink").mousePressEvent = lambda e: self.ver_portafolio_clicked.emit()
        metrics_layout.addWidget(self.card_portafolio)
        
        # Card: Órdenes Pendientes
        self.card_pendientes = self._crear_metric_card(
            "⏳ Órdenes Pendientes",
            "0",
            "",
            "#FF9800"
        )
        metrics_layout.addWidget(self.card_pendientes)
        
        # Card: Ganancia/Pérdida
        self.card_ganancia = self._crear_metric_card(
            "📈 Ganancia/Pérdida",
            "Bs. 0.00",
            "",
            "#4CAF50"
        )
        metrics_layout.addWidget(self.card_ganancia)
        
        # Card: Última Actualización
        self.card_actualizacion = self._crear_metric_card(
            "🔄 Última Actualización",
            "Nunca",
            "Actualizar precios →",
            "#9C27B0"
        )
        self.card_actualizacion.findChild(QLabel, "metricCardLink").mousePressEvent = lambda e: self.actualizar_precios_clicked.emit()
        metrics_layout.addWidget(self.card_actualizacion)
        
        layout.addLayout(metrics_layout)
        
        # --- BOTONES DE ACCIÓN ---
        acciones_layout = QHBoxLayout()
        acciones_layout.setSpacing(10)
        
        self.btn_nueva_compra = QPushButton("📈 Nueva Compra")
        self.btn_nueva_compra.setObjectName("primaryButton")
        self.btn_nueva_compra.clicked.connect(self.nueva_compra_clicked.emit)
        self.btn_nueva_compra.setEnabled(False)
        
        self.btn_nueva_venta = QPushButton("📉 Nueva Venta")
        self.btn_nueva_venta.setObjectName("dangerButton")
        self.btn_nueva_venta.clicked.connect(self.nueva_venta_clicked.emit)
        self.btn_nueva_venta.setEnabled(False)
        
        self.btn_ver_portafolio = QPushButton("💼 Ver Portafolio")
        self.btn_ver_portafolio.setObjectName("secondaryButton")
        self.btn_ver_portafolio.clicked.connect(self.ver_portafolio_clicked.emit)
        self.btn_ver_portafolio.setEnabled(False)
        
        self.btn_actualizar_precios = QPushButton("🔄 Actualizar Precios")
        self.btn_actualizar_precios.setObjectName("infoButton")
        self.btn_actualizar_precios.clicked.connect(self.actualizar_precios_clicked.emit)
        
        acciones_layout.addWidget(self.btn_nueva_compra)
        acciones_layout.addWidget(self.btn_nueva_venta)
        acciones_layout.addWidget(self.btn_ver_portafolio)
        acciones_layout.addStretch()
        acciones_layout.addWidget(self.btn_actualizar_precios)
        
        layout.addLayout(acciones_layout)
        
        # --- TABLA DE OPERACIONES RECIENTES ---
        tabla_header_layout = QHBoxLayout()
        
        tabla_title = QLabel("📋 Operaciones Recientes")
        tabla_title.setObjectName("sectionTitle")
        
        self.btn_ver_todas = QPushButton("Ver todas →")
        self.btn_ver_todas.setObjectName("linkButton")
        self.btn_ver_todas.clicked.connect(self.ver_todas_operaciones_clicked.emit)
        
        tabla_header_layout.addWidget(tabla_title)
        tabla_header_layout.addStretch()
        tabla_header_layout.addWidget(self.btn_ver_todas)
        
        layout.addLayout(tabla_header_layout)
        
        # Tabla
        self.tabla_operaciones = QTableWidget()
        self.tabla_operaciones.setObjectName("tablaOperaciones")
        self.tabla_operaciones.setColumnCount(7)
        self.tabla_operaciones.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Ticker", "Cantidad", "Precio", "Total", "Estado"
        ])
        
        # Configurar tabla
        header = self.tabla_operaciones.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.tabla_operaciones.setMaximumHeight(250)
        self.tabla_operaciones.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_operaciones.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.tabla_operaciones)
    
    def _crear_metric_card(self, titulo: str, valor: str, link: str, color: str) -> QFrame:
        """Crea una tarjeta de métrica"""
        card = QFrame()
        card.setObjectName("metricCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(20, 15, 20, 15)
        
        # Título
        title_label = QLabel(titulo)
        title_label.setObjectName("metricCardTitle")
        card_layout.addWidget(title_label)
        
        # Valor
        value_label = QLabel(valor)
        value_label.setObjectName("metricCardValue")
        value_label.setStyleSheet(f"color: {color};")
        card_layout.addWidget(value_label)
        
        # Link (si existe)
        if link:
            link_label = QLabel(link)
            link_label.setObjectName("metricCardLink")
            link_label.setCursor(Qt.CursorShape.PointingHandCursor)
            card_layout.addWidget(link_label)
        
        return card
    
    # ==================== HANDLERS INTERNOS ====================
    
    def _on_inversor_changed(self, index):
        """Handler interno cuando cambia el inversor"""
        if index < 0:
            return
        
        inversor_id = self.combo_inversor.currentData()
        if inversor_id:
            self.inversor_seleccionado.emit(inversor_id)
    
    def _on_casa_bolsa_changed(self, index):
        """Handler interno cuando cambia la casa de bolsa"""
        if index < 0:
            return
        
        cuenta_id = self.combo_casa_bolsa.currentData()
        if cuenta_id:
            self.cuenta_bursatil_seleccionada.emit(cuenta_id)
    
    def _on_cuenta_bancaria_changed(self, index):
        """Handler interno cuando cambia la cuenta bancaria"""
        if index < 0:
            return
        
        cuenta_id = self.combo_cuenta_bancaria.currentData()
        if cuenta_id:
            self.cuenta_bancaria_seleccionada.emit(cuenta_id)
    
    # ==================== MÉTODOS PÚBLICOS (llamados por controller) ====================
    
    def poblar_inversores(self, inversores_formateados: list):
        """
        Puebla el combo de inversores con datos ya formateados.
        
        Args:
            inversores_formateados: Lista de dicts con 'id', 'texto', 'tooltip'
        """
        logger.info(f"📥 poblar_inversores: {len(inversores_formateados)} inversores")
        
        self.inversores = inversores_formateados
        self.combo_inversor.clear()
        self.combo_inversor.addItem("👤 Seleccione un inversor...", None)
        
        if not inversores_formateados:
            logger.warning("⚠️ No hay inversores para mostrar")
            return
        
        for inv in inversores_formateados:
            # Agregar al combobox
            index = self.combo_inversor.count()
            self.combo_inversor.addItem(inv.get('texto', 'Sin nombre'), inv.get('id'))
            
            # Añadir tooltip si existe
            if 'tooltip' in inv:
                self.combo_inversor.setItemData(index, inv['tooltip'], 
                                               Qt.ItemDataRole.ToolTipRole)
        
        logger.info(f"✅ Combo inversor: {len(inversores_formateados)} opciones")
    
    def poblar_cuentas_bursatiles(self, cuentas_formateadas: list):
        """
        Puebla el combo de casas de bolsa con datos ya formateados.
        
        Args:
            cuentas_formateadas: Lista de dicts con 'id', 'texto', 'tooltip'
        """
        logger.info(f"📥 poblar_cuentas_bursatiles: {len(cuentas_formateadas)} cuentas")
        
        self.cuentas_bursatiles = cuentas_formateadas
        self.combo_casa_bolsa.clear()
        self.combo_casa_bolsa.addItem("📈 Seleccione cuenta bursátil...", None)
        
        if not cuentas_formateadas:
            logger.warning("⚠️ No hay cuentas bursátiles")
            self.combo_casa_bolsa.setEnabled(False)
            return
        
        for cuenta in cuentas_formateadas:
            # Agregar al combobox
            index = self.combo_casa_bolsa.count()
            self.combo_casa_bolsa.addItem(cuenta.get('texto', 'Sin número'), 
                                         cuenta.get('id'))
            
            # Añadir tooltip si existe
            if 'tooltip' in cuenta:
                self.combo_casa_bolsa.setItemData(index, cuenta['tooltip'], 
                                                 Qt.ItemDataRole.ToolTipRole)
        
        self.combo_casa_bolsa.setEnabled(True)
        logger.info(f"✅ Combo casas de bolsa: {len(cuentas_formateadas)} opciones")
    
    def poblar_cuentas_bancarias(self, cuentas_formateadas: list):
        """
        Puebla el combo de cuentas bancarias con datos ya formateados.
        
        Args:
            cuentas_formateadas: Lista de dicts con 'id', 'texto', 'tooltip'
        """
        logger.info(f"📥 poblar_cuentas_bancarias: {len(cuentas_formateadas)} cuentas")
        
        self.cuentas_bancarias = cuentas_formateadas
        self.combo_cuenta_bancaria.clear()
        self.combo_cuenta_bancaria.addItem("🏦 Seleccione cuenta bancaria...", None)
        
        if not cuentas_formateadas:
            logger.warning("⚠️ No hay cuentas bancarias")
            self.combo_cuenta_bancaria.setEnabled(False)
            return
        
        for cuenta in cuentas_formateadas:
            # Agregar al combobox
            index = self.combo_cuenta_bancaria.count()
            self.combo_cuenta_bancaria.addItem(cuenta.get('texto', 'Sin número'), 
                                                cuenta.get('id'))
            
            # Añadir tooltip si existe
            if 'tooltip' in cuenta:
                self.combo_cuenta_bancaria.setItemData(index, cuenta['tooltip'], 
                                                    Qt.ItemDataRole.ToolTipRole)
        
        self.combo_cuenta_bancaria.setEnabled(True)
        logger.info(f"✅ Combo cuentas bancarias: {len(cuentas_formateadas)} opciones")
    
    def actualizar_metrica_portafolio(self, valor: float):
        """Actualiza la métrica de valor del portafolio"""
        value_label = self.card_portafolio.findChild(QLabel, "metricCardValue")
        value_label.setText(f"Bs. {valor:,.2f}")
    
    def actualizar_metrica_pendientes(self, cantidad: int):
        """Actualiza la métrica de órdenes pendientes"""
        value_label = self.card_pendientes.findChild(QLabel, "metricCardValue")
        value_label.setText(str(cantidad))
    
    def actualizar_metrica_ganancia_perdida(self, valor: float):
        """Actualiza la métrica de ganancia/pérdida"""
        value_label = self.card_ganancia.findChild(QLabel, "metricCardValue")
        
        if valor >= 0:
            value_label.setText(f"+Bs. {valor:,.2f}")
            value_label.setStyleSheet("color: #4CAF50;")
        else:
            value_label.setText(f"Bs. {valor:,.2f}")
            value_label.setStyleSheet("color: #F44336;")
    
    def actualizar_metrica_saldo(self, saldo: float):
        """Actualiza el saldo disponible (opcional, podrías agregar otra card)"""
        # Por ahora no hay card de saldo, pero puedes agregarlo si lo necesitas
        pass
    
    def actualizar_ultima_actualizacion(self):
        """Actualiza la fecha de última actualización de precios"""
        value_label = self.card_actualizacion.findChild(QLabel, "metricCardValue")
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
        value_label.setText(ahora)
    
    def actualizar_tabla_operaciones(self, operaciones: list):
        """Actualiza la tabla de operaciones recientes"""
        self.operaciones_recientes = operaciones
        self.tabla_operaciones.setRowCount(len(operaciones))
        
        for row, op in enumerate(operaciones):
            # Fecha
            fecha = op.get('fecha_orden', '')
            if isinstance(fecha, str):
                try:
                    fecha_obj = datetime.fromisoformat(fecha)
                    fecha_display = fecha_obj.strftime("%d/%m/%Y")
                except:
                    fecha_display = fecha
            else:
                fecha_display = str(fecha)
            
            self.tabla_operaciones.setItem(row, 0, QTableWidgetItem(fecha_display))
            
            # Tipo
            tipo = op.get('tipo', '')
            tipo_item = QTableWidgetItem(tipo)
            if tipo == "Compra":
                tipo_item.setForeground(QColor("#4CAF50"))
            else:
                tipo_item.setForeground(QColor("#F44336"))
            self.tabla_operaciones.setItem(row, 1, tipo_item)
            
            # Ticker
            self.tabla_operaciones.setItem(row, 2, QTableWidgetItem(op.get('ticker', '-')))
            
            # Cantidad
            cantidad = QTableWidgetItem(f"{op.get('cantidad', 0):,}")
            cantidad.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_operaciones.setItem(row, 3, cantidad)
            
            # Precio
            precio = QTableWidgetItem(f"Bs. {op.get('precio_limite', 0):,.2f}")
            precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_operaciones.setItem(row, 4, precio)
            
            # Total
            total = QTableWidgetItem(f"Bs. {op.get('monto_total_estimado', 0):,.2f}")
            total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_operaciones.setItem(row, 5, total)
            
            # Estado
            estado_widget = self._crear_badge_estado(op.get('estado', 'Desconocido'))
            self.tabla_operaciones.setCellWidget(row, 6, estado_widget)
        
        # Habilitar botones si hay cuentas seleccionadas
        hay_seleccion = (self.combo_inversor.currentIndex() >= 0 and
                        self.combo_casa_bolsa.currentIndex() >= 0 and
                        self.combo_cuenta_bancaria.currentIndex() >= 0)
        
        self.btn_nueva_compra.setEnabled(hay_seleccion)
        self.btn_nueva_venta.setEnabled(hay_seleccion)
        self.btn_ver_portafolio.setEnabled(hay_seleccion)
    
    def _crear_badge_estado(self, estado: str) -> QWidget:
        """Crea un badge de estado"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        badge = QLabel(estado)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Estilos según estado
        if estado == "Ejecutada":
            badge.setObjectName("badgeSuccess")
        elif estado == "Pendiente":
            badge.setObjectName("badgeWarning")
        elif estado == "Cancelada":
            badge.setObjectName("badgeDanger")
        elif estado == "Esperando Fondos":
            badge.setObjectName("badgeInfo")
        else:
            badge.setObjectName("badgeDefault")
        
        layout.addWidget(badge)
        return widget
    
    def aplicar_estilos(self):
        """Aplica estilos CSS"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            
            #operacionesHeader {
                background-color: #2D2D2D;
                border-radius: 12px;
                padding: 20px;
            }
            
            #operacionesTitle {
                font-size: 28px;
                font-weight: bold;
                color: #FF6B00;
            }
            
            #selectorLabel {
                font-size: 12px;
                color: #AAAAAA;
                font-weight: bold;
            }
            
            #selectorCombo {
                background-color: #1E1E1E;
                border: 2px solid #3D3D3D;
                border-radius: 6px;
                padding: 10px;
                color: #FFFFFF;
                font-size: 14px;
                min-height: 40px;
            }
            
            #selectorCombo:focus {
                border-color: #FF6B00;
            }
            
            #selectorCombo::drop-down {
                border: none;
                background-color: #3D3D3D;
                width: 30px;
            }
            
            #metricCard {
                background-color: #2D2D2D;
                border-radius: 12px;
                border: 2px solid #3D3D3D;
            }
            
            #metricCardTitle {
                font-size: 13px;
                color: #AAAAAA;
                font-weight: bold;
            }
            
            #metricCardValue {
                font-size: 24px;
                font-weight: bold;
            }
            
            #metricCardLink {
                font-size: 12px;
                color: #FF6B00;
                text-decoration: underline;
            }
            
            #metricCardLink:hover {
                color: #FF8534;
            }
            
            #primaryButton {
                background-color: #FF6B00;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #primaryButton:hover {
                background-color: #FF8534;
            }
            
            #primaryButton:disabled {
                background-color: #3D3D3D;
                color: #666666;
            }
            
            #dangerButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #dangerButton:hover {
                background-color: #E57373;
            }
            
            #dangerButton:disabled {
                background-color: #3D3D3D;
                color: #666666;
            }
            
            #secondaryButton {
                background-color: transparent;
                color: #FFFFFF;
                border: 2px solid #3D3D3D;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
            }
            
            #secondaryButton:hover {
                border-color: #FF6B00;
                color: #FF6B00;
            }
            
            #secondaryButton:disabled {
                border-color: #2D2D2D;
                color: #666666;
            }
            
            #infoButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #infoButton:hover {
                background-color: #42A5F5;
            }
            
            #sectionTitle {
                font-size: 18px;
                font-weight: bold;
                color: #FF6B00;
            }
            
            #linkButton {
                background-color: transparent;
                color: #FF6B00;
                border: none;
                font-size: 13px;
                text-decoration: underline;
            }
            
            #linkButton:hover {
                color: #FF8534;
            }
            
            #tablaOperaciones {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 8px;
                gridline-color: #3D3D3D;
            }
            
            #tablaOperaciones::item {
                padding: 8px;
            }
            
            #tablaOperaciones QHeaderView::section {
                background-color: #1E1E1E;
                color: #AAAAAA;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #FF6B00;
                font-weight: bold;
            }
            
            #badgeSuccess {
                background-color: #4CAF50;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }
            
            #badgeWarning {
                background-color: #FF9800;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }
            
            #badgeDanger {
                background-color: #F44336;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }
            
            #badgeInfo {
                background-color: #2196F3;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }
            
            #badgeDefault {
                background-color: #757575;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """)