"""
Repositorios de Saldo
"""

from typing import List, Dict, Optional
from .base_repository import BaseRepository
from ..database.models_sql import SaldoDB, PortafolioItemDB, TituloDB, CuentaBursatilDB
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class SaldoRepository(BaseRepository):
    """Repositorio para gestionar saldos de cuentas bancarias"""
    
    def __init__(self, db_engine):
        super().__init__(db_engine, SaldoDB)
    
    def get_saldo_cuenta(self, cuenta_bancaria_id: int) -> Optional[Dict]:
        """Obtiene el saldo de una cuenta bancaria"""
        try:
            with self.db_engine.get_session() as session:
                saldo = session.query(SaldoDB).filter_by(
                    cuenta_bancaria_id=cuenta_bancaria_id
                ).first()
                
                if saldo:
                    return self._to_dict(saldo)
                else:
                    # Retornar saldo en ceros si no existe
                    return {
                        'cuenta_bancaria_id': cuenta_bancaria_id,
                        'disponible': 0,
                        'bloqueado': 0,
                        'en_transito': 0
                    }
        
        except Exception as e:
            logger.error(f"Error obteniendo saldo: {e}")
            return None
    
    def actualizar_saldo(self, cuenta_bancaria_id: int, 
                        disponible: float = None,
                        bloqueado: float = None,
                        en_transito: float = None) -> bool:
        """Actualiza componentes del saldo"""
        try:
            with self.db_engine.get_session() as session:
                saldo = session.query(SaldoDB).filter_by(
                    cuenta_bancaria_id=cuenta_bancaria_id
                ).first()
                
                if not saldo:
                    # Crear saldo si no existe
                    saldo = SaldoDB(
                        cuenta_bancaria_id=cuenta_bancaria_id,
                        disponible=disponible or 0,
                        bloqueado=bloqueado or 0,
                        en_transito=en_transito or 0
                    )
                    session.add(saldo)
                else:
                    # Actualizar solo los campos provistos
                    if disponible is not None:
                        saldo.disponible = disponible
                    if bloqueado is not None:
                        saldo.bloqueado = bloqueado
                    if en_transito is not None:
                        saldo.en_transito = en_transito
                
                session.commit()
                self._invalidate_cache()
                return True
        
        except Exception as e:
            logger.error(f"Error actualizando saldo: {e}")
            return False
    
    def agregar_deposito(self, cuenta_bancaria_id: int, monto: float) -> bool:
        """Agrega un depósito al saldo disponible"""
        try:
            with self.db_engine.get_session() as session:
                saldo = session.query(SaldoDB).filter_by(
                    cuenta_bancaria_id=cuenta_bancaria_id
                ).first()
                
                if not saldo:
                    saldo = SaldoDB(
                        cuenta_bancaria_id=cuenta_bancaria_id,
                        disponible=monto,
                        bloqueado=0,
                        en_transito=0
                    )
                    session.add(saldo)
                else:
                    saldo.disponible += monto
                
                session.commit()
                self._invalidate_cache()
                
                logger.info(f"💰 Depósito agregado: +Bs. {monto:,.2f}")
                return True
        
        except Exception as e:
            logger.error(f"Error agregando depósito: {e}")
            return False
    
    def bloquear_fondos(self, cuenta_bancaria_id: int, monto: float) -> bool:
        """Bloquea fondos (mueve de disponible a bloqueado)"""
        try:
            with self.db_engine.get_session() as session:
                saldo = session.query(SaldoDB).filter_by(
                    cuenta_bancaria_id=cuenta_bancaria_id
                ).first()
                
                if not saldo or saldo.disponible < monto:
                    return False
                
                saldo.disponible -= monto
                saldo.bloqueado += monto
                
                session.commit()
                self._invalidate_cache()
                return True
        
        except Exception as e:
            logger.error(f"Error bloqueando fondos: {e}")
            return False
    
    def liberar_fondos(self, cuenta_bancaria_id: int, monto: float) -> bool:
        """Libera fondos bloqueados"""
        try:
            with self.db_engine.get_session() as session:
                saldo = session.query(SaldoDB).filter_by(
                    cuenta_bancaria_id=cuenta_bancaria_id
                ).first()
                
                if not saldo or saldo.bloqueado < monto:
                    return False
                
                saldo.bloqueado -= monto
                saldo.disponible += monto
                
                session.commit()
                self._invalidate_cache()
                return True
        
        except Exception as e:
            logger.error(f"Error liberando fondos: {e}")
            return False
    
    def get_saldos_cliente(self, cliente_id: int) -> List[Dict]:
        """Obtiene todos los saldos de cuentas bancarias de un cliente"""
        try:
            with self.db_engine.get_session() as session:
                from ..database.models_sql import CuentaBancariaDB
                
                results = (
                    session.query(
                        SaldoDB,
                        CuentaBancariaDB.banco,
                        CuentaBancariaDB.numero_cuenta,
                        CuentaBancariaDB.tipo_cuenta
                    )
                    .join(CuentaBancariaDB, SaldoDB.cuenta_bancaria_id == CuentaBancariaDB.id)
                    .filter(CuentaBancariaDB.cliente_id == cliente_id)
                    .all()
                )
                
                saldos = []
                for saldo, banco, numero_cuenta, tipo_cuenta in results:
                    data = self._to_dict(saldo)
                    data.update({
                        'banco': banco,
                        'numero_cuenta': numero_cuenta,
                        'tipo_cuenta': tipo_cuenta
                    })
                    saldos.append(data)
                
                return saldos
        
        except Exception as e:
            logger.error(f"Error obteniendo saldos del cliente: {e}")
            return []