# src/bvc_gestor/database/repositories.py
"""
Repositorios para acceso a datos con SQLAlchemy
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.exc import SQLAlchemyError
import logging

from .models_sql import (
    ClienteDB, CuentaDB, ActivoDB, OrdenDB,
    TransaccionDB, PortafolioItemDB, MovimientoDB,
    DocumentoDB, ConfiguracionDB
)
from ..utils.logger import logger

class BaseRepository:
    """Repositorio base con operaciones CRUD comunes"""
    
    def __init__(self, db: Session, model_class):
        self.db = db
        self.model_class = model_class
    
    def get(self, id: Any) -> Optional[Any]:
        """Obtener por ID"""
        try:
            return self.db.query(self.model_class).filter(self.model_class.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo {self.model_class.__name__} con ID {id}: {str(e)}")
            return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Obtener todos los registros"""
        try:
            return self.db.query(self.model_class).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo todos los {self.model_class.__name__}: {str(e)}")
            return []
    
    def create(self, obj: Any) -> Optional[Any]:
        """Crear nuevo registro"""
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creando {self.model_class.__name__}: {str(e)}")
            return None
    
    def update(self, id: Any, update_data: Dict[str, Any]) -> Optional[Any]:
        """Actualizar registro"""
        try:
            obj = self.get(id)
            if obj:
                for key, value in update_data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                self.db.commit()
                self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error actualizando {self.model_class.__name__} con ID {id}: {str(e)}")
            return None
    
    def delete(self, id: Any) -> bool:
        """Eliminar registro"""
        try:
            obj = self.get(id)
            if obj:
                self.db.delete(obj)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error eliminando {self.model_class.__name__} con ID {id}: {str(e)}")
            return False
    
    def count(self) -> int:
        """Contar total de registros"""
        try:
            return self.db.query(func.count(self.model_class.id)).scalar()
        except SQLAlchemyError as e:
            logger.error(f"Error contando {self.model_class.__name__}: {str(e)}")
            return 0

class ClienteRepository(BaseRepository):
    """Repositorio específico para Clientes"""
    
    def __init__(self, db: Session):
        super().__init__(db, ClienteDB)
    
    def get_by_cedula(self, cedula: str) -> Optional[ClienteDB]:
        """Obtener cliente por cédula/RIF"""
        try:
            return self.db.query(ClienteDB).filter(ClienteDB.id == cedula).first()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo cliente por cédula {cedula}: {str(e)}")
            return None
    
    def search(self, query: str) -> List[ClienteDB]:
        """Buscar clientes por nombre, cédula o email"""
        try:
            search_pattern = f"%{query}%"
            return self.db.query(ClienteDB).filter(
                or_(
                    ClienteDB.nombre_completo.ilike(search_pattern),
                    ClienteDB.id.ilike(search_pattern),
                    ClienteDB.email.ilike(search_pattern)
                )
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error buscando clientes con query '{query}': {str(e)}")
            return []
    
    def get_active_clients(self) -> List[ClienteDB]:
        """Obtener clientes activos"""
        try:
            return self.db.query(ClienteDB).filter(ClienteDB.activo == True).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo clientes activos: {str(e)}")
            return []
    
    def get_by_risk_profile(self, perfil_riesgo: str) -> List[ClienteDB]:
        """Obtener clientes por perfil de riesgo"""
        try:
            return self.db.query(ClienteDB).filter(ClienteDB.perfil_riesgo == perfil_riesgo).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo clientes por perfil {perfil_riesgo}: {str(e)}")
            return []
    
    def get_client_summary(self) -> Dict[str, Any]:
        """Obtener resumen estadístico de clientes"""
        try:
            total = self.count()
            activos = self.db.query(func.count(ClienteDB.id)).filter(ClienteDB.activo == True).scalar() or 0
            naturales = self.db.query(func.count(ClienteDB.id)).filter(
                ClienteDB.tipo_persona == 'Natural'
            ).scalar() or 0
            juridicos = total - naturales
            
            return {
                'total': total,
                'activos': activos,
                'naturales': naturales,
                'juridicos': juridicos,
                'inactivos': total - activos
            }
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo resumen de clientes: {str(e)}")
            return {}

class CuentaRepository(BaseRepository):
    """Repositorio específico para Cuentas"""
    
    def __init__(self, db: Session):
        super().__init__(db, CuentaDB)
    
    def get_by_cliente(self, cliente_id: str) -> List[CuentaDB]:
        """Obtener cuentas de un cliente"""
        try:
            return self.db.query(CuentaDB).filter(CuentaDB.cliente_id == cliente_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo cuentas para cliente {cliente_id}: {str(e)}")
            return []
    
    def get_by_numero(self, numero_cuenta: str) -> Optional[CuentaDB]:
        """Obtener cuenta por número"""
        try:
            return self.db.query(CuentaDB).filter(CuentaDB.numero_cuenta == numero_cuenta).first()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo cuenta {numero_cuenta}: {str(e)}")
            return None
    
    def get_active_accounts(self) -> List[CuentaDB]:
        """Obtener cuentas activas"""
        try:
            return self.db.query(CuentaDB).filter(CuentaDB.estado == 'Activa').all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo cuentas activas: {str(e)}")
            return []
    
    def update_balance(self, cuenta_id: int, moneda: str, monto: float, 
                    tipo: str = 'disponible') -> bool:
        """Actualizar saldo de cuenta"""
        try:
            cuenta = self.get(cuenta_id)
            if not cuenta:
                return False
            
            field_name = f"saldo_{tipo}_{moneda.lower()}"
            if not hasattr(cuenta, field_name):
                return False
            
            current_balance = getattr(cuenta, field_name) or 0
            new_balance = current_balance + monto
            
            if new_balance < 0:
                return False  # Saldo negativo no permitido
            
            setattr(cuenta, field_name, new_balance)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error actualizando saldo cuenta {cuenta_id}: {str(e)}")
            return False

class OrdenRepository(BaseRepository):
    """Repositorio específico para Órdenes"""
    
    def __init__(self, db: Session):
        super().__init__(db, OrdenDB)
    
    def get_pending_orders(self) -> List[OrdenDB]:
        """Obtener órdenes pendientes"""
        try:
            return self.db.query(OrdenDB).filter(
                OrdenDB.estado == 'Pendiente'
            ).order_by(OrdenDB.fecha_creacion).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo órdenes pendientes: {str(e)}")
            return []
    
    def get_orders_by_client(self, cliente_id: str) -> List[OrdenDB]:
        """Obtener órdenes de un cliente"""
        try:
            return self.db.query(OrdenDB).filter(
                OrdenDB.cliente_id == cliente_id
            ).order_by(desc(OrdenDB.fecha_creacion)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo órdenes de cliente {cliente_id}: {str(e)}")
            return []
    
    def get_orders_by_status(self, estado: str) -> List[OrdenDB]:
        """Obtener órdenes por estado"""
        try:
            return self.db.query(OrdenDB).filter(
                OrdenDB.estado == estado
            ).order_by(OrdenDB.fecha_creacion).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo órdenes con estado {estado}: {str(e)}")
            return []
    
    def get_today_orders(self) -> List[OrdenDB]:
        """Obtener órdenes del día de hoy"""
        try:
            from datetime import datetime, date
            today = date.today()
            return self.db.query(OrdenDB).filter(
                func.date(OrdenDB.fecha_creacion) == today
            ).order_by(desc(OrdenDB.fecha_creacion)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo órdenes de hoy: {str(e)}")
            return []

class ActivoRepository(BaseRepository):
    """Repositorio específico para Activos"""
    
    def __init__(self, db: Session):
        super().__init__(db, ActivoDB)
    
    def get_active_assets(self) -> List[ActivoDB]:
        """Obtener activos bursátiles activos"""
        try:
            return self.db.query(ActivoDB).filter(ActivoDB.activo == True).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo activos activos: {str(e)}")
            return []
    
    def search(self, query: str) -> List[ActivoDB]:
        """Buscar activos por símbolo o nombre"""
        try:
            search_pattern = f"%{query}%"
            return self.db.query(ActivoDB).filter(
                or_(
                    ActivoDB.id.ilike(search_pattern),
                    ActivoDB.nombre.ilike(search_pattern)
                ),
                ActivoDB.activo == True
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error buscando activos con query '{query}': {str(e)}")
            return []
    
    def get_by_sector(self, sector: str) -> List[ActivoDB]:
        """Obtener activos por sector"""
        try:
            return self.db.query(ActivoDB).filter(
                ActivoDB.sector == sector,
                ActivoDB.activo == True
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo activos del sector {sector}: {str(e)}")
            return []
    
    def update_prices(self, prices: Dict[str, float]) -> bool:
        """Actualizar precios de activos"""
        try:
            for simbolo, precio in prices.items():
                activo = self.get(simbolo)
                if activo:
                    activo.precio_anterior = activo.precio_actual
                    activo.precio_actual = precio
                    if activo.precio_anterior > 0:
                        activo.variacion_diaria = (
                            (precio - activo.precio_anterior) / activo.precio_anterior
                        ) * 100
            
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error actualizando precios: {str(e)}")
            return False

class RepositoryFactory:
    """Factory para crear repositorios"""
    
    @staticmethod
    def get_repository(db: Session, model_type: str):
        """Obtener repositorio específico por tipo"""
        repositories = {
            'cliente': ClienteRepository,
            'cuenta': CuentaRepository,
            'activo': ActivoRepository,
            'orden': OrdenRepository,
            'transaccion': BaseRepository,
            'portafolio': BaseRepository,
            'movimiento': BaseRepository,
            'documento': BaseRepository,
            'configuracion': BaseRepository,
        }
        
        repo_class = repositories.get(model_type)
        if repo_class:
            if repo_class == BaseRepository:
                return repo_class(db, get_model_class(model_type))
            else:
                # Para repositorios específicos que solo necesitan db
                return repo_class(db)
        
        return None

def get_model_class(model_type: str):
    """Obtener clase de modelo por tipo"""
    from .models_sql import (
        ClienteDB, CuentaDB, ActivoDB, OrdenDB,
        TransaccionDB, PortafolioItemDB, MovimientoDB,
        DocumentoDB, ConfiguracionDB
    )
    
    model_map = {
        'cliente': ClienteDB,
        'cuenta': CuentaDB,
        'activo': ActivoDB,
        'orden': OrdenDB,
        'transaccion': TransaccionDB,
        'portafolio': PortafolioItemDB,
        'movimiento': MovimientoDB,
        'documento': DocumentoDB,
        'configuracion': ConfiguracionDB,
    }
    
    return model_map.get(model_type, None)