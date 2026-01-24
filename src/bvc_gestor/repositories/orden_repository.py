"""
Repositorio de Órdenes - Queries especializadas para órdenes.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .base_repository import BaseRepository
from ..database.models_sql import OrdenDB, TituloDB, CuentaBursatilDB, ClienteDB
from ..utils.constants import TipoOrden, EstadoOrden
from sqlalchemy import func, and_, or_
import logging

logger = logging.getLogger(__name__)


class OrdenRepository(BaseRepository):
    """Repositorio para gestionar órdenes de compra/venta"""
    
    def __init__(self, db_engine):
        super().__init__(db_engine, OrdenDB)
    
    # ==================== QUERIES ESPECIALIZADAS ====================
    
    def get_ordenes_por_cliente(self, cliente_id: int, 
                                activas_solo: bool = False,
                                limit: Optional[int] = None) -> List[Dict]:
        """Obtiene órdenes de un cliente con información completa"""
        try:
            with self.db_engine.get_session() as session:
                query = (
                    session.query(
                        OrdenDB,
                        TituloDB.ticker,
                        TituloDB.nombre.label('titulo_nombre'),
                        CuentaBursatilDB.numero_cuenta
                    )
                    .join(TituloDB, OrdenDB.titulo_id == TituloDB.id)
                    .join(CuentaBursatilDB, OrdenDB.cuenta_bursatil_id == CuentaBursatilDB.id)
                    .filter(CuentaBursatilDB.cliente_id == cliente_id)
                )
                
                if activas_solo:
                    query = query.filter(
                        OrdenDB.estado.in_([
                            EstadoOrden.PENDIENTE.value,
                            EstadoOrden.ESPERANDO_FONDOS.value
                        ])
                    )
                
                query = query.order_by(OrdenDB.fecha_orden.desc())
                
                if limit:
                    query = query.limit(limit)
                
                results = query.all()
                
                ordenes = []
                for orden, ticker, titulo_nombre, numero_cuenta in results:
                    data = self._to_dict(orden)
                    data['ticker'] = ticker
                    data['titulo_nombre'] = titulo_nombre
                    data['numero_cuenta'] = numero_cuenta
                    ordenes.append(data)
                
                return ordenes
        
        except Exception as e:
            logger.error(f"Error obteniendo órdenes del cliente {cliente_id}: {e}")
            return []
    
    def get_ordenes_recientes(self, limite_dias: int = 30, 
                            cliente_id: Optional[int] = None,
                            limit: int = 50) -> List[Dict]:
        """Obtiene órdenes recientes con joins"""
        try:
            fecha_limite = datetime.now() - timedelta(days=limite_dias)
            
            with self.db_engine.get_session() as session:
                query = (
                    session.query(
                        OrdenDB,
                        TituloDB.ticker,
                        TituloDB.nombre.label('titulo_nombre'),
                        ClienteDB.nombre_completo.label('cliente_nombre'),
                        CuentaBursatilDB.numero_cuenta
                    )
                    .join(TituloDB, OrdenDB.titulo_id == TituloDB.id)
                    .join(CuentaBursatilDB, OrdenDB.cuenta_bursatil_id == CuentaBursatilDB.id)
                    .join(ClienteDB, CuentaBursatilDB.cliente_id == ClienteDB.id)
                    .filter(OrdenDB.fecha_orden >= fecha_limite)
                )
                
                if cliente_id:
                    query = query.filter(ClienteDB.id == cliente_id)
                
                query = query.order_by(OrdenDB.fecha_orden.desc()).limit(limit)
                
                results = query.all()
                
                ordenes = []
                for orden, ticker, titulo_nombre, cliente_nombre, numero_cuenta in results:
                    data = self._to_dict(orden)
                    data['ticker'] = ticker
                    data['titulo_nombre'] = titulo_nombre
                    data['cliente_nombre'] = cliente_nombre
                    data['numero_cuenta'] = numero_cuenta
                    ordenes.append(data)
                
                return ordenes
        
        except Exception as e:
            logger.error(f"Error obteniendo órdenes recientes: {e}")
            return []
    
    def get_ordenes_pendientes_por_cuenta(self, cuenta_bursatil_id: int) -> List[Dict]:
        """Obtiene órdenes pendientes de una cuenta bursátil"""
        try:
            with self.db_engine.get_session() as session:
                query = (
                    session.query(OrdenDB, TituloDB.ticker, TituloDB.nombre)
                    .join(TituloDB, OrdenDB.titulo_id == TituloDB.id)
                    .filter(
                        and_(
                            OrdenDB.cuenta_bursatil_id == cuenta_bursatil_id,
                            OrdenDB.estado.in_([
                                EstadoOrden.PENDIENTE.value,
                                EstadoOrden.ESPERANDO_FONDOS.value
                            ])
                        )
                    )
                    .order_by(OrdenDB.fecha_orden.desc())
                )
                
                results = query.all()
                
                ordenes = []
                for orden, ticker, nombre in results:
                    data = self._to_dict(orden)
                    data['ticker'] = ticker
                    data['titulo_nombre'] = nombre
                    ordenes.append(data)
                
                return ordenes
        
        except Exception as e:
            logger.error(f"Error obteniendo órdenes pendientes: {e}")
            return []
    
    def get_estadisticas_ordenes(self, cliente_id: Optional[int] = None) -> Dict:
        """Obtiene estadísticas de órdenes"""
        try:
            with self.db_engine.get_session() as session:
                query = session.query(OrdenDB)
                
                if cliente_id:
                    query = query.join(CuentaBursatilDB).filter(
                        CuentaBursatilDB.cliente_id == cliente_id
                    )
                
                total = query.count()
                
                pendientes = query.filter(
                    OrdenDB.estado == EstadoOrden.PENDIENTE.value
                ).count()
                
                ejecutadas = query.filter(
                    OrdenDB.estado == EstadoOrden.EJECUTADA.value
                ).count()
                
                canceladas = query.filter(
                    OrdenDB.estado == EstadoOrden.CANCELADA.value
                ).count()
                
                esperando_fondos = query.filter(
                    OrdenDB.estado == EstadoOrden.ESPERANDO_FONDOS.value
                ).count()
                
                # Monto total en órdenes activas
                monto_activo = query.filter(
                    OrdenDB.estado.in_([
                        EstadoOrden.PENDIENTE.value,
                        EstadoOrden.ESPERANDO_FONDOS.value
                    ])
                ).with_entities(func.sum(OrdenDB.monto_total_estimado)).scalar() or 0
                
                return {
                    'total': total,
                    'pendientes': pendientes,
                    'ejecutadas': ejecutadas,
                    'canceladas': canceladas,
                    'esperando_fondos': esperando_fondos,
                    'monto_activo': float(monto_activo)
                }
        
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total': 0,
                'pendientes': 0,
                'ejecutadas': 0,
                'canceladas': 0,
                'esperando_fondos': 0,
                'monto_activo': 0
            }
    
    def cambiar_estado_orden(self, orden_id: int, nuevo_estado: EstadoOrden) -> bool:
        """Cambia el estado de una orden"""
        try:
            with self.db_engine.get_session() as session:
                orden = session.query(OrdenDB).filter_by(id=orden_id).first()
                
                if not orden:
                    logger.warning(f"Orden {orden_id} no encontrada")
                    return False
                
                estado_anterior = orden.estado
                orden.estado = nuevo_estado.value
                
                # Actualizar fecha de ejecución si aplica
                if nuevo_estado == EstadoOrden.EJECUTADA:
                    orden.fecha_ejecucion = datetime.now()
                
                session.commit()
                self._invalidate_cache(orden_id)
                
                logger.info(
                    f"✅ Orden {orden_id}: {estado_anterior} → {nuevo_estado.value}"
                )
                return True
        
        except Exception as e:
            logger.error(f"Error cambiando estado de orden: {e}")
            return False
    
    def cancelar_orden(self, orden_id: int, motivo: Optional[str] = None) -> bool:
        """Cancela una orden con motivo opcional"""
        try:
            with self.db_engine.get_session() as session:
                orden = session.query(OrdenDB).filter_by(id=orden_id).first()
                
                if not orden:
                    return False
                
                # Solo se pueden cancelar órdenes pendientes o esperando fondos
                if orden.estado not in [
                    EstadoOrden.PENDIENTE.value,
                    EstadoOrden.ESPERANDO_FONDOS.value
                ]:
                    logger.warning(
                        f"No se puede cancelar orden {orden_id} en estado {orden.estado}"
                    )
                    return False
                
                orden.estado = EstadoOrden.CANCELADA.value
                
                if motivo:
                    if orden.observaciones:
                        orden.observaciones += f"\n[CANCELACIÓN] {motivo}"
                    else:
                        orden.observaciones = f"[CANCELACIÓN] {motivo}"
                
                session.commit()
                self._invalidate_cache(orden_id)
                
                logger.info(f"✅ Orden {orden_id} cancelada: {motivo}")
                return True
        
        except Exception as e:
            logger.error(f"Error cancelando orden: {e}")
            return False
    
    def buscar_ordenes(self, 
                      ticker: Optional[str] = None,
                      tipo: Optional[TipoOrden] = None,
                      estado: Optional[EstadoOrden] = None,
                      fecha_desde: Optional[datetime] = None,
                      fecha_hasta: Optional[datetime] = None,
                      cliente_id: Optional[int] = None) -> List[Dict]:
        """Búsqueda avanzada de órdenes con múltiples filtros"""
        try:
            with self.db_engine.get_session() as session:
                query = (
                    session.query(
                        OrdenDB,
                        TituloDB.ticker,
                        TituloDB.nombre.label('titulo_nombre'),
                        ClienteDB.nombre_completo.label('cliente_nombre')
                    )
                    .join(TituloDB, OrdenDB.titulo_id == TituloDB.id)
                    .join(CuentaBursatilDB, OrdenDB.cuenta_bursatil_id == CuentaBursatilDB.id)
                    .join(ClienteDB, CuentaBursatilDB.cliente_id == ClienteDB.id)
                )
                
                # Aplicar filtros
                if ticker:
                    query = query.filter(TituloDB.ticker.ilike(f"%{ticker}%"))
                
                if tipo:
                    query = query.filter(OrdenDB.tipo == tipo.value)
                
                if estado:
                    query = query.filter(OrdenDB.estado == estado.value)
                
                if fecha_desde:
                    query = query.filter(OrdenDB.fecha_orden >= fecha_desde)
                
                if fecha_hasta:
                    query = query.filter(OrdenDB.fecha_orden <= fecha_hasta)
                
                if cliente_id:
                    query = query.filter(ClienteDB.id == cliente_id)
                
                query = query.order_by(OrdenDB.fecha_orden.desc())
                
                results = query.all()
                
                ordenes = []
                for orden, ticker, titulo_nombre, cliente_nombre in results:
                    data = self._to_dict(orden)
                    data['ticker'] = ticker
                    data['titulo_nombre'] = titulo_nombre
                    data['cliente_nombre'] = cliente_nombre
                    ordenes.append(data)
                
                return ordenes
        
        except Exception as e:
            logger.error(f"Error en búsqueda de órdenes: {e}")
            return []
    
    def get_orden_completa(self, orden_id: int) -> Optional[Dict]:
        """Obtiene una orden con toda la información relacionada"""
        try:
            with self.db_engine.get_session() as session:
                result = (
                    session.query(
                        OrdenDB,
                        TituloDB.ticker,
                        TituloDB.nombre.label('titulo_nombre'),
                        TituloDB.precio_actual.label('precio_mercado'),
                        ClienteDB.nombre_completo.label('cliente_nombre'),
                        ClienteDB.rif_cedula.label('cliente_cedula'),
                        CuentaBursatilDB.cuenta,
                        CuentaBursatilDB.casa_bolsa
                    )
                    .join(TituloDB, OrdenDB.titulo_id == TituloDB.id)
                    .join(CuentaBursatilDB, OrdenDB.cuenta_bursatil_id == CuentaBursatilDB.id)
                    .join(ClienteDB, CuentaBursatilDB.cliente_id == ClienteDB.id)
                    .filter(OrdenDB.id == orden_id)
                    .first()
                )
                
                if not result:
                    return None
                
                (orden, ticker, titulo_nombre, precio_mercado, 
                cliente_nombre, cliente_cedula, numero_cuenta, casa_bolsa) = result
                
                data = self._to_dict(orden)
                data.update({
                    'ticker': ticker,
                    'titulo_nombre': titulo_nombre,
                    'precio_mercado': precio_mercado,
                    'cliente_nombre': cliente_nombre,
                    'cliente_cedula': cliente_cedula,
                    'numero_cuenta': numero_cuenta,
                    'casa_bolsa': casa_bolsa
                })
                
                return data
        
        except Exception as e:
            logger.error(f"Error obteniendo orden completa: {e}")
            return None