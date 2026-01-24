"""
Controller de Operaciones - REFACTORIZADO
Usa Service Layer para lógica de negocio.
Solo maneja navegación y coordinación de UI.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
import logging

from ..services.operaciones_service import OperacionesService
from ..repositories.orden_repository import OrdenRepository
from ..repositories.saldo_repository import SaldoRepository
from ..repositories.portafolio_repository import PortafolioRepository
from ..repositories.base_repository import BaseRepository
from ..database.models_sql import ClienteDB, CuentaBursatilDB, CuentaBancariaDB, TituloDB, BancoDB, CasaBolsaDB
from ..utils.constants import TipoOrden, EstadoOrden
from ..utils.formatters import DataFormatter

logger = logging.getLogger(__name__)


class OperacionesController(QObject):
    """
    Controller para el módulo de operaciones.
    
    Responsabilidades:
    - Conectar señales de UI
    - Navegar entre vistas del módulo
    - Coordinar llamadas a Services
    - Actualizar UI con resultados
    """
    
    # Señales para actualizar UI
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)
    
    def __init__(self, module):
        super().__init__()
        self.module = module
        
        # Acceso a las vistas
        self.dashboard = module.view_dashboard
        self.list_view = module.view_lista
        self.portafolio_view = module.view_portafolio
        
        # Services y Repositories
        from ..database.engine import get_database
        self.db_engine = get_database()
        
        self.operaciones_service = OperacionesService(self.db_engine)
        self.orden_repo = OrdenRepository(self.db_engine)
        self.saldo_repo = SaldoRepository(self.db_engine)
        self.portafolio_repo = PortafolioRepository(self.db_engine)
        
        # Repositorios adicionales para queries básicas
        self.cliente_repo = BaseRepository(self.db_engine, ClienteDB)
        self.cuenta_bursatil_repo = BaseRepository(self.db_engine, CuentaBursatilDB)
        self.cuenta_bancaria_repo = BaseRepository(self.db_engine, CuentaBancariaDB)
        self.titulo_repo = BaseRepository(self.db_engine, TituloDB)
        
        # Estado actual
        self.inversor_actual_id = None
        self.cuenta_bursatil_actual_id = None
        self.cuenta_bancaria_actual_id = None
        
        self._nombres_cache = {
            'bancos': {},      # {id: nombre}
            'casas_bolsa': {}  # {id: nombre}
        }
        
        # Cargar cache de nombres
        self._cargar_cache_nombres()
        
        self.setup_connections()
    def _cargar_cache_nombres(self):
        """Carga en cache los nombres de bancos y casas de bolsa"""
        try:
            logger.info("🔄 Cargando cache de nombres...")
            
            # Cargar bancos
            bancos_repo = BaseRepository(self.db_engine, BancoDB)
            bancos = bancos_repo.find_many(estatus=True)
            self._nombres_cache['bancos'] = {
                b['id']: b.get('nombre', f"Banco {b['id']}")
                for b in bancos
            }
            
            # Cargar casas de bolsa
            casas_repo = BaseRepository(self.db_engine, CasaBolsaDB)
            casas = casas_repo.find_many(estatus=True)
            self._nombres_cache['casas_bolsa'] = {
                c['id']: c.get('nombre', f"Casa {c['id']}")
                for c in casas
            }
            
            logger.info(f"✅ Cache cargado: "
                        f"{len(self._nombres_cache['bancos'])} bancos, "
                        f"{len(self._nombres_cache['casas_bolsa'])} casas")
            
        except Exception as e:
            logger.error(f"❌ Error cargando cache: {e}")
    
    def get_banco_nombre(self, banco_id: int) -> str:
        """Obtiene nombre de un banco desde cache"""
        return self._nombres_cache['bancos'].get(banco_id, f"Banco {banco_id}")
    
    def get_casa_bolsa_nombre(self, casa_id: int) -> str:
        """Obtiene nombre de una casa de bolsa desde cache"""
        return self._nombres_cache['casas_bolsa'].get(casa_id, f"Casa {casa_id}")
    
    # ==================== SETUP ====================
    
    def setup_connections(self):
        """Conecta las señales de las vistas"""
        # Dashboard
        self.dashboard.inversor_seleccionado.connect(self.on_inversor_seleccionado)
        self.dashboard.cuenta_bursatil_seleccionada.connect(self.on_cuenta_bursatil_seleccionada)
        self.dashboard.cuenta_bancaria_seleccionada.connect(self.on_cuenta_bancaria_seleccionada)
        self.dashboard.nueva_compra_clicked.connect(self.abrir_nueva_compra)
        self.dashboard.nueva_venta_clicked.connect(self.abrir_nueva_venta)
        self.dashboard.ver_todas_operaciones_clicked.connect(self.mostrar_lista)
        self.dashboard.ver_portafolio_clicked.connect(self.mostrar_portafolio)
        self.dashboard.actualizar_precios_clicked.connect(self.abrir_actualizar_precios)
        
        # List View
        self.list_view.orden_seleccionada.connect(self.ver_detalle_orden)
        self.list_view.nueva_orden_clicked.connect(self.abrir_nueva_orden)
        self.list_view.volver_clicked.connect(self.mostrar_dashboard)
        
        # Portafolio View
        self.portafolio_view.vender_posicion_clicked.connect(self.abrir_venta_desde_portafolio)
        self.portafolio_view.volver_clicked.connect(self.mostrar_dashboard)
    
    # ==================== NAVEGACIÓN ====================
    
    def mostrar_dashboard(self):
        """Muestra el dashboard principal"""
        self.module.setCurrentIndex(0)
        self.actualizar_dashboard()
    
    def mostrar_lista(self):
        """Muestra la lista de operaciones"""
        self.module.setCurrentIndex(1)
        self.actualizar_lista_operaciones()
    
    def mostrar_portafolio(self):
        """Muestra el portafolio"""
        self.module.setCurrentIndex(2)
        self.actualizar_portafolio()
    
    
    # ==================== MÉTODOS FORMATEADOS ====================
    
    def obtener_inversores_formateados(self) -> List[Dict]:
        """Retorna lista de inversores formateados para UI"""
        inversores = self.cliente_repo.find_many(estatus=True)
        
        return [
            {
                'id': inv['id'],
                'texto': DataFormatter.format_inversor(inv),
                'tooltip': f"{inv.get('nombre_completo')}\n"
                            f"RIF/Cédula: {inv.get('rif_cedula')}",
                'data': inv
            }
            for inv in inversores
        ]
    
    def obtener_cuentas_bancarias_formateadas(self, cliente_id: int) -> List[Dict]:
        """Retorna cuentas bancarias formateadas para UI"""
        cuentas = self.cuenta_bancaria_repo.find_many(
            cliente_id=cliente_id,
            estatus=True
        )
        
        return [
            {
                'id': cuenta['id'],
                'texto': DataFormatter.format_cuenta_bancaria(
                    cuenta,
                    self.get_banco_nombre(cuenta.get('banco_id'))
                ),
                'tooltip': DataFormatter.get_cuenta_bancaria_tooltip(
                    cuenta,
                    self.get_banco_nombre(cuenta.get('banco_id'))
                ),
                'data': cuenta,
                'banco_nombre': self.get_banco_nombre(cuenta.get('banco_id'))
            }
            for cuenta in cuentas
        ]
    
    def obtener_cuentas_bursatiles_formateadas(self, cliente_id: int) -> List[Dict]:
        """Retorna cuentas bursátiles formateadas para UI"""
        cuentas = self.cuenta_bursatil_repo.find_many(
            cliente_id=cliente_id,
            estatus=True
        )
        
        return [
            {
                'id': cuenta['id'],
                'texto': DataFormatter.format_cuenta_bursatil(
                    cuenta,
                    self.get_casa_bolsa_nombre(cuenta.get('casa_bolsa_id'))
                ),
                'tooltip': DataFormatter.get_cuenta_bursatil_tooltip(
                    cuenta,
                    self.get_casa_bolsa_nombre(cuenta.get('casa_bolsa_id'))
                ),
                'data': cuenta,
                'casa_nombre': self.get_casa_bolsa_nombre(cuenta.get('casa_bolsa_id'))
            }
            for cuenta in cuentas
        ]
    
    
    # ==================== EVENTOS DE SELECCIÓN ====================
    def on_inversor_seleccionado(self, inversor_id: int):
        """Handler cuando se selecciona un inversor"""
        self.inversor_actual_id = inversor_id
        
        # Cargar cuentas formateadas
        cuentas_bursatiles = self.obtener_cuentas_bursatiles_formateadas(inversor_id)
        cuentas_bancarias = self.obtener_cuentas_bancarias_formateadas(inversor_id)
        
        # Poblar UI
        self.dashboard.poblar_cuentas_bursatiles(cuentas_bursatiles)
        self.dashboard.poblar_cuentas_bancarias(cuentas_bancarias)
        
        # Actualizar métricas
        self.actualizar_metricas()
    
    def on_cuenta_bursatil_seleccionada(self, cuenta_id: int):
        """Handler cuando se selecciona una cuenta bursátil"""
        self.cuenta_bursatil_actual_id = cuenta_id
        self.actualizar_metricas()
    
    def on_cuenta_bancaria_seleccionada(self, cuenta_id: int):
        """Handler cuando se selecciona una cuenta bancaria"""
        self.cuenta_bancaria_actual_id = cuenta_id
        self.actualizar_metricas()
    
    # ==================== ACTUALIZAR UI ====================
    
    def actualizar_dashboard(self):
        """Actualiza todos los componentes del dashboard"""
        # Cargar inversores formateados
        inversores = self.obtener_inversores_formateados()
        self.dashboard.poblar_inversores(inversores)
        
        # Actualizar métricas
        self.actualizar_metricas()
        
        # Cargar operaciones recientes
        self.actualizar_operaciones_recientes()
    
    def actualizar_metricas(self):
        """Actualiza las métricas del dashboard"""
        if not self.inversor_actual_id:
            return
        
        try:
            # Obtener saldo disponible
            saldo_info = None
            if self.cuenta_bancaria_actual_id:
                saldo_info = self.saldo_repo.get_saldo_cuenta(self.cuenta_bancaria_actual_id)
            
            saldo_disponible = saldo_info['disponible'] if saldo_info else 0
            
            # Obtener valor del portafolio
            valor_portafolio = 0
            if self.cuenta_bursatil_actual_id:
                resumen = self.portafolio_repo.get_resumen_portafolio(self.cuenta_bursatil_actual_id)
                valor_portafolio = resumen.get('valor_mercado_total', 0)
            
            # Obtener estadísticas de órdenes
            stats = self.orden_repo.get_estadisticas_ordenes(self.inversor_actual_id)
            
            # Actualizar métricas en dashboard
            self.dashboard.actualizar_metrica_portafolio(valor_portafolio)
            self.dashboard.actualizar_metrica_pendientes(stats['pendientes'])
            self.dashboard.actualizar_metrica_saldo(saldo_disponible)
            
            # Ganancia/Pérdida (calculada del portafolio)
            if self.cuenta_bursatil_actual_id:
                resumen = self.portafolio_repo.get_resumen_portafolio(self.cuenta_bursatil_actual_id)
                gp = resumen.get('ganancia_perdida_total', 0)
                self.dashboard.actualizar_metrica_ganancia_perdida(gp)
        
        except Exception as e:
            logger.error(f"Error actualizando métricas: {e}")
            self.error_ocurrido.emit(f"Error al actualizar métricas: {str(e)}")
    
    def actualizar_operaciones_recientes(self):
        """Actualiza la tabla de operaciones recientes"""
        try:
            ordenes = self.orden_repo.get_ordenes_recientes(
                limite_dias=30,
                cliente_id=self.inversor_actual_id,
                limit=10
            )
            
            self.dashboard.actualizar_tabla_operaciones(ordenes)
        
        except Exception as e:
            logger.error(f"Error actualizando operaciones: {e}")
    
    def actualizar_lista_operaciones(self):
        """Actualiza la vista de lista completa"""
        try:
            # Obtener filtros de la vista
            filtros = self.list_view.obtener_filtros()
            
            ordenes = self.orden_repo.buscar_ordenes(
                ticker=filtros.get('ticker'),
                tipo=filtros.get('tipo'),
                estado=filtros.get('estado'),
                fecha_desde=filtros.get('fecha_desde'),
                fecha_hasta=filtros.get('fecha_hasta'),
                cliente_id=self.inversor_actual_id
            )
            
            self.list_view.poblar_tabla(ordenes)
        
        except Exception as e:
            logger.error(f"Error actualizando lista: {e}")
    
    def actualizar_portafolio(self):
        """Actualiza la vista de portafolio"""
        try:
            if not self.cuenta_bursatil_actual_id:
                return
            
            resumen = self.portafolio_repo.get_resumen_portafolio(self.cuenta_bursatil_actual_id)
            
            # Actualizar cards de resumen
            self.portafolio_view.actualizar_resumen(resumen)
            
            # Actualizar tabla de posiciones
            self.portafolio_view.poblar_tabla(resumen.get('posiciones', []))
        
        except Exception as e:
            logger.error(f"Error actualizando portafolio: {e}")
    
    # ==================== DIÁLOGOS ====================
    
    def abrir_nueva_compra(self):
        """Abre el diálogo de nueva compra"""
        from ..ui.dialogs.nueva_compra_dialog import NuevaCompraDialog
        
        if not self._validar_selecciones():
            return
        
        dialog = NuevaCompraDialog(
            parent=self.module,
            service=self.operaciones_service,
            inversor_id=self.inversor_actual_id,
        )
        
        dialog.orden_creada.connect(self.on_orden_creada)
        dialog.exec()
    
    def abrir_nueva_venta(self):
        """Abre el diálogo de nueva venta"""
        from ..ui.dialogs.nueva_venta_dialog import NuevaVentaDialog
        
        if not self._validar_selecciones():
            return
        
        # Verificar que hay posiciones
        portafolio = self.portafolio_repo.get_portafolio_cuenta(self.cuenta_bursatil_actual_id)
        
        if not portafolio:
            QMessageBox.information(
                self.module,
                "Sin Posiciones",
                "No hay posiciones disponibles para vender en esta cuenta."
            )
            return
        
        dialog = NuevaVentaDialog(
            parent=self.module,
            service=self.operaciones_service,
            cliente_id=self.inversor_actual_id,
            cuenta_bursatil_id=self.cuenta_bursatil_actual_id,
            cuenta_bancaria_id=self.cuenta_bancaria_actual_id,
            portafolio=portafolio
        )
        
        dialog.orden_creada.connect(self.on_orden_creada)
        dialog.exec()
    
    def abrir_nueva_orden(self):
        """Abre selector de tipo de orden"""
        # Mostrar diálogo para elegir compra o venta
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        
        dialog = QDialog(self.module)
        dialog.setWindowTitle("Nueva Orden")
        dialog.resize(300, 150)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("¿Qué tipo de orden desea crear?")
        layout.addWidget(label)
        
        buttons_layout = QHBoxLayout()
        
        btn_compra = QPushButton("📈 Compra")
        btn_compra.clicked.connect(lambda: (dialog.accept(), self.abrir_nueva_compra()))
        
        btn_venta = QPushButton("📉 Venta")
        btn_venta.clicked.connect(lambda: (dialog.accept(), self.abrir_nueva_venta()))
        
        buttons_layout.addWidget(btn_compra)
        buttons_layout.addWidget(btn_venta)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec()
    
    def abrir_venta_desde_portafolio(self, portafolio_item_id: int):
        """Abre diálogo de venta desde una posición específica"""
        from ..ui.dialogs.nueva_venta_dialog import NuevaVentaDialog
        
        posicion = self.portafolio_repo.get_by_id(portafolio_item_id)
        
        if not posicion:
            return
        
        dialog = NuevaVentaDialog(
            parent=self.module,
            service=self.operaciones_service,
            cliente_id=self.inversor_actual_id,
            cuenta_bursatil_id=self.cuenta_bursatil_actual_id,
            cuenta_bancaria_id=self.cuenta_bancaria_actual_id,
            posicion_preseleccionada=posicion
        )
        
        dialog.orden_creada.connect(self.on_orden_creada)
        dialog.exec()
    
    def abrir_actualizar_precios(self):
        """Abre el diálogo de actualización de precios"""
        from ..ui.dialogs.actualizar_precios_dialog import ActualizarPreciosDialog
        
        dialog = ActualizarPreciosDialog(
            parent=self.module,
            controller=self
        )
        
        dialog.precios_actualizados.connect(self.on_precios_actualizados)
        dialog.exec()
    
    def ver_detalle_orden(self, orden_id: int):
        """Muestra el detalle de una orden"""
        # TODO: Implementar DetalleOrdenDialog
        orden = self.orden_repo.get_orden_completa(orden_id)
        
        if orden:
            QMessageBox.information(
                self.module,
                "Detalle de Orden",
                f"Orden #{orden_id}\n"
                f"Ticker: {orden['ticker']}\n"
                f"Tipo: {orden['tipo']}\n"
                f"Cantidad: {orden['cantidad']}\n"
                f"Estado: {orden['estado']}"
            )
    
    # ==================== CALLBACKS ====================
    
    def on_orden_creada(self, orden_id: int):
        """Callback cuando se crea una orden"""
        logger.info(f"Orden creada: ID={orden_id}")
        
        # Actualizar todas las vistas
        self.actualizar_metricas()
        self.actualizar_operaciones_recientes()
        
        # Emitir señal
        self.datos_actualizados.emit()
    
    def on_precios_actualizados(self, resultados: list):
        """Callback cuando se actualizan precios"""
        logger.info(f"{len(resultados)} precios actualizados")
        
        # Refrescar portafolio (los valores cambiaron)
        self.actualizar_metricas()
        
        if self.module.currentIndex() == 2:  # Si está en portafolio
            self.actualizar_portafolio()
    
    # ==================== MÉTODOS PARA DIÁLOGOS ====================
    
    def obtener_inversores_activos(self):
        """Retorna lista de inversores activos"""
        return self.cliente_repo.find_many(estatus=True)
    
    def obtener_cuentas_bursatiles_cliente(self, cliente_id: int):
        """Retorna cuentas bursátiles de un cliente"""
        return self.obtener_cuentas_bursatiles_formateadas(cliente_id)
    
    def obtener_cuentas_bancarias_cliente(self, cliente_id: int):
        """Retorna cuentas bancarias de un cliente"""
        return self.obtener_cuentas_bancarias_formateadas(cliente_id)
    
    def obtener_saldo_disponible(self, cuenta_bancaria_id: int) -> float:
        """Retorna saldo disponible de una cuenta"""
        saldo = self.saldo_repo.get_saldo_cuenta(cuenta_bancaria_id)
        return saldo['disponible'] if saldo else 0
    
    def buscar_activo_por_ticker(self, ticker: str):
        """Busca un activo por ticker"""
        return self.titulo_repo.find_one(ticker=ticker.upper(), estatus=True)
    
    def obtener_portafolio_cuenta(self, cuenta_bursatil_id: int):
        """Obtiene portafolio de una cuenta"""
        return self.portafolio_repo.get_portafolio_cuenta(cuenta_bursatil_id)
    
    def obtener_todos_tickers_activos(self):
        """Retorna todos los tickers activos"""
        return self.titulo_repo.find_many(estatus=True)
    
    def actualizar_precios_masivo(self, actualizados: list) -> bool:
        """Actualiza precios de múltiples tickers"""
        try:
            updates = [
                {'id': item['ticker_id'], 'precio_actual': item['precio_nuevo']}
                for item in actualizados
            ]
            
            count = self.titulo_repo.bulk_update(updates)
            return count > 0
        
        except Exception as e:
            logger.error(f"Error en actualización masiva: {e}")
            return False
    
    # ==================== UTILIDADES ====================
    
    def _validar_selecciones(self) -> bool:
        """Valida que estén seleccionados inversor y cuentas"""
        if not self.inversor_actual_id:
            QMessageBox.warning(
                self.module,
                "Selección Requerida",
                "Debe seleccionar un inversor"
            )
            return False
        
        if not self.cuenta_bursatil_actual_id:
            QMessageBox.warning(
                self.module,
                "Selección Requerida",
                "Debe seleccionar una cuenta bursátil"
            )
            return False
        
        if not self.cuenta_bancaria_actual_id:
            QMessageBox.warning(
                self.module,
                "Selección Requerida",
                "Debe seleccionar una cuenta bancaria"
            )
            return False
        
        return True