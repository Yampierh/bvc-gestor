"""
Repositorios de Portafolio
"""

from typing import List, Dict, Optional
from .base_repository import BaseRepository
from ..database.models_sql import SaldoDB, PortafolioItemDB, TituloDB, CuentaBursatilDB
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class PortafolioRepository(BaseRepository):
    """Repositorio para gestionar portafolios de inversión"""
    
    def __init__(self, db_engine):
        super().__init__(db_engine, PortafolioItemDB)
    
    def get_portafolio_cuenta(self, cuenta_bursatil_id: int, 
                            incluir_precios_actuales: bool = True) -> List[Dict]:
        """Obtiene el portafolio completo de una cuenta bursátil"""
        try:
            with self.db_engine.get_session() as session:
                query = (
                    session.query(
                        PortafolioItemDB,
                        TituloDB.ticker,
                        TituloDB.nombre,
                        TituloDB.precio_actual
                    )
                    .join(TituloDB, PortafolioItemDB.titulo_id == TituloDB.id)
                    .filter(PortafolioItemDB.cuenta_bursatil_id == cuenta_bursatil_id)
                    .filter(PortafolioItemDB.cantidad_total > 0)
                )
                
                results = query.all()
                
                portafolio = []
                for item, ticker, nombre, precio_actual in results:
                    data = self._to_dict(item)
                    data['ticker'] = ticker
                    data['nombre'] = nombre
                    data['precio_actual'] = precio_actual
                    
                    # Calcular métricas
                    if incluir_precios_actuales and precio_actual:
                        valor_mercado = item.cantidad_total * precio_actual
                        costo_total = item.cantidad_total * item.costo_promedio
                        ganancia_perdida = valor_mercado - costo_total
                        rendimiento = (ganancia_perdida / costo_total * 100) if costo_total > 0 else 0
                        
                        data['valor_mercado'] = float(valor_mercado)
                        data['costo_total'] = float(costo_total)
                        data['ganancia_perdida'] = float(ganancia_perdida)
                        data['rendimiento_pct'] = float(rendimiento)
                    
                    portafolio.append(data)
                
                return portafolio
        
        except Exception as e:
            logger.error(f"Error obteniendo portafolio: {e}")
            return []
    
    def get_resumen_portafolio(self, cuenta_bursatil_id: int) -> Dict:
        """Obtiene resumen del portafolio con totales"""
        try:
            portafolio = self.get_portafolio_cuenta(cuenta_bursatil_id)
            
            if not portafolio:
                return {
                    'total_posiciones': 0,
                    'valor_mercado_total': 0,
                    'inversion_total': 0,
                    'ganancia_perdida_total': 0,
                    'rendimiento_total_pct': 0
                }
            
            valor_mercado_total = sum(p['valor_mercado'] for p in portafolio)
            inversion_total = sum(p['costo_total'] for p in portafolio)
            ganancia_perdida = valor_mercado_total - inversion_total
            rendimiento = (ganancia_perdida / inversion_total * 100) if inversion_total > 0 else 0
            
            return {
                'total_posiciones': len(portafolio),
                'valor_mercado_total': valor_mercado_total,
                'inversion_total': inversion_total,
                'ganancia_perdida_total': ganancia_perdida,
                'rendimiento_total_pct': rendimiento,
                'posiciones': portafolio
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo resumen de portafolio: {e}")
            return {}
    
    def get_posicion_ticker(self, cuenta_bursatil_id: int, 
                           titulo_id: int) -> Optional[Dict]:
        """Obtiene la posición de un ticker específico"""
        try:
            with self.db_engine.get_session() as session:
                result = (
                    session.query(
                        PortafolioItemDB,
                        TituloDB.ticker,
                        TituloDB.nombre,
                        TituloDB.precio_actual
                    )
                    .join(TituloDB, PortafolioItemDB.titulo_id == TituloDB.id)
                    .filter(
                        PortafolioItemDB.cuenta_bursatil_id == cuenta_bursatil_id,
                        PortafolioItemDB.titulo_id == titulo_id
                    )
                    .first()
                )
                
                if not result:
                    return None
                
                item, ticker, nombre, precio_actual = result
                data = self._to_dict(item)
                data['ticker'] = ticker
                data['nombre'] = nombre
                data['precio_actual'] = precio_actual
                
                return data
        
        except Exception as e:
            logger.error(f"Error obteniendo posición: {e}")
            return None
    
    def get_portafolio_cliente(self, cliente_id: int) -> List[Dict]:
        """Obtiene portafolio consolidado de todas las cuentas de un cliente"""
        try:
            with self.db_engine.get_session() as session:
                results = (
                    session.query(
                        PortafolioItemDB,
                        TituloDB.ticker,
                        TituloDB.nombre,
                        TituloDB.precio_actual,
                        CuentaBursatilDB.casa_bolsa,
                        CuentaBursatilDB.numero_cuenta
                    )
                    .join(TituloDB, PortafolioItemDB.titulo_id == TituloDB.id)
                    .join(CuentaBursatilDB, PortafolioItemDB.cuenta_bursatil_id == CuentaBursatilDB.id)
                    .filter(CuentaBursatilDB.cliente_id == cliente_id)
                    .filter(PortafolioItemDB.cantidad_total > 0)
                    .all()
                )
                
                portafolio = []
                for item, ticker, nombre, precio_actual, casa_bolsa, numero_cuenta in results:
                    data = self._to_dict(item)
                    data.update({
                        'ticker': ticker,
                        'nombre': nombre,
                        'precio_actual': precio_actual,
                        'casa_bolsa': casa_bolsa,
                        'numero_cuenta': numero_cuenta
                    })
                    
                    # Calcular métricas
                    if precio_actual:
                        valor_mercado = item.cantidad_total * precio_actual
                        costo_total = item.cantidad_total * item.costo_promedio
                        ganancia_perdida = valor_mercado - costo_total
                        
                        data['valor_mercado'] = float(valor_mercado)
                        data['costo_total'] = float(costo_total)
                        data['ganancia_perdida'] = float(ganancia_perdida)
                    
                    portafolio.append(data)
                
                return portafolio
        
        except Exception as e:
            logger.error(f"Error obteniendo portafolio del cliente: {e}")
            return []