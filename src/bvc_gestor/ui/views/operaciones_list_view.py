"""
Vista de Lista de Operaciones - Tabla completa con filtros.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDateEdit, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QColor
from datetime import datetime, timedelta
import logging

from ...utils.constants import TipoOrden, EstadoOrden

logger = logging.getLogger(__name__)


class OperacionesListView(QWidget):
    """
    Vista de lista completa de operaciones con filtros avanzados.
    
    Signals:
        orden_seleccionada: Emitido cuando se selecciona una orden (orden_id)
        nueva_orden_clicked: Emitido cuando se clickea "Nueva Orden"
        volver_clicked: Emitido cuando se clickea "Volver"
    """
    
    orden_seleccionada = pyqtSignal(int)
    nueva_orden_clicked = pyqtSignal()
    volver_clicked = pyqtSignal()
    filtros_aplicados = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ordenes = []
        self.setup_ui()
        self.aplicar_estilos()
    
    def setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header con botones
        header_layout = QHBoxLayout()
        
        self.btn_volver = QPushButton("← Volver")
        self.btn_volver.setObjectName("backButton")
        self.btn_volver.clicked.connect(self.volver_clicked.emit)
        
        title_label = QLabel("📋 Todas las Operaciones")
        title_label.setObjectName("pageTitle")
        
        self.btn_nueva_orden = QPushButton("+ Nueva Orden")
        self.btn_nueva_orden.setObjectName("primaryButton")
        self.btn_nueva_orden.clicked.connect(self.nueva_orden_clicked.emit)
        
        header_layout.addWidget(self.btn_volver)
        header_layout.addWidget(title_label, 1)
        header_layout.addWidget(self.btn_nueva_orden)
        
        layout.addLayout(header_layout)
        
        # --- Panel de Filtros ---
        filtros_frame = QFrame()
        filtros_frame.setObjectName("filtrosFrame")
        filtros_layout = QVBoxLayout(filtros_frame)
        filtros_layout.setSpacing(15)
        
        # Título de filtros
        filtros_title = QLabel("🔍 Filtros de Búsqueda")
        filtros_title.setObjectName("filtrosTitle")
        filtros_layout.addWidget(filtros_title)
        
        # Primera fila de filtros
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        # Búsqueda por ticker
        search_layout = QVBoxLayout()
        search_layout.setSpacing(5)
        
        lbl_search = QLabel("Ticker:")
        lbl_search.setObjectName("filterLabel")
        
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Buscar por ticker...")
        self.input_search.setObjectName("filterInput")
        self.input_search.textChanged.connect(self.on_filtros_changed)
        
        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.input_search)
        row1_layout.addLayout(search_layout, 2)
        
        # Tipo de orden
        tipo_layout = QVBoxLayout()
        tipo_layout.setSpacing(5)
        
        lbl_tipo = QLabel("Tipo:")
        lbl_tipo.setObjectName("filterLabel")
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Todos", None)
        self.combo_tipo.addItem("Compra", TipoOrden.COMPRA)
        self.combo_tipo.addItem("Venta", TipoOrden.VENTA)
        self.combo_tipo.setObjectName("filterInput")
        self.combo_tipo.currentIndexChanged.connect(self.on_filtros_changed)
        
        tipo_layout.addWidget(lbl_tipo)
        tipo_layout.addWidget(self.combo_tipo)
        row1_layout.addLayout(tipo_layout, 1)
        
        # Estado
        estado_layout = QVBoxLayout()
        estado_layout.setSpacing(5)
        
        lbl_estado = QLabel("Estado:")
        lbl_estado.setObjectName("filterLabel")
        
        self.combo_estado = QComboBox()
        self.combo_estado.addItem("Todos", None)
        self.combo_estado.addItem("Pendiente", EstadoOrden.PENDIENTE)
        self.combo_estado.addItem("Ejecutada", EstadoOrden.EJECUTADA)
        self.combo_estado.addItem("Cancelada", EstadoOrden.CANCELADA)
        self.combo_estado.addItem("Esperando Fondos", EstadoOrden.ESPERANDO_FONDOS)
        self.combo_estado.setObjectName("filterInput")
        self.combo_estado.currentIndexChanged.connect(self.on_filtros_changed)
        
        estado_layout.addWidget(lbl_estado)
        estado_layout.addWidget(self.combo_estado)
        row1_layout.addLayout(estado_layout, 1)
        
        filtros_layout.addLayout(row1_layout)
        
        # Segunda fila: Rango de fechas
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        # Fecha desde
        desde_layout = QVBoxLayout()
        desde_layout.setSpacing(5)
        
        lbl_desde = QLabel("Desde:")
        lbl_desde.setObjectName("filterLabel")
        
        self.date_desde = QDateEdit()
        self.date_desde.setCalendarPopup(True)
        self.date_desde.setDisplayFormat("dd/MM/yyyy")
        self.date_desde.setDate(QDate.currentDate().addMonths(-1))
        self.date_desde.setObjectName("filterInput")
        self.date_desde.dateChanged.connect(self.on_filtros_changed)
        
        desde_layout.addWidget(lbl_desde)
        desde_layout.addWidget(self.date_desde)
        row2_layout.addLayout(desde_layout)
        
        # Fecha hasta
        hasta_layout = QVBoxLayout()
        hasta_layout.setSpacing(5)
        
        lbl_hasta = QLabel("Hasta:")
        lbl_hasta.setObjectName("filterLabel")
        
        self.date_hasta = QDateEdit()
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.setDisplayFormat("dd/MM/yyyy")
        self.date_hasta.setDate(QDate.currentDate())
        self.date_hasta.setObjectName("filterInput")
        self.date_hasta.dateChanged.connect(self.on_filtros_changed)
        
        hasta_layout.addWidget(lbl_hasta)
        hasta_layout.addWidget(self.date_hasta)
        row2_layout.addLayout(hasta_layout)
        
        # Botones de filtros rápidos
        rapidos_layout = QVBoxLayout()
        rapidos_layout.setSpacing(5)
        
        lbl_rapidos = QLabel("Filtros Rápidos:")
        lbl_rapidos.setObjectName("filterLabel")
        
        rapidos_btns = QHBoxLayout()
        rapidos_btns.setSpacing(5)
        
        btn_hoy = QPushButton("Hoy")
        btn_hoy.setObjectName("quickFilterButton")
        btn_hoy.clicked.connect(lambda: self.filtro_rapido('hoy'))
        
        btn_semana = QPushButton("Esta Semana")
        btn_semana.setObjectName("quickFilterButton")
        btn_semana.clicked.connect(lambda: self.filtro_rapido('semana'))
        
        btn_mes = QPushButton("Este Mes")
        btn_mes.setObjectName("quickFilterButton")
        btn_mes.clicked.connect(lambda: self.filtro_rapido('mes'))
        
        rapidos_btns.addWidget(btn_hoy)
        rapidos_btns.addWidget(btn_semana)
        rapidos_btns.addWidget(btn_mes)
        rapidos_btns.addStretch()
        
        rapidos_layout.addWidget(lbl_rapidos)
        rapidos_layout.addLayout(rapidos_btns)
        row2_layout.addLayout(rapidos_layout, 1)
        
        # Botón limpiar filtros
        btn_limpiar = QPushButton("🗑️ Limpiar Filtros")
        btn_limpiar.setObjectName("secondaryButton")
        btn_limpiar.clicked.connect(self.limpiar_filtros)
        row2_layout.addWidget(btn_limpiar)
        
        filtros_layout.addLayout(row2_layout)
        
        layout.addWidget(filtros_frame)
        
        # --- Tabla de Operaciones ---
        self.tabla_operaciones = QTableWidget()
        self.tabla_operaciones.setObjectName("tablaOperaciones")
        self.tabla_operaciones.setColumnCount(9)
        self.tabla_operaciones.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Ticker", "Nombre", "Cantidad", 
            "Precio", "Total", "Estado", "Acciones"
        ])
        
        # Configurar columnas
        header = self.tabla_operaciones.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        self.tabla_operaciones.setColumnWidth(8, 100)
        
        self.tabla_operaciones.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_operaciones.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        
        layout.addWidget(self.tabla_operaciones, 1)
        
        # Footer con totales
        footer_layout = QHBoxLayout()
        
        self.lbl_total_ordenes = QLabel("Total: 0 órdenes")
        self.lbl_total_ordenes.setObjectName("footerLabel")
        
        footer_layout.addWidget(self.lbl_total_ordenes)
        footer_layout.addStretch()
        
        layout.addLayout(footer_layout)
    
    def filtro_rapido(self, periodo: str):
        """Aplica filtros rápidos de fecha"""
        hoy = QDate.currentDate()
        
        if periodo == 'hoy':
            self.date_desde.setDate(hoy)
            self.date_hasta.setDate(hoy)
        elif periodo == 'semana':
            self.date_desde.setDate(hoy.addDays(-7))
            self.date_hasta.setDate(hoy)
        elif periodo == 'mes':
            self.date_desde.setDate(hoy.addMonths(-1))
            self.date_hasta.setDate(hoy)
    
    def limpiar_filtros(self):
        """Limpia todos los filtros"""
        self.input_search.clear()
        self.combo_tipo.setCurrentIndex(0)
        self.combo_estado.setCurrentIndex(0)
        self.date_desde.setDate(QDate.currentDate().addMonths(-1))
        self.date_hasta.setDate(QDate.currentDate())
    
    def on_filtros_changed(self):
        """Handler cuando cambian los filtros"""
        self.filtros_aplicados.emit()
    
    def obtener_filtros(self) -> dict:
        """Retorna los filtros actuales"""
        filtros = {}
        
        # Ticker
        ticker = self.input_search.text().strip()
        if ticker:
            filtros['ticker'] = ticker
        
        # Tipo
        tipo = self.combo_tipo.currentData()
        if tipo:
            filtros['tipo'] = tipo
        
        # Estado
        estado = self.combo_estado.currentData()
        if estado:
            filtros['estado'] = estado
        
        # Fechas
        filtros['fecha_desde'] = self.date_desde.date().toPyDate()
        filtros['fecha_hasta'] = self.date_hasta.date().toPyDate()
        
        return filtros
    
    def poblar_tabla(self, ordenes: list):
        """Puebla la tabla con las órdenes"""
        self.ordenes = ordenes
        self.tabla_operaciones.setRowCount(len(ordenes))
        
        for row, orden in enumerate(ordenes):
            # Fecha
            fecha_str = orden['fecha_orden']
            if isinstance(fecha_str, str):
                try:
                    fecha = datetime.fromisoformat(fecha_str)
                    fecha_display = fecha.strftime("%d/%m/%Y")
                except:
                    fecha_display = fecha_str
            else:
                fecha_display = str(fecha_str)
            
            self.tabla_operaciones.setItem(row, 0, QTableWidgetItem(fecha_display))
            
            # Tipo
            tipo_item = QTableWidgetItem(orden['tipo'])
            if orden['tipo'] == TipoOrden.COMPRA.value:
                tipo_item.setForeground(QColor("#4CAF50"))
            else:
                tipo_item.setForeground(QColor("#F44336"))
            self.tabla_operaciones.setItem(row, 1, tipo_item)
            
            # Ticker
            self.tabla_operaciones.setItem(row, 2, QTableWidgetItem(orden['ticker']))
            
            # Nombre
            self.tabla_operaciones.setItem(row, 3, QTableWidgetItem(
                orden.get('titulo_nombre', '-')
            ))
            
            # Cantidad
            cant_item = QTableWidgetItem(f"{orden['cantidad']:,}")
            cant_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_operaciones.setItem(row, 4, cant_item)
            
            # Precio
            precio = orden.get('precio_limite', 0)
            precio_item = QTableWidgetItem(f"Bs. {precio:,.2f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_operaciones.setItem(row, 5, precio_item)
            
            # Total
            total = orden.get('monto_total_estimado', 0)
            total_item = QTableWidgetItem(f"Bs. {total:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_operaciones.setItem(row, 6, total_item)
            
            # Estado
            estado_item = self._crear_badge_estado(orden['estado'])
            self.tabla_operaciones.setCellWidget(row, 7, estado_item)
            
            # Acciones
            acciones_widget = self._crear_acciones(orden)
            self.tabla_operaciones.setCellWidget(row, 8, acciones_widget)
        
        # Actualizar totales
        self.lbl_total_ordenes.setText(f"Total: {len(ordenes)} órdenes")
    
    def _crear_badge_estado(self, estado: str) -> QWidget:
        """Crea un badge para el estado"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        badge = QLabel(estado)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Estilos según estado
        if estado == EstadoOrden.EJECUTADA.value:
            badge.setObjectName("badgeSuccess")
        elif estado == EstadoOrden.PENDIENTE.value:
            badge.setObjectName("badgeWarning")
        elif estado == EstadoOrden.CANCELADA.value:
            badge.setObjectName("badgeDanger")
        elif estado == EstadoOrden.ESPERANDO_FONDOS.value:
            badge.setObjectName("badgeInfo")
        else:
            badge.setObjectName("badgeDefault")
        
        layout.addWidget(badge)
        return widget
    
    def _crear_acciones(self, orden: dict) -> QWidget:
        """Crea los botones de acciones para una orden"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        btn_ver = QPushButton("👁")
        btn_ver.setObjectName("actionButton")
        btn_ver.setToolTip("Ver detalles")
        btn_ver.clicked.connect(lambda: self.orden_seleccionada.emit(orden['id']))
        
        layout.addWidget(btn_ver)
        
        # Botón cancelar solo si está pendiente
        if orden['estado'] in [EstadoOrden.PENDIENTE.value, EstadoOrden.ESPERANDO_FONDOS.value]:
            btn_cancelar = QPushButton("✖")
            btn_cancelar.setObjectName("actionButtonDanger")
            btn_cancelar.setToolTip("Cancelar orden")
            btn_cancelar.clicked.connect(lambda: self.confirmar_cancelacion(orden))
            layout.addWidget(btn_cancelar)
        
        return widget
    
    def confirmar_cancelacion(self, orden: dict):
        """Confirma la cancelación de una orden"""
        respuesta = QMessageBox.question(
            self,
            "Cancelar Orden",
            f"¿Desea cancelar la orden de {orden['tipo']} de {orden['ticker']}?\n\n"
            f"Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            # Emitir señal para que el controller maneje la cancelación
            # (Aquí necesitarías agregar una señal cancelar_orden)
            logger.info(f"Solicitud de cancelación para orden {orden['id']}")
    
    def aplicar_estilos(self):
        """Aplica estilos CSS"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            
            #pageTitle {
                font-size: 24px;
                font-weight: bold;
                color: #FF6B00;
            }
            
            #backButton {
                background-color: transparent;
                color: #AAAAAA;
                border: 2px solid #3D3D3D;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
            }
            
            #backButton:hover {
                border-color: #FF6B00;
                color: #FF6B00;
            }
            
            #primaryButton {
                background-color: #FF6B00;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #primaryButton:hover {
                background-color: #FF8534;
            }
            
            #filtrosFrame {
                background-color: #2D2D2D;
                border-radius: 8px;
                padding: 20px;
                border: 2px solid #3D3D3D;
            }
            
            #filtrosTitle {
                font-size: 16px;
                font-weight: bold;
                color: #FF6B00;
                padding-bottom: 10px;
            }
            
            #filterLabel {
                font-size: 12px;
                color: #AAAAAA;
                font-weight: bold;
            }
            
            #filterInput {
                background-color: #1E1E1E;
                border: 2px solid #3D3D3D;
                border-radius: 6px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 13px;
                min-height: 30px;
            }
            
            #filterInput:focus {
                border-color: #FF6B00;
            }
            
            #quickFilterButton {
                background-color: #3D3D3D;
                color: #CCCCCC;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            
            #quickFilterButton:hover {
                background-color: #FF6B00;
                color: white;
            }
            
            #secondaryButton {
                background-color: transparent;
                color: #AAAAAA;
                border: 2px solid #3D3D3D;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            
            #secondaryButton:hover {
                border-color: #FF6B00;
                color: #FF6B00;
            }
            
            #tablaOperaciones {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 8px;
                gridline-color: #3D3D3D;
            }
            
            #tablaOperaciones::item {
                padding: 10px;
                border-bottom: 1px solid #3D3D3D;
            }
            
            #tablaOperaciones::item:selected {
                background-color: #FF6B00;
            }
            
            #tablaOperaciones QHeaderView::section {
                background-color: #1E1E1E;
                color: #AAAAAA;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #FF6B00;
                font-weight: bold;
                font-size: 13px;
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
            
            #actionButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                min-width: 30px;
            }
            
            #actionButton:hover {
                background-color: #42A5F5;
            }
            
            #actionButtonDanger {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                min-width: 30px;
            }
            
            #actionButtonDanger:hover {
                background-color: #E57373;
            }
            
            #footerLabel {
                font-size: 13px;
                color: #AAAAAA;
                font-weight: bold;
            }
        """)