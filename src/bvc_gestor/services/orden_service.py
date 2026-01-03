# src/bvc_gestor/services/orden_service.py
from decimal import Decimal
import logging
from sqlalchemy.orm import Session
from ..database.models_sql import OrdenDB, CuentaDB
from ..database.repositories import RepositoryFactory, CuentaRepository
from ..utils.calculos_financieros import calcular_comision_bvc, calcular_monto_total_orden
from ..utils.constants import EstadoOrden, Moneda, TipoOrden, TipoOperacion
from ..utils.calculos_financieros import simular_ejecucion_orden

# Configuración de Logging
logger = logging.getLogger(__name__)

class SaldoInsuficienteError(Exception):
    """Excepción para fondos insuficientes"""
    pass

class ActivoNoEncontradoError(Exception):
    """Excepción cuando el activo no existe"""
    pass

class PosicionInsuficienteError(Exception):
    """Excepción cuando se intenta vender más de lo que se tiene"""
    pass

class OrdenService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def ejecutar_orden_compra(self, cliente_id: int, cuenta_id: int, activo_id: str, cantidad: int, precio: Decimal):
        """
        Crea una orden de compra validando saldos y bloqueando fondos.
        """
        try:
            # 1. Obtener la cuenta (usando tu repositorio)
            cuenta_repo = RepositoryFactory.get_repository(self.db, 'cuenta')
            cuenta = cuenta_repo.get_by_id(cuenta_id)
            
            if not cuenta or cuenta.cliente_id != cliente_id:
                raise ValueError("Cuenta no válida o no pertenece al cliente.")

            # 2. Calcular costos reales usando tus utilidades
            # Esto desglosa comisión base e IVA automáticamente
            costos = calcular_comision_bvc(Decimal(cantidad) * precio)
            monto_total = calcular_monto_total_orden(Decimal(cantidad), precio, costos['comision_total'])

            # 3. Validar Disponibilidad
            if cuenta.saldo_disponible_bs < monto_total:
                raise ValueError(f"Saldo insuficiente. Necesitas {monto_total} Bs (incluye comisiones).")

            # 4. TRANSACCIÓN ATÓMICA: Bloqueo de fondos
            # Restamos de disponible y sumamos a bloqueado
            cuenta.saldo_disponible_bs -= monto_total
            cuenta.saldo_bloqueado_bs += monto_total

            # 5. Crear la Orden
            nueva_orden = OrdenDB(
                cliente_id=cliente_id,
                cuenta_id=cuenta_id,
                activo_id=activo_id,
                tipo_orden=TipoOrden.COMPRA,
                tipo_operacion=TipoOperacion.MERCADO,
                cantidad=cantidad,
                precio_limite=precio,
                comision_base=costos['comision_base'],
                iva_comision=costos['iva'],
                estado=EstadoOrden.PENDIENTE,
                numero_orden=self.generar_numero_orden(),
                cantidad_ejecutada=0,
                tasa_bcv_snapshot=Decimal("36.50")
            )

            self.db.add(nueva_orden)
            
            # Guardamos todo: El cambio de saldo y la nueva orden
            self.db.commit()
            logger.info(f"Orden {nueva_orden.numero_orden} creada y fondos bloqueados: {monto_total} Bs")
            return nueva_orden

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al procesar orden de compra: {e}")
            raise e

    def generar_numero_orden(self):
        import uuid
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    def procesar_ordenes_pendientes(self):
        """
        Escanea órdenes pendientes y simula su ejecución en el mercado.
        """
        orden_repo = RepositoryFactory.get_repository(self.db, 'orden')
        portafolio_repo = RepositoryFactory.get_repository(self.db, 'portafolio')
        cuenta_repo = RepositoryFactory.get_repository(self.db, 'cuenta')
        
        # 1. Buscar todas las pendientes (esto es lo que haría un 'bot' de mercado)
        pendientes = self.db.query(OrdenDB).filter_by(estado=EstadoOrden.PENDIENTE).all()
        
        ejecutadas = 0
        for orden in pendientes:
            # 2. Simular si se ejecuta (usando tu lógica de probabilidad)
            # Para la prueba, simulamos un precio de mercado igual al límite
            resultado = simular_ejecucion_orden(
                cantidad=orden.cantidad,
                precio_solicitado=orden.precio_limite,
                precio_mercado=orden.precio_limite,
                tipo_orden=orden.tipo_orden.value
            )

            if resultado['probabilidad_ejecucion'] >= 0.5: # Si hay suerte...
                try:
                    # A. Marcar orden como EJECUTADA
                    orden.estado = EstadoOrden.EJECUTADA
                    orden.precio_ejecucion_promedio = resultado['precio_ejecucion']
                    orden.cantidad_ejecutada = orden.cantidad
                    
                    # B. Confirmar el gasto en la cuenta
                    # El dinero ya estaba bloqueado, ahora lo "gastamos" definitivamente
                    cuenta = cuenta_repo.get_by_id(orden.cuenta_id)
                    monto_total = orden.cantidad * orden.precio_limite + orden.comision_base + orden.iva_comision
                    cuenta.saldo_bloqueado_bs -= monto_total
                    # (El saldo disponible ya se restó al crear la orden)

                    # C. Entregar las acciones al Portafolio
                    portafolio_repo.actualizar_o_crear_posicion(
                        orden.cliente_id, 
                        orden.activo_id, 
                        orden.cantidad, 
                        float(orden.precio_limite)
                    )
                    
                    self.db.commit()
                    ejecutadas += 1
                    logger.info(f"✨ Orden {orden.numero_orden} EJECUTADA exitosamente.")
                except Exception as e:
                    self.db.rollback()
                    logger.error(f"Error ejecutando orden {orden.id}: {e}")
        
        return ejecutadas