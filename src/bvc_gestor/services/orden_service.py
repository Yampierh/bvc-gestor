# src/bvc_gestor/services/orden_service.py
"""
Servicio para gestión de órdenes bursátiles
"""
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

from ..database.engine import get_database
from ..database.repositories import RepositoryFactory
from ..database.models_sql import OrdenDB, CuentaDB, ClienteDB, TransaccionDB
from ..utils.calculos_financieros import (
    calcular_comision_bvc,
    calcular_monto_total_orden,
    validar_limites_cliente,
    simular_ejecucion_orden
)
from ..utils.constants import TipoOrden, TipoOperacion, EstadoOrden, Moneda
from ..utils.logger import logger

class OrdenService:
    """Servicio para operaciones con órdenes"""
    
    def __init__(self):
        self.db_session = None
    
    def obtener_sesion(self):
        """Obtener sesión de base de datos"""
        if self.db_session is None:
            self.db_session = get_database().get_session()
        return self.db_session
    
    def generar_numero_orden(self) -> str:
        """Generar número de orden único"""
        import random
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = random.randint(1000, 9999)
        return f"ORD-{timestamp}-{random_part}"
    
    def validar_orden(self, orden_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validar una orden antes de crearla
        
        Returns:
            (es_valida, mensaje_error)
        """
        try:
            # Validaciones básicas
            if orden_data['cantidad'] <= 0:
                return False, "La cantidad debe ser mayor a cero"
            
            if orden_data['tipo_operacion'] == TipoOperacion.LIMITADA.value:
                if not orden_data.get('precio_limite'):
                    return False, "Las órdenes limitadas requieren precio límite"
                if orden_data['precio_limite'] <= 0:
                    return False, "El precio límite debe ser mayor a cero"
            
            # Obtener información del cliente y cuenta
            session = self.obtener_sesion()
            cliente_repo = RepositoryFactory.get_repository(session, 'cliente')
            cuenta_repo = RepositoryFactory.get_repository(session, 'cuenta')
            activo_repo = RepositoryFactory.get_repository(session, 'activo')
            
            cliente = cliente_repo.get(orden_data['cliente_id'])
            if not cliente:
                return False, "Cliente no encontrado"
            
            cuenta = cuenta_repo.get(orden_data['cuenta_id'])
            if not cuenta:
                return False, "Cuenta no encontrada"
            
            activo = activo_repo.get(orden_data['activo_id'])
            if not activo:
                return False, "Activo no encontrado"
            
            # Validar límites y saldos
            precio = orden_data.get('precio_limite') or orden_data.get('precio') or activo.precio_actual
            monto_operacion = calcular_monto_total_orden(
                orden_data['cantidad'],
                precio,
                orden_data['tipo_orden']
            )
            
            # Determinar moneda
            moneda = activo.moneda if activo.moneda in ['USD', 'Bs'] else 'USD'
            
            # Obtener límites y saldos según moneda
            if moneda == 'USD':
                limite = cliente.limite_inversion_usd or Decimal('0.00')
                saldo = cuenta.saldo_disponible_usd or Decimal('0.00')
            else:
                limite = cliente.limite_inversion_bs or Decimal('0.00')
                saldo = cuenta.saldo_disponible_bs or Decimal('0.00')
            
            # Validar
            es_valida, mensaje = validar_limites_cliente(
                monto_operacion,
                moneda,
                limite,
                saldo,
                cliente.perfil_riesgo.value
            )
            
            if not es_valida:
                return False, mensaje
            
            # Validar horario bursátil (simulado)
            hora_actual = datetime.now().time()
            hora_apertura = datetime.strptime("09:30", "%H:%M").time()
            hora_cierre = datetime.strptime("14:00", "%H:%M").time()
            
            if not (hora_apertura <= hora_actual <= hora_cierre):
                return False, "Fuera del horario bursátil (09:30 - 14:00)"
            
            return True, "Orden válida"
            
        except Exception as e:
            logger.error(f"Error validando orden: {e}")
            return False, f"Error de validación: {str(e)}"
    
    def crear_orden(self, orden_data: Dict[str, Any]) -> Tuple[Optional[OrdenDB], str]:
        """
        Crear una nueva orden bursátil
        
        Returns:
            (orden_creada, mensaje)
        """
        try:
            # Validar orden
            es_valida, mensaje = self.validar_orden(orden_data)
            if not es_valida:
                return None, mensaje
            
            session = self.obtener_sesion()
            activo_repo = RepositoryFactory.get_repository(session, 'activo')
            
            # Obtener precio si no está especificado (orden de mercado)
            activo = activo_repo.get(orden_data['activo_id'])
            precio = orden_data.get('precio_limite') or orden_data.get('precio')
            
            if not precio:
                # Para órdenes de mercado, usar precio actual
                orden_data['precio'] = activo.precio_actual
                precio = activo.precio_actual
            
            # Calcular comisiones
            monto_operacion = calcular_monto_total_orden(
                orden_data['cantidad'],
                precio,
                orden_data['tipo_orden']
            )
            
            comisiones = calcular_comision_bvc(
                abs(monto_operacion),
                tipo_operacion="normal"
            )
            
            # Crear objeto de orden
            orden = OrdenDB(
                numero_orden=self.generar_numero_orden(),
                cliente_id=orden_data['cliente_id'],
                cuenta_id=orden_data['cuenta_id'],
                activo_id=orden_data['activo_id'],
                tipo_orden=orden_data['tipo_orden'],
                tipo_operacion=orden_data['tipo_operacion'],
                cantidad=orden_data['cantidad'],
                precio=precio if orden_data['tipo_operacion'] == TipoOperacion.MERCADO.value else None,
                precio_limite=orden_data.get('precio_limite'),
                comision_base=comisiones['comision_base'],
                iva_comision=comisiones['iva'],
                comision_total=comisiones['comision_total'],
                fecha_vencimiento=datetime.now() + timedelta(days=1),  # Vence en 24 horas
                notas=orden_data.get('notas')
            )
            
            # Si es orden de compra, bloquear fondos
            if orden_data['tipo_orden'] == TipoOrden.COMPRA.value:
                self.bloquear_fondos(
                    orden_data['cuenta_id'],
                    activo.moneda,
                    abs(monto_operacion) + comisiones['comision_total']
                )
            
            # Guardar en base de datos
            orden_repo = RepositoryFactory.get_repository(session, 'orden')
            orden_creada = orden_repo.create(orden)
            
            if orden_creada:
                logger.info(f"Orden creada: {orden_creada.numero_orden} para cliente {orden_data['cliente_id']}")
                return orden_creada, "Orden creada exitosamente"
            else:
                return None, "Error al crear la orden"
            
        except Exception as e:
            logger.error(f"Error creando orden: {e}")
            return None, f"Error creando orden: {str(e)}"
    
    def bloquear_fondos(self, cuenta_id: int, moneda: str, monto: Decimal):
        """Bloquear fondos para una orden pendiente"""
        try:
            session = self.obtener_sesion()
            cuenta_repo = RepositoryFactory.get_repository(session, 'cuenta')
            
            cuenta = cuenta_repo.get(cuenta_id)
            if not cuenta:
                raise ValueError("Cuenta no encontrada")
            
            # Determinar campo según moneda
            campo_saldo = f"saldo_disponible_{moneda.lower()}"
            campo_bloqueado = f"saldo_bloqueado_{moneda.lower()}"
            
            if not hasattr(cuenta, campo_saldo) or not hasattr(cuenta, campo_bloqueado):
                raise ValueError(f"Moneda no soportada: {moneda}")
            
            # Verificar saldo disponible
            saldo_disponible = getattr(cuenta, campo_saldo) or Decimal('0.00')
            if saldo_disponible < monto:
                raise ValueError(f"Saldo insuficiente. Disponible: {saldo_disponible}, Necesario: {monto}")
            
            # Transferir de disponible a bloqueado
            setattr(cuenta, campo_saldo, saldo_disponible - monto)
            
            saldo_bloqueado = getattr(cuenta, campo_bloqueado) or Decimal('0.00')
            setattr(cuenta, campo_bloqueado, saldo_bloqueado + monto)
            
            session.commit()
            logger.info(f"Bloqueados {monto} {moneda} en cuenta {cuenta_id}")
            
        except Exception as e:
            logger.error(f"Error bloqueando fondos: {e}")
            raise
    
    def desbloquear_fondos(self, cuenta_id: int, moneda: str, monto: Decimal):
        """Desbloquear fondos (orden cancelada o rechazada)"""
        try:
            session = self.obtener_sesion()
            cuenta_repo = RepositoryFactory.get_repository(session, 'cuenta')
            
            cuenta = cuenta_repo.get(cuenta_id)
            if not cuenta:
                raise ValueError("Cuenta no encontrada")
            
            campo_saldo = f"saldo_disponible_{moneda.lower()}"
            campo_bloqueado = f"saldo_bloqueado_{moneda.lower()}"
            
            if not hasattr(cuenta, campo_saldo) or not hasattr(cuenta, campo_bloqueado):
                raise ValueError(f"Moneda no soportada: {moneda}")
            
            # Verificar saldo bloqueado
            saldo_bloqueado = getattr(cuenta, campo_bloqueado) or Decimal('0.00')
            if saldo_bloqueado < monto:
                logger.warning(f"Saldo bloqueado ({saldo_bloqueado}) menor a monto a desbloquear ({monto})")
                monto = saldo_bloqueado  # Desbloquear solo lo disponible
            
            # Transferir de bloqueado a disponible
            setattr(cuenta, campo_bloqueado, saldo_bloqueado - monto)
            
            saldo_disponible = getattr(cuenta, campo_saldo) or Decimal('0.00')
            setattr(cuenta, campo_saldo, saldo_disponible + monto)
            
            session.commit()
            logger.info(f"Desbloqueados {monto} {moneda} en cuenta {cuenta_id}")
            
        except Exception as e:
            logger.error(f"Error desbloqueando fondos: {e}")
            raise
    
    def cancelar_orden(self, orden_id: int) -> Tuple[bool, str]:
        """Cancelar una orden pendiente"""
        try:
            session = self.obtener_sesion()
            orden_repo = RepositoryFactory.get_repository(session, 'orden')
            activo_repo = RepositoryFactory.get_repository(session, 'activo')
            
            orden = orden_repo.get(orden_id)
            if not orden:
                return False, "Orden no encontrada"
            
            if orden.estado != EstadoOrden.PENDIENTE:
                return False, f"No se puede cancelar una orden en estado: {orden.estado.value}"
            
            # Obtener información para desbloquear fondos
            activo = activo_repo.get(orden.activo_id)
            moneda = activo.moneda if activo.moneda in ['USD', 'Bs'] else 'USD'
            
            monto_total = Decimal(orden.cantidad) * (orden.precio or orden.precio_limite or Decimal('0.00'))
            monto_a_desbloquear = monto_total + (orden.comision_total or Decimal('0.00'))
            
            # Solo desbloquear si es orden de compra
            if orden.tipo_orden == TipoOrden.COMPRA:
                self.desbloquear_fondos(orden.cuenta_id, moneda, monto_a_desbloquear)
            
            # Actualizar estado
            orden.estado = EstadoOrden.CANCELADA
            session.commit()
            
            logger.info(f"Orden cancelada: {orden.numero_orden}")
            return True, "Orden cancelada exitosamente"
            
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            return False, f"Error cancelando orden: {str(e)}"
    
    def simular_orden(self, orden_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simular ejecución de una orden antes de crearla"""
        try:
            session = self.obtener_sesion()
            activo_repo = RepositoryFactory.get_repository(session, 'activo')
            
            activo = activo_repo.get(orden_data['activo_id'])
            if not activo:
                return {"error": "Activo no encontrado"}
            
            # Obtener precio para simulación
            precio_solicitado = orden_data.get('precio_limite') or orden_data.get('precio')
            precio_mercado = activo.precio_actual
            
            # Simular ejecución
            simulacion = simular_ejecucion_orden(
                orden_data['tipo_orden'],
                orden_data['cantidad'],
                precio_solicitado,
                precio_mercado
            )
            
            # Calcular comisiones
            monto_simulado = Decimal(orden_data['cantidad']) * simulacion['precio_ejecucion']
            comisiones = calcular_comision_bvc(monto_simulado)
            
            # Calcular total
            monto_total = monto_simulado + comisiones['comision_total']
            if orden_data['tipo_orden'] == TipoOrden.VENTA.value:
                monto_total = monto_simulado - comisiones['comision_total']
            
            # Validar contra límites de cliente
            cliente_repo = RepositoryFactory.get_repository(session, 'cliente')
            cuenta_repo = RepositoryFactory.get_repository(session, 'cuenta')
            
            cliente = cliente_repo.get(orden_data['cliente_id'])
            cuenta = cuenta_repo.get(orden_data['cuenta_id'])
            
            moneda = activo.moneda if activo.moneda in ['USD', 'Bs'] else 'USD'
            
            if moneda == 'USD':
                limite = cliente.limite_inversion_usd or Decimal('0.00')
                saldo = cuenta.saldo_disponible_usd or Decimal('0.00')
            else:
                limite = cliente.limite_inversion_bs or Decimal('0.00')
                saldo = cuenta.saldo_disponible_bs or Decimal('0.00')
            
            es_valida, mensaje_validacion = validar_limites_cliente(
                monto_total if orden_data['tipo_orden'] == TipoOrden.COMPRA.value else -monto_total,
                moneda,
                limite,
                saldo,
                cliente.perfil_riesgo.value
            )
            
            return {
                'simulacion': simulacion,
                'comisiones': {
                    'base': float(comisiones['comision_base']),
                    'iva': float(comisiones['iva']),
                    'total': float(comisiones['comision_total'])
                },
                'montos': {
                    'operacion': float(monto_simulado),
                    'comisiones': float(comisiones['comision_total']),
                    'total': float(monto_total)
                },
                'validacion': {
                    'es_valida': es_valida,
                    'mensaje': mensaje_validacion
                },
                'activo': {
                    'simbolo': activo.id,
                    'nombre': activo.nombre,
                    'precio_actual': float(activo.precio_actual),
                    'moneda': activo.moneda
                }
            }
            
        except Exception as e:
            logger.error(f"Error simulando orden: {e}")
            return {"error": f"Error en simulación: {str(e)}"}
    
    def obtener_ordenes_pendientes(self, cliente_id: Optional[str] = None) -> List[OrdenDB]:
        """Obtener órdenes pendientes"""
        try:
            session = self.obtener_sesion()
            orden_repo = RepositoryFactory.get_repository(session, 'orden')
            
            if cliente_id:
                return orden_repo.get_orders_by_client(cliente_id)
            else:
                return orden_repo.get_pending_orders()
                
        except Exception as e:
            logger.error(f"Error obteniendo órdenes pendientes: {e}")
            return []
    
    def obtener_historial_ordenes(self, cliente_id: str, dias: int = 30) -> List[OrdenDB]:
        """Obtener historial de órdenes de un cliente"""
        try:
            session = self.obtener_sesion()
            orden_repo = RepositoryFactory.get_repository(session, 'orden')
            
            # Obtener todas las órdenes del cliente
            ordenes = orden_repo.get_orders_by_client(cliente_id)
            
            # Filtrar por fecha (últimos N días)
            fecha_limite = datetime.now() - timedelta(days=dias)
            ordenes_filtradas = [
                orden for orden in ordenes
                if orden.fecha_creacion >= fecha_limite
            ]
            
            return ordenes_filtradas
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de órdenes: {e}")
            return []