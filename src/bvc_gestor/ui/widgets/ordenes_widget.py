# src/bvc_gestor/ui/widgets/ordenes_widget.py
"""
Widget de gestión de órdenes bursátiles
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QToolBar,
    QStatusBar, QSplitter, QFrame, QGroupBox, QTextEdit,
    QDateEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QTabWidget,
    QFormLayout, QScrollArea, QSizePolicy, QDialog, QDialogButtonBox,
    QProgressBar, QToolButton, QMenu, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTimer, QSize, QDateTime
from PyQt6.QtGui import QIcon, QFont, QAction, QKeySequence, QShortcut, QColor
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any

from ...core.app_state import AppState
from ...utils.logger import logger
from ...utils.constants import TipoOrden, TipoOperacion, EstadoOrden, Moneda
from ...database.engine import get_database
from ...database.repositories import RepositoryFactory
from ...database.models_sql import OrdenDB, ClienteDB, ActivoDB, CuentaDB
from ...services.orden_service import OrdenService

class OrdenesTableWidget(QTableWidget):
    """Tabla personalizada para órdenes"""
    
    orden_selected = pyqtSignal(int)  # Señal con ID de la orden
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz de la tabla"""
        # Configurar columnas
        self.setColumnCount(10)
        self.setHorizontalHeaderLabels([
            "ID", "N° Orden", "Cliente", "Activo", "Tipo", 
            "Cantidad", "Precio", "Estado", "Creada", "Total"
        ])
        
        # Configurar propiedades
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        
        # Ajustar ancho de columnas
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # N° Orden
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Cliente
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Activo
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Tipo
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Cantidad
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Precio
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Creada
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Total
        
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
    
    def load_ordenes(self, ordenes: List[OrdenDB]):
        """Cargar órdenes en la tabla"""
        self.setRowCount(0)  # Limpiar tabla
        
        for row, orden in enumerate(ordenes):
            self.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(orden.id))
            id_item.setData(Qt.ItemDataRole.UserRole, orden.id)
            self.setItem(row, 0, id_item)
            
            # Número de orden
            orden_item = QTableWidgetItem(orden.numero_orden)
            self.setItem(row, 1, orden_item)
            
            # Cliente (obtener nombre)
            cliente_nombre = self.get_cliente_nombre(orden.cliente_id)
            cliente_item = QTableWidgetItem(cliente_nombre)
            self.setItem(row, 2, cliente_item)
            
            # Activo
            activo_item = QTableWidgetItem(orden.activo_id)
            self.setItem(row, 3, activo_item)
            
            # Tipo (Compra/Venta + Mercado/Limitada)
            tipo_text = f"{orden.tipo_orden.value[:1]}-{orden.tipo_operacion.value[:1]}"
            tipo_item = QTableWidgetItem(tipo_text)
            
            # Color según tipo de orden
            if orden.tipo_orden.value == TipoOrden.COMPRA.value:
                tipo_item.setForeground(QColor("#198754"))  # Verde para compra
            else:
                tipo_item.setForeground(QColor("#dc3545"))  # Rojo para venta
            
            self.setItem(row, 4, tipo_item)
            
            # Cantidad
            cantidad_item = QTableWidgetItem(f"{orden.cantidad:,}")
            cantidad_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row, 5, cantidad_item)
            
            # Precio
            precio = orden.precio or orden.precio_limite or 0
            precio_item = QTableWidgetItem(f"${float(precio):,.4f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row, 6, precio_item)
            
            # Estado
            estado_item = QTableWidgetItem(orden.estado.value)
            
            # Color según estado
            if orden.estado.value == EstadoOrden.EJECUTADA.value:
                estado_item.setForeground(QColor("#198754"))
            elif orden.estado.value == EstadoOrden.PENDIENTE.value:
                estado_item.setForeground(QColor("#ffc107"))
            elif orden.estado.value == EstadoOrden.CANCELADA.value:
                estado_item.setForeground(QColor("#6c757d"))
            elif orden.estado.value == EstadoOrden.RECHAZADA.value:
                estado_item.setForeground(QColor("#dc3545"))
            
            self.setItem(row, 7, estado_item)
            
            # Fecha creación
            fecha_item = QTableWidgetItem(orden.fecha_creacion.strftime("%d/%m %H:%M"))
            self.setItem(row, 8, fecha_item)
            
            # Total estimado
            if precio:
                total = float(precio) * orden.cantidad
                total_item = QTableWidgetItem(f"${total:,.2f}")
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                # Color según tipo
                if orden.tipo_orden.value == TipoOrden.COMPRA.value:
                    total_item.setForeground(QColor("#198754"))
                else:
                    total_item.setForeground(QColor("#dc3545"))
                    
                self.setItem(row, 9, total_item)
    
    def get_cliente_nombre(self, cliente_id: str) -> str:
        """Obtener nombre del cliente por ID"""
        try:
            db = get_database()
            session = db.get_session()
            cliente_repo = RepositoryFactory.get_repository(session, 'cliente')
            cliente = cliente_repo.get(cliente_id)
            session.close()
            
            if cliente:
                # Acortar nombre si es muy largo
                nombre = cliente.nombre_completo
                if len(nombre) > 20:
                    return nombre[:17] + "..."
                return nombre
            return cliente_id
        except:
            return cliente_id
    
    def on_selection_changed(self):
        """Manejar cambio de selección"""
        selected_items = self.selectedItems()
        if selected_items:
            # El ID está en la columna 0
            for item in selected_items:
                if item.column() == 0:
                    orden_id = item.data(Qt.ItemDataRole.UserRole)
                    if orden_id:
                        self.orden_selected.emit(orden_id)
                    break

class NuevaOrdenDialog(QDialog):
    """Diálogo para crear nueva orden"""
    
    orden_creada = pyqtSignal(dict)  # Señal con datos de la orden creada
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.orden_service = OrdenService()
        self.cliente_actual = None
        self.cuenta_actual = None
        self.activo_seleccionado = None
        self.setup_ui()
        self.setup_connections()
        self.cargar_datos_iniciales()
        self.setWindowTitle("Nueva Orden Bursátil")
        self.resize(700, 600)
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Crear pestañas
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Pestaña 1: Selección de cliente y activo
        seleccion_tab = QWidget()
        seleccion_layout = QVBoxLayout()
        seleccion_tab.setLayout(seleccion_layout)
        
        # Grupo: Selección de cliente
        cliente_group = QGroupBox("👤 Cliente")
        cliente_layout = QFormLayout()
        cliente_group.setLayout(cliente_layout)
        
        self.cliente_combo = QComboBox()
        self.cliente_combo.setEditable(True)
        self.cliente_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        cliente_layout.addRow("Cliente:", self.cliente_combo)
        
        self.cuenta_combo = QComboBox()
        cliente_layout.addRow("Cuenta:", self.cuenta_combo)
        
        # Información del cliente seleccionado
        self.cliente_info_label = QLabel("Seleccione un cliente")
        self.cliente_info_label.setWordWrap(True)
        self.cliente_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        cliente_layout.addRow(self.cliente_info_label)
        
        seleccion_layout.addWidget(cliente_group)
        
        # Grupo: Selección de activo
        activo_group = QGroupBox("📈 Activo Bursátil")
        activo_layout = QVBoxLayout()
        activo_group.setLayout(activo_layout)
        
        # Búsqueda de activos
        search_layout = QHBoxLayout()
        self.activo_search = QLineEdit()
        self.activo_search.setPlaceholderText("Buscar por símbolo o nombre...")
        search_layout.addWidget(self.activo_search)
        
        self.search_btn = QPushButton("🔍 Buscar")
        search_layout.addWidget(self.search_btn)
        
        activo_layout.addLayout(search_layout)
        
        # Lista de activos
        self.activos_table = QTableWidget()
        self.activos_table.setColumnCount(5)
        self.activos_table.setHorizontalHeaderLabels(["Símbolo", "Nombre", "Precio", "Variación", "Sector"])
        self.activos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.activos_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        header = self.activos_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.activos_table.setMaximumHeight(200)
        activo_layout.addWidget(self.activos_table)
        
        # Información del activo seleccionado
        self.activo_info_label = QLabel("Seleccione un activo")
        self.activo_info_label.setWordWrap(True)
        self.activo_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        activo_layout.addWidget(self.activo_info_label)
        
        seleccion_layout.addWidget(activo_group)
        
        tab_widget.addTab(seleccion_tab, "1. Selección")
        
        # Pestaña 2: Configuración de la orden
        config_tab = QWidget()
        config_layout = QVBoxLayout()
        config_tab.setLayout(config_layout)
        
        # Grupo: Tipo de orden
        tipo_group = QGroupBox("📋 Tipo de Orden")
        tipo_layout = QGridLayout()
        tipo_group.setLayout(tipo_layout)
        
        self.tipo_orden_combo = QComboBox()
        self.tipo_orden_combo.addItems([TipoOrden.COMPRA.value, TipoOrden.VENTA.value])
        tipo_layout.addWidget(QLabel("Operación:"), 0, 0)
        tipo_layout.addWidget(self.tipo_orden_combo, 0, 1)
        
        self.tipo_operacion_combo = QComboBox()
        self.tipo_operacion_combo.addItems([TipoOperacion.MERCADO.value, TipoOperacion.LIMITADA.value])
        self.tipo_operacion_combo.currentTextChanged.connect(self.on_tipo_operacion_changed)
        tipo_layout.addWidget(QLabel("Tipo:"), 1, 0)
        tipo_layout.addWidget(self.tipo_operacion_combo, 1, 1)
        
        config_layout.addWidget(tipo_group)
        
        # Grupo: Detalles de la orden
        detalles_group = QGroupBox("💰 Detalles")
        detalles_layout = QFormLayout()
        detalles_group.setLayout(detalles_layout)
        
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setRange(1, 1000000)
        self.cantidad_spin.setValue(100)
        detalles_layout.addRow("Cantidad:", self.cantidad_spin)
        
        self.precio_limite_spin = QDoubleSpinBox()
        self.precio_limite_spin.setRange(0.0001, 10000.0000)
        self.precio_limite_spin.setDecimals(4)
        self.precio_limite_spin.setPrefix("$ ")
        self.precio_limite_spin.setEnabled(False)  # Solo para órdenes limitadas
        detalles_layout.addRow("Precio Límite:", self.precio_limite_spin)
        
        config_layout.addWidget(detalles_group)
        
        # Grupo: Simulación
        simulacion_group = QGroupBox("📊 Simulación")
        simulacion_layout = QVBoxLayout()
        simulacion_group.setLayout(simulacion_layout)
        
        self.simular_btn = QPushButton("🔄 Simular Orden")
        self.simular_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        simulacion_layout.addWidget(self.simular_btn)
        
        self.simulacion_label = QLabel("Haga clic en 'Simular Orden' para ver detalles")
        self.simulacion_label.setWordWrap(True)
        self.simulacion_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 15px;
                margin-top: 10px;
                font-size: 13px;
            }
        """)
        simulacion_layout.addWidget(self.simulacion_label)
        
        config_layout.addWidget(simulacion_group)
        
        # Grupo: Notas
        notas_group = QGroupBox("📝 Notas")
        notas_layout = QVBoxLayout()
        notas_group.setLayout(notas_layout)
        
        self.notas_edit = QTextEdit()
        self.notas_edit.setMaximumHeight(80)
        self.notas_edit.setPlaceholderText("Notas adicionales sobre esta orden...")
        notas_layout.addWidget(self.notas_edit)
        
        config_layout.addWidget(notas_group)
        
        tab_widget.addTab(config_tab, "2. Configuración")
        
        # Botones del diálogo
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.aceptar)
        button_box.rejected.connect(self.reject)
        
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Crear Orden")
        self.ok_button.setEnabled(False)  # Deshabilitado hasta que todo esté completo
        
        layout.addWidget(button_box)
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Cliente
        self.cliente_combo.currentIndexChanged.connect(self.on_cliente_seleccionado)
        
        # Activo
        self.search_btn.clicked.connect(self.buscar_activos)
        self.activos_table.itemSelectionChanged.connect(self.on_activo_seleccionado)
        self.activo_search.returnPressed.connect(self.buscar_activos)
        
        # Simulación
        self.simular_btn.clicked.connect(self.simular_orden)
        
        # Cambios en campos que afectan la simulación
        self.cantidad_spin.valueChanged.connect(self.on_campos_cambiados)
        self.precio_limite_spin.valueChanged.connect(self.on_campos_cambiados)
        self.tipo_orden_combo.currentTextChanged.connect(self.on_campos_cambiados)
        self.tipo_operacion_combo.currentTextChanged.connect(self.on_campos_cambiados)
    
    def cargar_datos_iniciales(self):
        """Cargar datos iniciales en combos"""
        # Cargar clientes
        try:
            db = get_database()
            session = db.get_session()
            cliente_repo = RepositoryFactory.get_repository(session, 'cliente')
            
            clientes = cliente_repo.get_active_clients()
            self.cliente_combo.clear()
            self.cliente_combo.addItem("-- Seleccione un cliente --", None)
            
            for cliente in clientes:
                texto = f"{cliente.nombre_completo} ({cliente.id})"
                self.cliente_combo.addItem(texto, cliente.id)
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error cargando clientes: {e}")
    
    def buscar_activos(self):
        """Buscar activos por texto"""
        query = self.activo_search.text().strip()
        
        try:
            db = get_database()
            session = db.get_session()
            activo_repo = RepositoryFactory.get_repository(session, 'activo')
            
            if query:
                activos = activo_repo.search(query)
            else:
                activos = activo_repo.get_active_assets()
            
            # Mostrar en tabla
            self.activos_table.setRowCount(0)
            
            for row, activo in enumerate(activos):
                self.activos_table.insertRow(row)
                
                # Símbolo
                simbolo_item = QTableWidgetItem(activo.id)
                simbolo_item.setData(Qt.ItemDataRole.UserRole, activo.id)
                self.activos_table.setItem(row, 0, simbolo_item)
                
                # Nombre
                nombre_item = QTableWidgetItem(activo.nombre)
                self.activos_table.setItem(row, 1, nombre_item)
                
                # Precio
                precio_item = QTableWidgetItem(f"${float(activo.precio_actual):,.4f}")
                precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.activos_table.setItem(row, 2, precio_item)
                
                # Variación
                variacion = float(activo.variacion_diaria)
                color = "#198754" if variacion >= 0 else "#dc3545"
                signo = "+" if variacion >= 0 else ""
                variacion_item = QTableWidgetItem(f"{signo}{variacion:,.4f}")
                variacion_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                variacion_item.setForeground(QColor(color))
                self.activos_table.setItem(row, 3, variacion_item)
                
                # Sector
                sector_item = QTableWidgetItem(activo.sector or "N/A")
                self.activos_table.setItem(row, 4, sector_item)
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error buscando activos: {e}")
    
    def on_cliente_seleccionado(self, index: int):
        """Manejar selección de cliente"""
        cliente_id = self.cliente_combo.itemData(index)
        
        if not cliente_id:
            self.cliente_actual = None
            self.cuenta_actual = None
            self.cliente_info_label.setText("Seleccione un cliente")
            self.cuenta_combo.clear()
            self.validar_formulario()
            return
        
        try:
            db = get_database()
            session = db.get_session()
            
            # Obtener cliente
            cliente_repo = RepositoryFactory.get_repository(session, 'cliente')
            cliente = cliente_repo.get(cliente_id)
            
            if cliente:
                self.cliente_actual = cliente
                
                # Mostrar información
                info = f"""
                <b>{cliente.nombre_completo}</b><br>
                ID: {cliente.id} | Tipo: {cliente.tipo_persona.value}<br>
                Perfil: {cliente.perfil_riesgo.value} | Límite USD: ${float(cliente.limite_inversion_usd or 0):,.2f}
                """
                self.cliente_info_label.setText(info)
                
                # Cargar cuentas del cliente
                cuenta_repo = RepositoryFactory.get_repository(session, 'cuenta')
                cuentas = cuenta_repo.get_by_cliente(cliente_id)
                
                self.cuenta_combo.clear()
                self.cuenta_combo.addItem("-- Seleccione cuenta --", None)
                
                for cuenta in cuentas:
                    if cuenta.estado == "Activa":
                        texto = f"{cuenta.numero_cuenta} (${float(cuenta.saldo_disponible_usd or 0):,.2f} disp.)"
                        self.cuenta_combo.addItem(texto, cuenta.id)
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error cargando cliente: {e}")
            self.cliente_info_label.setText(f"Error: {str(e)}")
    
    def on_activo_seleccionado(self):
        """Manejar selección de activo"""
        selected_items = self.activos_table.selectedItems()
        if not selected_items:
            return
        
        # Obtener símbolo del activo (columna 0)
        for item in selected_items:
            if item.column() == 0:
                activo_id = item.data(Qt.ItemDataRole.UserRole)
                self.cargar_info_activo(activo_id)
                break
    
    def cargar_info_activo(self, activo_id: str):
        """Cargar información del activo seleccionado"""
        try:
            db = get_database()
            session = db.get_session()
            activo_repo = RepositoryFactory.get_repository(session, 'activo')
            
            activo = activo_repo.get(activo_id)
            if activo:
                self.activo_seleccionado = activo
                
                # Mostrar información
                variacion = float(activo.variacion_diaria)
                color = "green" if variacion >= 0 else "red"
                signo = "+" if variacion >= 0 else ""
                
                info = f"""
                <b>{activo.nombre} ({activo.id})</b><br>
                Tipo: {activo.tipo} | Sector: {activo.sector or "N/A"}<br>
                Precio: <b>${float(activo.precio_actual):,.4f}</b> {activo.moneda}<br>
                Variación: <span style='color:{color}'><b>{signo}{variacion:,.4f}</b></span> | Lote: {activo.lote_standard}
                """
                self.activo_info_label.setText(info)
                
                # Establecer precio límite por defecto
                self.precio_limite_spin.setValue(float(activo.precio_actual))
                
                # Ajustar cantidad al lote estándar
                cantidad_actual = self.cantidad_spin.value()
                if cantidad_actual % activo.lote_standard != 0:
                    sugerido = ((cantidad_actual // activo.lote_standard) + 1) * activo.lote_standard
                    self.cantidad_spin.setValue(sugerido)
                    QMessageBox.information(
                        self, "Ajuste de cantidad",
                        f"La cantidad se ajustó al lote estándar: {sugerido:,} (lote: {activo.lote_standard})"
                    )
            
            session.close()
            self.validar_formulario()
            
        except Exception as e:
            logger.error(f"Error cargando activo: {e}")
    
    def on_tipo_operacion_changed(self, tipo: str):
        """Manejar cambio en tipo de operación"""
        if tipo == TipoOperacion.LIMITADA.value:
            self.precio_limite_spin.setEnabled(True)
        else:
            self.precio_limite_spin.setEnabled(False)
    
    def on_campos_cambiados(self):
        """Manejar cambios en campos de la orden"""
        # Limpiar simulación anterior
        self.simulacion_label.setText("Haga clic en 'Simular Orden' para ver detalles actualizados")
        self.simulacion_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 15px;
                margin-top: 10px;
                font-size: 13px;
            }
        """)
    
    def simular_orden(self):
        """Simular la orden actual"""
        if not self.validar_campos_simulacion():
            return
        
        # Obtener datos para simulación
        datos = self.obtener_datos_simulacion()
        
        # Llamar al servicio de simulación
        try:
            resultado = self.orden_service.simular_orden(datos)
            
            if "error" in resultado:
                self.mostrar_error_simulacion(resultado["error"])
                return
            
            # Mostrar resultados
            self.mostrar_resultado_simulacion(resultado)
            
        except Exception as e:
            logger.error(f"Error en simulación: {e}")
            self.mostrar_error_simulacion(str(e))
    
    def validar_campos_simulacion(self) -> bool:
        """Validar campos necesarios para simulación"""
        errores = []
        
        if not self.cliente_actual:
            errores.append("Seleccione un cliente")
        
        if not self.cuenta_actual:
            errores.append("Seleccione una cuenta")
        
        if not self.activo_seleccionado:
            errores.append("Seleccione un activo")
        
        if self.tipo_operacion_combo.currentText() == TipoOperacion.LIMITADA.value:
            if self.precio_limite_spin.value() <= 0:
                errores.append("Ingrese un precio límite válido")
        
        if self.cantidad_spin.value() <= 0:
            errores.append("Ingrese una cantidad válida")
        
        if errores:
            QMessageBox.warning(self, "Campos incompletos", "\n".join(errores))
            return False
        
        return True
    
    def obtener_datos_simulacion(self) -> Dict[str, Any]:
        """Obtener datos para simulación"""
        return {
            'cliente_id': self.cliente_actual.id,
            'cuenta_id': self.cuenta_actual,
            'activo_id': self.activo_seleccionado.id,
            'tipo_orden': self.tipo_orden_combo.currentText(),
            'tipo_operacion': self.tipo_operacion_combo.currentText(),
            'cantidad': self.cantidad_spin.value(),
            'precio_limite': self.precio_limite_spin.value() if self.tipo_operacion_combo.currentText() == TipoOperacion.LIMITADA.value else None,
            'precio': None  # Para órdenes de mercado
        }
    
    def mostrar_resultado_simulacion(self, resultado: Dict[str, Any]):
        """Mostrar resultado de simulación"""
        simulacion = resultado['simulacion']
        comisiones = resultado['comisiones']
        montos = resultado['montos']
        validacion = resultado['validacion']
        activo = resultado['activo']
        
        # Determinar color según validación
        color = "#198754" if validacion['es_valida'] else "#dc3545"
        icon = "✅" if validacion['es_valida'] else "❌"
        
        html = f"""
        <div style='border-left: 4px solid {color}; padding-left: 10px;'>
            <h4 style='color: {color}; margin-top: 0;'>{icon} {validacion['mensaje']}</h4>
            
            <b>Activo:</b> {activo['nombre']} ({activo['simbolo']})<br>
            <b>Precio actual:</b> ${activo['precio_actual']:,.4f} {activo['moneda']}<br>
            <b>Precio ejecución estimado:</b> ${simulacion['precio_ejecucion']:,.4f}<br>
            <b>Probabilidad de ejecución:</b> {simulacion['probabilidad_ejecucion']*100:.0f}%<br>
            <b>Tiempo estimado:</b> {simulacion['tiempo_estimado_minutos']} minutos<br><br>
            
            <b>Montos:</b><br>
            • Operación: ${montos['operacion']:,.2f}<br>
            • Comisiones: ${montos['comisiones']:,.2f} (${comisiones['base']:,.2f} + ${comisiones['iva']:,.2f} IVA)<br>
            • <b>Total: ${montos['total']:,.2f}</b><br><br>
            
            <i>{simulacion['comentario']}</i>
        </div>
        """
        
        self.simulacion_label.setText(html)
        self.simulacion_label.setTextFormat(Qt.TextFormat.RichText)
    
    def mostrar_error_simulacion(self, error: str):
        """Mostrar error en simulación"""
        html = f"""
        <div style='border-left: 4px solid #dc3545; padding-left: 10px;'>
            <h4 style='color: #dc3545; margin-top: 0;'>❌ Error en simulación</h4>
            <p>{error}</p>
        </div>
        """
        self.simulacion_label.setText(html)
        self.simulacion_label.setTextFormat(Qt.TextFormat.RichText)
    
    def validar_formulario(self):
        """Validar todo el formulario"""
        campos_completos = all([
            self.cliente_actual,
            self.cuenta_actual,
            self.activo_seleccionado,
            self.cantidad_spin.value() > 0
        ])
        
        if self.tipo_operacion_combo.currentText() == TipoOperacion.LIMITADA.value:
            campos_completos = campos_completos and (self.precio_limite_spin.value() > 0)
        
        self.ok_button.setEnabled(campos_completos)
    
    def obtener_datos_orden(self) -> Dict[str, Any]:
        """Obtener datos completos de la orden"""
        cuenta_id = self.cuenta_combo.currentData()
        
        return {
            'cliente_id': self.cliente_actual.id,
            'cuenta_id': cuenta_id,
            'activo_id': self.activo_seleccionado.id,
            'tipo_orden': self.tipo_orden_combo.currentText(),
            'tipo_operacion': self.tipo_operacion_combo.currentText(),
            'cantidad': self.cantidad_spin.value(),
            'precio_limite': self.precio_limite_spin.value() if self.tipo_operacion_combo.currentText() == TipoOperacion.LIMITADA.value else None,
            'notas': self.notas_edit.toPlainText().strip() or None
        }
    
    def aceptar(self):
        """Aceptar y crear la orden"""
        if not self.validar_campos_simulacion():
            return
        
        # Confirmación final
        reply = QMessageBox.question(
            self, "Confirmar orden",
            "¿Está seguro de crear esta orden?\n\n"
            "Esta acción bloqueará los fondos necesarios y creará la orden bursátil.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            datos = self.obtener_datos_orden()
            orden, mensaje = self.orden_service.crear_orden(datos)
            
            if orden:
                QMessageBox.information(self, "Éxito", f"Orden creada exitosamente:\n\nNúmero: {orden.numero_orden}")
                self.orden_creada.emit(datos)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", f"No se pudo crear la orden:\n\n{mensaje}")
                
        except Exception as e:
            logger.error(f"Error creando orden: {e}")
            QMessageBox.critical(self, "Error", f"Error creando orden:\n\n{str(e)}")

class OrdenesWidget(QWidget):
    """Widget principal de gestión de órdenes"""
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.db_session = None
        self.orden_service = OrdenService()
        self.current_orden_id = None
        self.setup_ui()
        self.setup_connections()
        self.load_ordenes()
        logger.info("OrdenesWidget inicializado")
    
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
        
        # Acciones
        self.nueva_orden_action = QAction("➕ Nueva Orden", self)
        self.nueva_orden_action.setToolTip("Crear nueva orden bursátil")
        
        self.cancelar_orden_action = QAction("⏹️ Cancelar", self)
        self.cancelar_orden_action.setToolTip("Cancelar orden seleccionada")
        self.cancelar_orden_action.setEnabled(False)
        
        self.ver_detalles_action = QAction("👁️ Detalles", self)
        self.ver_detalles_action.setToolTip("Ver detalles de orden seleccionada")
        self.ver_detalles_action.setEnabled(False)
        
        self.refresh_action = QAction("🔄 Actualizar", self)
        self.refresh_action.setToolTip("Actualizar lista de órdenes")
        
        # Botón de filtros con menú
        self.filtros_btn = QToolButton()
        self.filtros_btn.setText("🔍 Filtros")
        self.filtros_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        filtros_menu = QMenu()
        self.filtro_todas = QAction("Todas las órdenes", self)
        self.filtro_todas.setCheckable(True)
        self.filtro_todas.setChecked(True)
        
        self.filtro_pendientes = QAction("Órdenes pendientes", self)
        self.filtro_pendientes.setCheckable(True)
        
        self.filtro_hoy = QAction("Órdenes de hoy", self)
        self.filtro_hoy.setCheckable(True)
        
        filtros_menu.addAction(self.filtro_todas)
        filtros_menu.addAction(self.filtro_pendientes)
        filtros_menu.addAction(self.filtro_hoy)
        self.filtros_btn.setMenu(filtros_menu)
        
        # Agregar acciones a toolbar
        toolbar.addAction(self.nueva_orden_action)
        toolbar.addAction(self.cancelar_orden_action)
        toolbar.addAction(self.ver_detalles_action)
        toolbar.addSeparator()
        toolbar.addWidget(self.filtros_btn)
        toolbar.addSeparator()
        toolbar.addAction(self.refresh_action)
        
        # Barra de búsqueda
        toolbar.addWidget(QLabel("   Buscar:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("N° orden, cliente, activo...")
        self.search_edit.setMaximumWidth(300)
        toolbar.addWidget(self.search_edit)
        
        main_layout.addWidget(toolbar)
        
        # Splitter para dividir tabla y detalles
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Panel superior: Tabla de órdenes
        top_panel = QWidget()
        top_layout = QVBoxLayout()
        top_panel.setLayout(top_layout)
        
        # Título y estadísticas
        stats_layout = QHBoxLayout()
        
        self.title_label = QLabel("💼 Órdenes Bursátiles")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c5aa0;
            }
        """)
        stats_layout.addWidget(self.title_label)
        
        stats_layout.addStretch()
        
        self.stats_label = QLabel("Cargando...")
        self.stats_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        stats_layout.addWidget(self.stats_label)
        
        top_layout.addLayout(stats_layout)
        
        # Tabla de órdenes
        self.ordenes_table = OrdenesTableWidget()
        top_layout.addWidget(self.ordenes_table)
        
        splitter.addWidget(top_panel)
        
        # Panel inferior: Detalles de orden
        bottom_panel = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_panel.setLayout(bottom_layout)
        
        self.detalles_label = QLabel("📋 Seleccione una orden para ver sus detalles")
        self.detalles_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detalles_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
                font-style: italic;
                padding: 20px;
            }
        """)
        bottom_layout.addWidget(self.detalles_label)
        
        splitter.addWidget(bottom_panel)
        
        # Configurar proporciones
        splitter.setSizes([400, 200])
        
        main_layout.addWidget(splitter, 1)
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Listo")
        main_layout.addWidget(self.status_bar)
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Acciones de toolbar
        self.nueva_orden_action.triggered.connect(self.nueva_orden)
        self.cancelar_orden_action.triggered.connect(self.cancelar_orden)
        self.ver_detalles_action.triggered.connect(self.ver_detalles_orden)
        self.refresh_action.triggered.connect(self.load_ordenes)
        
        # Filtros
        self.filtro_todas.triggered.connect(self.aplicar_filtro_todas)
        self.filtro_pendientes.triggered.connect(self.aplicar_filtro_pendientes)
        self.filtro_hoy.triggered.connect(self.aplicar_filtro_hoy)
        
        # Búsqueda
        self.search_edit.textChanged.connect(self.buscar_ordenes)
        
        # Tabla
        self.ordenes_table.orden_selected.connect(self.on_orden_selected)
        
        # Atajos de teclado
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.nueva_orden)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(lambda: self.search_edit.setFocus())
        QShortcut(QKeySequence("F5"), self).activated.connect(self.load_ordenes)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.cancelar_orden)
    
    def load_ordenes(self):
        """Cargar órdenes desde base de datos"""
        try:
            db = get_database()
            session = db.get_session()
            orden_repo = RepositoryFactory.get_repository(session, 'orden')
            
            # Obtener todas las órdenes
            ordenes = orden_repo.get_all()
            
            # Aplicar filtro actual
            ordenes = self.aplicar_filtro_actual(ordenes)
            
            # Cargar en tabla
            self.ordenes_table.load_ordenes(ordenes)
            
            # Actualizar estadísticas
            self.actualizar_estadisticas(ordenes)
            
            self.status_bar.showMessage(f"Cargadas {len(ordenes)} órdenes", 3000)
            logger.info(f"Cargadas {len(ordenes)} órdenes")
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error cargando órdenes: {e}")
            self.status_bar.showMessage(f"Error: {str(e)}", 5000)
    
    def aplicar_filtro_actual(self, ordenes: List[OrdenDB]) -> List[OrdenDB]:
        """Aplicar filtro actual a la lista de órdenes"""
        if self.filtro_pendientes.isChecked():
            return [o for o in ordenes if o.estado.value == EstadoOrden.PENDIENTE.value]
        elif self.filtro_hoy.isChecked():
            hoy = datetime.now().date()
            return [o for o in ordenes if o.fecha_creacion.date() == hoy]
        else:  # Todas
            return ordenes
    
    def aplicar_filtro_todas(self):
        """Aplicar filtro 'Todas'"""
        self.filtro_pendientes.setChecked(False)
        self.filtro_hoy.setChecked(False)
        self.load_ordenes()
    
    def aplicar_filtro_pendientes(self):
        """Aplicar filtro 'Pendientes'"""
        self.filtro_todas.setChecked(False)
        self.filtro_hoy.setChecked(False)
        self.load_ordenes()
    
    def aplicar_filtro_hoy(self):
        """Aplicar filtro 'Hoy'"""
        self.filtro_todas.setChecked(False)
        self.filtro_pendientes.setChecked(False)
        self.load_ordenes()
    
    def actualizar_estadisticas(self, ordenes: List[OrdenDB]):
        """Actualizar estadísticas de órdenes"""
        total = len(ordenes)
        pendientes = len([o for o in ordenes if o.estado.value == EstadoOrden.PENDIENTE.value])
        ejecutadas = len([o for o in ordenes if o.estado.value == EstadoOrden.EJECUTADA.value])
        hoy = len([o for o in ordenes if o.fecha_creacion.date() == datetime.now().date()])
        
        self.stats_label.setText(
            f"Total: {total} | Pendientes: {pendientes} | Ejecutadas: {ejecutadas} | Hoy: {hoy}"
        )
    
    def buscar_ordenes(self):
        """Buscar órdenes por texto"""
        query = self.search_edit.text().strip().lower()
        
        if not query:
            self.load_ordenes()
            return
        
        try:
            db = get_database()
            session = db.get_session()
            orden_repo = RepositoryFactory.get_repository(session, 'orden')
            
            # Obtener todas y filtrar localmente (simplificado)
            todas_ordenes = orden_repo.get_all()
            ordenes_filtradas = []
            
            for orden in todas_ordenes:
                # Buscar en varios campos
                if (query in orden.numero_orden.lower() or
                    query in orden.cliente_id.lower() or
                    query in orden.activo_id.lower()):
                    ordenes_filtradas.append(orden)
            
            # Aplicar filtro actual
            ordenes_filtradas = self.aplicar_filtro_actual(ordenes_filtradas)
            
            # Mostrar resultados
            self.ordenes_table.load_ordenes(ordenes_filtradas)
            self.actualizar_estadisticas(ordenes_filtradas)
            
            self.status_bar.showMessage(f"Búsqueda: '{query}' - {len(ordenes_filtradas)} resultados", 3000)
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error buscando órdenes: {e}")
    
    def on_orden_selected(self, orden_id: int):
        """Manejar selección de orden en tabla"""
        self.current_orden_id = orden_id
        
        # Habilitar acciones
        self.cancelar_orden_action.setEnabled(True)
        self.ver_detalles_action.setEnabled(True)
        
        # Cargar detalles
        self.cargar_detalles_orden(orden_id)
    
    def cargar_detalles_orden(self, orden_id: int):
        """Cargar detalles de la orden seleccionada"""
        try:
            db = get_database()
            session = db.get_session()
            orden_repo = RepositoryFactory.get_repository(session, 'orden')
            cliente_repo = RepositoryFactory.get_repository(session, 'cliente')
            activo_repo = RepositoryFactory.get_repository(session, 'activo')
            
            orden = orden_repo.get(orden_id)
            if not orden:
                return
            
            cliente = cliente_repo.get(orden.cliente_id)
            activo = activo_repo.get(orden.activo_id)
            
            # Crear HTML con detalles
            html = self.generar_html_detalles(orden, cliente, activo)
            
            self.detalles_label.setText(html)
            self.detalles_label.setTextFormat(Qt.TextFormat.RichText)
            self.detalles_label.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 15px;
                    font-size: 13px;
                }
            """)
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error cargando detalles de orden: {e}")
            self.detalles_label.setText(f"Error cargando detalles: {str(e)}")
    
    def generar_html_detalles(self, orden: OrdenDB, cliente: ClienteDB, activo: ActivoDB) -> str:
        """Generar HTML con detalles de la orden"""
        # Determinar color según estado
        if orden.estado.value == EstadoOrden.EJECUTADA.value:
            estado_color = "#198754"
            estado_icon = "✅"
        elif orden.estado.value == EstadoOrden.PENDIENTE.value:
            estado_color = "#ffc107"
            estado_icon = "⏳"
        elif orden.estado.value == EstadoOrden.CANCELADA.value:
            estado_color = "#6c757d"
            estado_icon = "⏹️"
        else:  # RECHAZADA
            estado_color = "#dc3545"
            estado_icon = "❌"
        
        # Calcular montos
        precio = orden.precio or orden.precio_limite or Decimal('0.00')
        monto_operacion = precio * Decimal(orden.cantidad)
        monto_total = monto_operacion + (orden.comision_total or Decimal('0.00'))
        
        html = f"""
        <div style='font-family: Arial, sans-serif;'>
            <h3 style='color: #2c5aa0; margin-top: 0;'>{estado_icon} Orden: {orden.numero_orden}</h3>
            
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                <div>
                    <h4 style='color: #495057; margin-bottom: 5px;'>📋 Información General</h4>
                    <p><b>Estado:</b> <span style='color: {estado_color};'>{orden.estado.value}</span></p>
                    <p><b>Cliente:</b> {cliente.nombre_completo}</p>
                    <p><b>Activo:</b> {activo.nombre} ({activo.id})</p>
                    <p><b>Tipo:</b> {orden.tipo_orden.value} - {orden.tipo_operacion.value}</p>
                    <p><b>Creada:</b> {orden.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                
                <div>
                    <h4 style='color: #495057; margin-bottom: 5px;'>💰 Detalles Financieros</h4>
                    <p><b>Cantidad:</b> {orden.cantidad:,}</p>
                    <p><b>Precio:</b> ${float(precio):,.4f}</p>
                    <p><b>Monto operación:</b> ${float(monto_operacion):,.2f}</p>
                    <p><b>Comisiones:</b> ${float(orden.comision_total or 0):,.2f}</p>
                    <p><b>Total:</b> <b>${float(monto_total):,.2f}</b></p>
                </div>
            </div>
        """
        
        # Información adicional según estado
        if orden.estado.value == EstadoOrden.EJECUTADA.value and orden.fecha_ejecucion:
            html += f"""
            <div style='margin-top: 15px; padding: 10px; background-color: #e8f5e8; border-radius: 4px;'>
                <b>📈 Ejecutada:</b> {orden.fecha_ejecucion.strftime('%d/%m/%Y %H:%M')}<br>
                <b>Cantidad ejecutada:</b> {orden.cantidad_ejecutada:,} de {orden.cantidad:,}<br>
                <b>Precio promedio:</b> ${float(orden.precio_ejecucion_promedio or 0):,.4f}<br>
                <b>N° Operación BVC:</b> {orden.numero_operacion_bvc or 'No registrado'}
            </div>
            """
        elif orden.estado.value == EstadoOrden.PENDIENTE.value and orden.fecha_vencimiento:
            html += f"""
            <div style='margin-top: 15px; padding: 10px; background-color: #fff3cd; border-radius: 4px;'>
                <b>⏰ Vencimiento:</b> {orden.fecha_vencimiento.strftime('%d/%m/%Y %H:%M')}<br>
                <b>Tiempo restante:</b> {(orden.fecha_vencimiento - datetime.now()).seconds // 3600} horas<br>
                <i>Esta orden vencerá automáticamente si no es ejecutada</i>
            </div>
            """
        
        # Notas
        if orden.notas:
            html += f"""
            <div style='margin-top: 15px; padding: 10px; background-color: #e7f3ff; border-radius: 4px;'>
                <b>📝 Notas:</b><br>{orden.notas}
            </div>
            """
        
        html += "</div>"
        return html
    
    def nueva_orden(self):
        """Mostrar diálogo para nueva orden"""
        dialog = NuevaOrdenDialog(self)
        dialog.orden_creada.connect(self.on_orden_creada)
        dialog.exec()
    
    def on_orden_creada(self, orden_data: dict):
        """Manejar creación de nueva orden"""
        self.load_ordenes()
        self.status_bar.showMessage("Nueva orden creada exitosamente", 3000)
    
    def cancelar_orden(self):
        """Cancelar orden seleccionada"""
        if not self.current_orden_id:
            return
        
        # Confirmación
        reply = QMessageBox.question(
            self, "Confirmar cancelación",
            "¿Está seguro de cancelar esta orden?\n\n"
            "Los fondos bloqueados serán liberados.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            exito, mensaje = self.orden_service.cancelar_orden(self.current_orden_id)
            
            if exito:
                QMessageBox.information(self, "Éxito", "Orden cancelada exitosamente")
                self.load_ordenes()
                self.status_bar.showMessage("Orden cancelada", 3000)
                
                # Limpiar detalles
                self.current_orden_id = None
                self.cancelar_orden_action.setEnabled(False)
                self.ver_detalles_action.setEnabled(False)
                self.detalles_label.setText("📋 Seleccione una orden para ver sus detalles")
                self.detalles_label.setStyleSheet("""
                    QLabel {
                        color: #6c757d;
                        font-size: 14px;
                        font-style: italic;
                        padding: 20px;
                    }
                """)
            else:
                QMessageBox.critical(self, "Error", f"No se pudo cancelar la orden:\n\n{mensaje}")
                
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            QMessageBox.critical(self, "Error", f"Error cancelando orden:\n\n{str(e)}")
    
    def ver_detalles_orden(self):
        """Ver detalles completos de la orden"""
        if not self.current_orden_id:
            return
        
        # Ya se muestran en el panel inferior, pero podríamos mostrar un diálogo más completo
        QMessageBox.information(
            self, "Detalles de Orden",
            f"Los detalles de la orden {self.current_orden_id} se muestran en el panel inferior.\n\n"
            "Para más opciones, use el menú contextual (próximamente)."
        )
    
    def cleanup(self):
        """Limpiar recursos"""
        if hasattr(self, 'db_session') and self.db_session:
            self.db_session.close()