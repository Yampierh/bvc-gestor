import logging
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from ..database.models_sql import (
    OrdenDB, CuentaDB, ActivoDB, PortafolioItemDB, ClienteDB
)
from ..utils.constants import EstadoOrden, TipoOrden, TipoOperacion

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
    """
    Servicio centralizado para la gestión de órdenes bursátiles.
    Maneja validaciones, cálculo de comisiones y bloqueo de fondos.
    """

    # Tarifas BVC (Ejemplo aproximado, esto debería venir de una tabla de configuración)
    TARIFA_CASA_BOLSA = Decimal("0.0090")  # 0.90%
    TARIFA_BOLSA = Decimal("0.0010")       # 0.10%
    TARIFA_CAJA = Decimal("0.0005")        # 0.05%
    IVA = Decimal("0.16")                  # 16%

    def __init__(self, db: Session):
        self.db = db

    def calcular_comisiones(self, monto_bruto: Decimal) -> dict:
        """
        Calcula el desglose de comisiones para una operación.
        """
        comision_base = monto_bruto * (self.TARIFA_CASA_BOLSA + self.TARIFA_BOLSA + self.TARIFA_CAJA)
        # En Venezuela suele haber un mínimo, por ahora usaremos el % simple
        iva_comision = comision_base * self.IVA
        total_comision = comision_base + iva_comision

        return {
            "base": round(comision_base, 2),
            "iva": round(iva_comision, 2),
            "total": round(total_comision, 2)
        }

    def crear_orden(
        self, 
        cliente_id: int, 
        cuenta_id: int, 
        ticker: str, 
        tipo_orden: TipoOrden, 
        cantidad: int, 
        precio: Decimal
    ) -> OrdenDB:
        """
        Crea una orden nueva, valida fondos y bloquea el dinero/acciones.
        """
        logger.info(f"Iniciando creación de orden: {tipo_orden} {cantidad} {ticker} @ {precio}")

        # 1. Validaciones básicas
        cuenta = self.db.get(CuentaDB, cuenta_id)
        if not cuenta or cuenta.cliente_id != cliente_id:
            raise ValueError("Cuenta inválida o no pertenece al cliente")
        
        activo = self.db.get(ActivoDB, ticker)
        if not activo:
            raise ActivoNoEncontradoError(f"El activo {ticker} no existe")

        monto_bruto = Decimal(cantidad) * precio
        comisiones = self.calcular_comisiones(monto_bruto)
        monto_total_operacion = monto_bruto + comisiones["total"]

        # 2. Lógica de COMPRA
        if tipo_orden == TipoOrden.COMPRA:
            # Verificar disponibilidad (Saldo Disponible >= Monto + Comisiones)
            if cuenta.saldo_disponible_bs < monto_total_operacion:
                deficit = monto_total_operacion - cuenta.saldo_disponible_bs
                raise SaldoInsuficienteError(
                    f"Saldo insuficiente. Requerido: {monto_total_operacion}, Disponible: {cuenta.saldo_disponible_bs}"
                )
            
            # BLOQUEO DE FONDOS (Movimiento contable interno)
            cuenta.saldo_disponible_bs -= monto_total_operacion
            cuenta.saldo_bloqueado_bs += monto_total_operacion
            logger.info(f"Fondos bloqueados para compra: {monto_total_operacion} Bs")

        # 3. Lógica de VENTA
        elif tipo_orden == TipoOrden.VENTA:
            # Buscar si tiene las acciones en portafolio
            stmt = select(PortafolioItemDB).where(
                and_(
                    PortafolioItemDB.cuenta_id == cuenta_id,
                    PortafolioItemDB.activo_id == ticker
                )
            )
            item_portafolio = self.db.execute(stmt).scalar_one_or_none()

            # Necesitamos considerar acciones que ya están comprometidas en otras órdenes de venta abiertas
            # (Esta lógica avanzada la podemos refinar luego, por ahora validamos saldo total)
            if not item_portafolio or item_portafolio.cantidad < cantidad:
                cantidad_actual = item_portafolio.cantidad if item_portafolio else 0
                raise PosicionInsuficienteError(
                    f"No tienes suficientes acciones. Requerido: {cantidad}, Tienes: {cantidad_actual}"
                )
            
            # En venta, no bloqueamos dinero, bloqueamos "acciones" (lógica futura)
            # Pero las comisiones se descontarán del resultado final (Neto a cobrar)

        # 4. Crear el objeto OrdenDB
        nueva_orden = OrdenDB(
            numero_orden=self._generar_numero_orden(),
            cliente_id=cliente_id,
            cuenta_id=cuenta_id,
            activo_id=ticker,
            tipo_orden=tipo_orden,
            tipo_operacion=TipoOperacion.LIMITADA, # Por defecto Limitada
            cantidad=cantidad,
            precio_limite=precio,
            comision_base=comisiones["base"],
            iva_comision=comisiones["iva"],
            estado=EstadoOrden.PENDIENTE,
            # Guardamos la tasa del BCV solo si aplica (aquí asumimos 1 para Bs)
            tasa_bcv_snapshot=Decimal("1.0000") 
        )

        self.db.add(nueva_orden)
        
        # 5. Commit de la transacción (Orden + Actualización de Saldo)
        try:
            self.db.commit()
            self.db.refresh(nueva_orden)
            logger.info(f"Orden creada exitosamente: ID {nueva_orden.id}")
            return nueva_orden
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al guardar la orden: {e}")
            raise e

    def _generar_numero_orden(self) -> str:
        """Genera un ID único legible, ej: OR-20231027-0001"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # En producción usaríamos una secuencia o UUID
        return f"ORD-{timestamp}"