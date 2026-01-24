"""
Service de Operaciones - Lógica de negocio para compra/venta.
Maneja validaciones, cálculos y transacciones complejas.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import logging

from ..database.models_sql import (
    OrdenDB, TransaccionDB, PortafolioItemDB, SaldoDB, 
    MovimientoDB, OrdenMovimientoDB
)
from ..utils.constants import TipoOrden, EstadoOrden, TipoMovimiento
from ..repositories.orden_repository import OrdenRepository
from ..repositories.saldo_repository import SaldoRepository
from ..repositories.portafolio_repository import PortafolioRepository

logger = logging.getLogger(__name__)


class OperacionesService:
    """
    Service para operaciones de compra/venta.
    Centraliza toda la lógica de negocio.
    """
    
    def __init__(self, db_engine):
        self.db_engine = db_engine
        
        # Repositorios
        self.orden_repo = OrdenRepository(db_engine)
        self.saldo_repo = SaldoRepository(db_engine)
        self.portafolio_repo = PortafolioRepository(db_engine)
        
        # Configuración de comisiones (puede venir de config)
        self.config_comisiones = {
            'casa_bolsa_compra': 0.005,  # 0.5%
            'casa_bolsa_venta': 0.005,
            'cnv': 0.001,  # 0.1%
            'iva': 0.16   # 16%
        }
    
    # ==================== CREAR ORDEN DE COMPRA ====================
    
    def crear_orden_compra(self, datos_orden: Dict) -> Tuple[bool, Optional[int], str]:
        """
        Crea una orden de compra con todas las validaciones.
        
        Args:
            datos_orden: {
                'cliente_id': int,
                'cuenta_bursatil_id': int,
                'cuenta_bancaria_id': int,
                'titulo_id': int,
                'cantidad': int,
                'precio_limite': Decimal,
                'tipo': TipoOrden,
                'observaciones': str (opcional)
            }
        
        Returns:
            (exito: bool, orden_id: int | None, mensaje: str)
        """
        try:
            # 1. VALIDAR DATOS DE ENTRADA
            validacion = self._validar_datos_compra(datos_orden)
            if not validacion['valido']:
                return False, None, validacion['mensaje']
            
            # 2. CALCULAR MONTOS
            cantidad = datos_orden['cantidad']
            precio = Decimal(str(datos_orden['precio_limite']))
            
            monto_base = cantidad * precio
            comisiones = self.calcular_comisiones_compra(monto_base)
            monto_total = monto_base + comisiones['total']
            
            # 3. VERIFICAR SALDO DISPONIBLE
            saldo_info = self.saldo_repo.get_saldo_cuenta(
                datos_orden['cuenta_bancaria_id']
            )
            
            saldo_disponible = saldo_info.get('disponible', 0) if saldo_info else 0
            
            # Determinar estado inicial
            if saldo_disponible >= monto_total:
                estado_inicial = EstadoOrden.PENDIENTE
                bloquear_fondos = True
            else:
                estado_inicial = EstadoOrden.ESPERANDO_FONDOS
                bloquear_fondos = False
            
            # 4. CREAR ORDEN EN TRANSACCIÓN
            def _crear_orden_tx(session):
                # Crear orden
                orden = OrdenDB(
                    cuenta_bursatil_id=datos_orden['cuenta_bursatil_id'],
                    cuenta_bancaria_id=datos_orden['cuenta_bancaria_id'],
                    titulo_id=datos_orden['titulo_id'],
                    tipo=datos_orden['tipo'].value,
                    cantidad=cantidad,
                    precio_limite=precio,
                    estado=estado_inicial.value,
                    fecha_orden=datetime.now(),
                    comision_estimada=comisiones['total'],
                    monto_total_estimado=monto_total,
                    observaciones=datos_orden.get('observaciones')
                )
                
                session.add(orden)
                session.flush()  # Para obtener el ID
                
                # Bloquear fondos si hay saldo suficiente
                if bloquear_fondos:
                    saldo = session.query(SaldoDB).filter_by(
                        cuenta_bancaria_id=datos_orden['cuenta_bancaria_id']
                    ).first()
                    
                    if saldo:
                        saldo.disponible -= monto_total
                        saldo.bloqueado += monto_total
                        logger.info(f"💰 Fondos bloqueados: Bs. {monto_total:,.2f}")
                
                return orden.id
            
            orden_id = self.orden_repo.execute_in_transaction(_crear_orden_tx)
            
            # 5. MENSAJE DE ÉXITO
            if estado_inicial == EstadoOrden.PENDIENTE:
                mensaje = (
                    f"✅ Orden de compra creada exitosamente.\n"
                    f"Fondos bloqueados: Bs. {monto_total:,.2f}\n"
                    f"Estado: PENDIENTE"
                )
            else:
                mensaje = (
                    f"⚠️ Orden creada en estado ESPERANDO_FONDOS.\n"
                    f"Saldo disponible: Bs. {saldo_disponible:,.2f}\n"
                    f"Requerido: Bs. {monto_total:,.2f}\n"
                    f"Faltante: Bs. {(monto_total - saldo_disponible):,.2f}"
                )
            
            logger.info(f"✅ Orden compra creada: ID={orden_id}, Estado={estado_inicial.value}")
            return True, orden_id, mensaje
        
        except Exception as e:
            logger.error(f"Error creando orden de compra: {e}")
            return False, None, f"Error al crear orden: {str(e)}"
    
    # ==================== CREAR ORDEN DE VENTA ====================
    
    def crear_orden_venta(self, datos_orden: Dict) -> Tuple[bool, Optional[int], str]:
        """
        Crea una orden de venta con validación de posiciones.
        
        Args:
            datos_orden: {
                'cliente_id': int,
                'cuenta_bursatil_id': int,
                'cuenta_bancaria_id': int,
                'portafolio_item_id': int,
                'cantidad': int,
                'precio_limite': Decimal,
                'tipo': TipoOrden,
                'observaciones': str (opcional)
            }
        
        Returns:
            (exito: bool, orden_id: int | None, mensaje: str)
        """
        try:
            # 1. VALIDAR POSICIÓN DISPONIBLE
            posicion = self.portafolio_repo.get_by_id(datos_orden['portafolio_item_id'])
            
            if not posicion:
                return False, None, "Posición no encontrada"
            
            cantidad_vender = datos_orden['cantidad']
            cantidad_disponible = posicion['cantidad_disponible']
            
            if cantidad_vender > cantidad_disponible:
                return False, None, (
                    f"Cantidad insuficiente. Disponible: {cantidad_disponible}, "
                    f"Solicitado: {cantidad_vender}"
                )
            
            # 2. CALCULAR MONTOS Y G/P
            precio_venta = Decimal(str(datos_orden['precio_limite']))
            monto_venta = cantidad_vender * precio_venta
            
            comisiones = self.calcular_comisiones_venta(monto_venta)
            monto_neto = monto_venta - comisiones['total']
            
            # Calcular ganancia/pérdida
            precio_costo_promedio = Decimal(str(posicion['costo_promedio']))
            costo_total = cantidad_vender * precio_costo_promedio
            ganancia_perdida = monto_neto - costo_total
            
            # 3. CREAR ORDEN EN TRANSACCIÓN
            def _crear_orden_venta_tx(session):
                # Crear orden
                orden = OrdenDB(
                    cuenta_bursatil_id=datos_orden['cuenta_bursatil_id'],
                    cuenta_bancaria_id=datos_orden['cuenta_bancaria_id'],
                    titulo_id=posicion['titulo_id'],
                    tipo=TipoOrden.VENTA.value,
                    cantidad=cantidad_vender,
                    precio_limite=precio_venta,
                    estado=EstadoOrden.PENDIENTE.value,
                    fecha_orden=datetime.now(),
                    comision_estimada=comisiones['total'],
                    monto_total_estimado=monto_neto,
                    observaciones=datos_orden.get('observaciones')
                )
                
                session.add(orden)
                session.flush()
                
                # Bloquear cantidad en portafolio
                item = session.query(PortafolioItemDB).filter_by(
                    id=datos_orden['portafolio_item_id']
                ).first()
                
                if item:
                    item.cantidad_disponible -= cantidad_vender
                    item.cantidad_bloqueada += cantidad_vender
                    logger.info(f"🔒 Bloqueadas {cantidad_vender} acciones de {posicion['ticker']}")
                
                return orden.id
            
            orden_id = self.orden_repo.execute_in_transaction(_crear_orden_venta_tx)
            
            # 4. MENSAJE DE ÉXITO
            gp_texto = "ganancia" if ganancia_perdida >= 0 else "pérdida"
            mensaje = (
                f"✅ Orden de venta creada exitosamente.\n"
                f"Cantidad: {cantidad_vender} acciones\n"
                f"Monto neto estimado: Bs. {monto_neto:,.2f}\n"
                f"{gp_texto.capitalize()} estimada: Bs. {abs(ganancia_perdida):,.2f}"
            )
            
            logger.info(f"✅ Orden venta creada: ID={orden_id}")
            return True, orden_id, mensaje
        
        except Exception as e:
            logger.error(f"Error creando orden de venta: {e}")
            return False, None, f"Error al crear orden: {str(e)}"
    
    # ==================== EJECUTAR ORDEN ====================
    
    def ejecutar_orden(self, orden_id: int, 
                      precio_ejecucion: Decimal,
                      fecha_ejecucion: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Ejecuta una orden pendiente.
        Actualiza saldos, portafolio y crea transacción.
        """
        try:
            if fecha_ejecucion is None:
                fecha_ejecucion = datetime.now()
            
            # Obtener orden completa
            orden = self.orden_repo.get_orden_completa(orden_id)
            
            if not orden:
                return False, "Orden no encontrada"
            
            if orden['estado'] != EstadoOrden.PENDIENTE.value:
                return False, f"Orden en estado {orden['estado']}, no se puede ejecutar"
            
            # Ejecutar según tipo
            def _ejecutar_tx(session):
                orden_db = session.query(OrdenDB).filter_by(id=orden_id).first()
                
                if orden['tipo'] == TipoOrden.COMPRA.value:
                    return self._ejecutar_compra_tx(
                        session, orden_db, precio_ejecucion, fecha_ejecucion
                    )
                else:
                    return self._ejecutar_venta_tx(
                        session, orden_db, precio_ejecucion, fecha_ejecucion
                    )
            
            self.orden_repo.execute_in_transaction(_ejecutar_tx)
            
            logger.info(f"✅ Orden {orden_id} ejecutada exitosamente")
            return True, "Orden ejecutada exitosamente"
        
        except Exception as e:
            logger.error(f"Error ejecutando orden: {e}")
            return False, f"Error: {str(e)}"
    
    def _ejecutar_compra_tx(self, session, orden: OrdenDB, 
                           precio_ejecucion: Decimal, 
                           fecha_ejecucion: datetime):
        """Ejecuta una compra dentro de transacción"""
        cantidad = orden.cantidad
        monto_acciones = cantidad * precio_ejecucion
        comisiones = self.calcular_comisiones_compra(monto_acciones)
        monto_total = monto_acciones + comisiones['total']
        
        # 1. Crear transacción
        transaccion = TransaccionDB(
            orden_id=orden.id,
            cantidad=cantidad,
            precio_ejecucion=precio_ejecucion,
            comision_casa_bolsa=comisiones['casa_bolsa'],
            comision_cnv=comisiones['cnv'],
            iva=comisiones['iva'],
            monto_total=monto_total,
            fecha_ejecucion=fecha_ejecucion
        )
        session.add(transaccion)
        
        # 2. Actualizar orden
        orden.estado = EstadoOrden.EJECUTADA.value
        orden.fecha_ejecucion = fecha_ejecucion
        orden.precio_ejecucion = precio_ejecucion
        
        # 3. Actualizar saldo (desbloquear y ajustar)
        saldo = session.query(SaldoDB).filter_by(
            cuenta_bancaria_id=orden.cuenta_bancaria_id
        ).first()
        
        if saldo:
            # Desbloquear monto estimado
            saldo.bloqueado -= orden.monto_total_estimado
            
            # Ajustar si el monto real es diferente
            diferencia = orden.monto_total_estimado - monto_total
            if diferencia != 0:
                saldo.disponible += diferencia
        
        # 4. Agregar al portafolio
        portafolio_item = session.query(PortafolioItemDB).filter_by(
            cuenta_bursatil_id=orden.cuenta_bursatil_id,
            titulo_id=orden.titulo_id
        ).first()
        
        if portafolio_item:
            # Actualizar posición existente (promedio ponderado)
            cantidad_anterior = portafolio_item.cantidad_total
            costo_anterior = portafolio_item.costo_promedio
            
            costo_total_anterior = cantidad_anterior * costo_anterior
            costo_total_nuevo = cantidad * precio_ejecucion
            
            portafolio_item.cantidad_total += cantidad
            portafolio_item.cantidad_disponible += cantidad
            portafolio_item.costo_promedio = (
                (costo_total_anterior + costo_total_nuevo) / 
                portafolio_item.cantidad_total
            )
        else:
            # Crear nueva posición
            portafolio_item = PortafolioItemDB(
                cuenta_bursatil_id=orden.cuenta_bursatil_id,
                titulo_id=orden.titulo_id,
                cantidad_total=cantidad,
                cantidad_disponible=cantidad,
                cantidad_bloqueada=0,
                costo_promedio=precio_ejecucion,
                fecha_primera_compra=fecha_ejecucion
            )
            session.add(portafolio_item)
        
        logger.info(f"💼 Portafolio actualizado: +{cantidad} acciones")
    
    def _ejecutar_venta_tx(self, session, orden: OrdenDB,
                          precio_ejecucion: Decimal,
                          fecha_ejecucion: datetime):
        """Ejecuta una venta dentro de transacción"""
        cantidad = orden.cantidad
        monto_venta = cantidad * precio_ejecucion
        comisiones = self.calcular_comisiones_venta(monto_venta)
        monto_neto = monto_venta - comisiones['total']
        
        # 1. Crear transacción
        transaccion = TransaccionDB(
            orden_id=orden.id,
            cantidad=cantidad,
            precio_ejecucion=precio_ejecucion,
            comision_casa_bolsa=comisiones['casa_bolsa'],
            comision_cnv=comisiones['cnv'],
            iva=comisiones['iva'],
            monto_total=monto_neto,
            fecha_ejecucion=fecha_ejecucion
        )
        session.add(transaccion)
        
        # 2. Actualizar orden
        orden.estado = EstadoOrden.EJECUTADA.value
        orden.fecha_ejecucion = fecha_ejecucion
        orden.precio_ejecucion = precio_ejecucion
        
        # 3. Actualizar saldo (agregar monto neto)
        saldo = session.query(SaldoDB).filter_by(
            cuenta_bancaria_id=orden.cuenta_bancaria_id
        ).first()
        
        if saldo:
            saldo.disponible += monto_neto
        else:
            # Crear saldo si no existe
            saldo = SaldoDB(
                cuenta_bancaria_id=orden.cuenta_bancaria_id,
                disponible=monto_neto,
                bloqueado=0,
                en_transito=0
            )
            session.add(saldo)
        
        # 4. Actualizar portafolio
        portafolio_item = session.query(PortafolioItemDB).filter_by(
            cuenta_bursatil_id=orden.cuenta_bursatil_id,
            titulo_id=orden.titulo_id
        ).first()
        
        if portafolio_item:
            # Desbloquear y reducir cantidad
            portafolio_item.cantidad_bloqueada -= cantidad
            portafolio_item.cantidad_total -= cantidad
            
            # Si se vendió todo, eliminar item
            if portafolio_item.cantidad_total == 0:
                session.delete(portafolio_item)
                logger.info(f"🗑️ Posición eliminada (vendida completamente)")
        
        logger.info(f"💰 Venta ejecutada: +Bs. {monto_neto:,.2f} al saldo")
    
    # ==================== CANCELAR ORDEN ====================
    
    def cancelar_orden(self, orden_id: int, motivo: str = "") -> Tuple[bool, str]:
        """Cancela una orden y libera recursos bloqueados"""
        try:
            orden = self.orden_repo.get_by_id(orden_id)
            
            if not orden:
                return False, "Orden no encontrada"
            
            if orden['estado'] not in [
                EstadoOrden.PENDIENTE.value,
                EstadoOrden.ESPERANDO_FONDOS.value
            ]:
                return False, f"No se puede cancelar orden en estado {orden['estado']}"
            
            def _cancelar_tx(session):
                orden_db = session.query(OrdenDB).filter_by(id=orden_id).first()
                orden_db.estado = EstadoOrden.CANCELADA.value
                
                # Liberar fondos bloqueados (si es compra)
                if orden['tipo'] == TipoOrden.COMPRA.value and orden['estado'] == EstadoOrden.PENDIENTE.value:
                    saldo = session.query(SaldoDB).filter_by(
                        cuenta_bancaria_id=orden['cuenta_bancaria_id']
                    ).first()
                    
                    if saldo:
                        saldo.bloqueado -= orden['monto_total_estimado']
                        saldo.disponible += orden['monto_total_estimado']
                        logger.info(f"💰 Fondos liberados: Bs. {orden['monto_total_estimado']:,.2f}")
                
                # Liberar acciones bloqueadas (si es venta)
                if orden['tipo'] == TipoOrden.VENTA.value:
                    item = session.query(PortafolioItemDB).filter_by(
                        cuenta_bursatil_id=orden['cuenta_bursatil_id'],
                        titulo_id=orden['titulo_id']
                    ).first()
                    
                    if item:
                        item.cantidad_bloqueada -= orden['cantidad']
                        item.cantidad_disponible += orden['cantidad']
                        logger.info(f"🔓 Acciones liberadas: {orden['cantidad']}")
                
                # Agregar motivo
                if motivo:
                    if orden_db.observaciones:
                        orden_db.observaciones += f"\n[CANCELADA] {motivo}"
                    else:
                        orden_db.observaciones = f"[CANCELADA] {motivo}"
            
            self.orden_repo.execute_in_transaction(_cancelar_tx)
            
            logger.info(f"✅ Orden {orden_id} cancelada: {motivo}")
            return True, "Orden cancelada exitosamente"
        
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            return False, f"Error: {str(e)}"
    
    # ==================== CÁLCULO DE COMISIONES ====================
    
    def calcular_comisiones_compra(self, monto_base: Decimal) -> Dict:
        """Calcula todas las comisiones de una compra"""
        monto = Decimal(str(monto_base))
        
        comision_casa = monto * Decimal(str(self.config_comisiones['casa_bolsa_compra']))
        comision_cnv = monto * Decimal(str(self.config_comisiones['cnv']))
        
        subtotal_comisiones = comision_casa + comision_cnv
        iva = subtotal_comisiones * Decimal(str(self.config_comisiones['iva']))
        
        total = comision_casa + comision_cnv + iva
        
        return {
            'casa_bolsa': float(comision_casa),
            'cnv': float(comision_cnv),
            'iva': float(iva),
            'total': float(total)
        }
    
    def calcular_comisiones_venta(self, monto_base: Decimal) -> Dict:
        """Calcula todas las comisiones de una venta"""
        monto = Decimal(str(monto_base))
        
        comision_casa = monto * Decimal(str(self.config_comisiones['casa_bolsa_venta']))
        comision_cnv = monto * Decimal(str(self.config_comisiones['cnv']))
        
        subtotal_comisiones = comision_casa + comision_cnv
        iva = subtotal_comisiones * Decimal(str(self.config_comisiones['iva']))
        
        total = comision_casa + comision_cnv + iva
        
        return {
            'casa_bolsa': float(comision_casa),
            'cnv': float(comision_cnv),
            'iva': float(iva),
            'total': float(total)
        }
    
    # ==================== VALIDACIONES ====================
    
    def _validar_datos_compra(self, datos: Dict) -> Dict:
        """Valida datos de entrada para orden de compra"""
        # Validar campos requeridos
        required = ['cuenta_bursatil_id', 'cuenta_bancaria_id', 
                   'titulo_id', 'cantidad', 'precio_limite', 'tipo']
        
        for field in required:
            if field not in datos:
                return {'valido': False, 'mensaje': f"Campo requerido: {field}"}
        
        # Validar cantidad
        if datos['cantidad'] <= 0:
            return {'valido': False, 'mensaje': "La cantidad debe ser mayor a 0"}
        
        # Validar precio
        if datos['precio_limite'] <= 0:
            return {'valido': False, 'mensaje': "El precio debe ser mayor a 0"}
        
        return {'valido': True, 'mensaje': ''}
    
    # ==================== INFORMACIÓN ADICIONAL ====================
    
    def get_resumen_operaciones(self, cliente_id: int) -> Dict:
        """Obtiene resumen completo de operaciones de un cliente"""
        try:
            ordenes = self.orden_repo.get_ordenes_por_cliente(cliente_id)
            estadisticas = self.orden_repo.get_estadisticas_ordenes(cliente_id)
            
            return {
                'ordenes_recientes': ordenes[:10],
                'estadisticas': estadisticas,
                'total_ordenes': len(ordenes)
            }
        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return {
                'ordenes_recientes': [],
                'estadisticas': {},
                'total_ordenes': 0
            }