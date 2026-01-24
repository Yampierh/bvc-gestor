"""
Base Repository - Patrón Repository para acceso a datos.
Proporciona operaciones CRUD genéricas con caché opcional.
"""

from typing import List, Optional, Dict, Any, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheEntry:
    """Entrada de caché con TTL"""
    def __init__(self, data, ttl_seconds=300):
        self.data = data
        self.timestamp = datetime.now()
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def is_valid(self):
        return datetime.now() - self.timestamp < self.ttl


class BaseRepository:
    """
    Repositorio base con operaciones CRUD genéricas.
    Todas las consultas a BD deben pasar por repositorios.
    """
    
    def __init__(self, db_engine, model_class: Type[T]):
        self.db_engine = db_engine
        self.model_class = model_class
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_enabled = True
    
    # ==================== CRUD BÁSICO ====================
    
    def get_by_id(self, id: int, use_cache=True) -> Optional[Dict]:
        """Obtiene un registro por ID"""
        cache_key = f"{self.model_class.__name__}:{id}"
        
        # Verificar caché
        if use_cache and self._cache_enabled:
            cached = self._cache.get(cache_key)
            if cached and cached.is_valid():
                logger.debug(f"Cache HIT: {cache_key}")
                return cached.data
        
        # Query a BD
        try:
            with self.db_engine.get_session() as session:
                entity = session.query(self.model_class).filter_by(id=id).first()
                
                if entity:
                    data = self._to_dict(entity)
                    
                    # Guardar en caché
                    if use_cache and self._cache_enabled:
                        self._cache[cache_key] = CacheEntry(data)
                    
                    return data
                
                return None
        
        except Exception as e:
            logger.error(f"Error en get_by_id {self.model_class.__name__}({id}): {e}")
            return None
    
    def get_all(self, filters: Optional[Dict] = None, use_cache=False) -> List[Dict]:
        """Obtiene todos los registros con filtros opcionales"""
        cache_key = f"{self.model_class.__name__}:all:{str(filters)}"
        
        if use_cache and self._cache_enabled:
            cached = self._cache.get(cache_key)
            if cached and cached.is_valid():
                logger.debug(f"Cache HIT: {cache_key}")
                return cached.data
        
        try:
            with self.db_engine.get_session() as session:
                query = session.query(self.model_class)
                
                # Aplicar filtros
                if filters:
                    query = query.filter_by(**filters)
                
                entities = query.all()
                data = [self._to_dict(e) for e in entities]
                
                if use_cache and self._cache_enabled:
                    self._cache[cache_key] = CacheEntry(data)
                
                return data
        
        except Exception as e:
            logger.error(f"Error en get_all {self.model_class.__name__}: {e}")
            return []
    
    def create(self, data: Dict) -> Optional[int]:
        """Crea un nuevo registro"""
        try:
            with self.db_engine.get_session() as session:
                entity = self.model_class(**data)
                session.add(entity)
                session.commit()
                
                # Invalidar caché
                self._invalidate_cache()
                
                logger.info(f"✅ Creado {self.model_class.__name__} ID={entity.id}")
                return entity.id
        
        except Exception as e:
            logger.error(f"Error en create {self.model_class.__name__}: {e}")
            return None
    
    def update(self, id: int, data: Dict) -> bool:
        """Actualiza un registro existente"""
        try:
            with self.db_engine.get_session() as session:
                entity = session.query(self.model_class).filter_by(id=id).first()
                
                if not entity:
                    logger.warning(f"{self.model_class.__name__} ID={id} no encontrado")
                    return False
                
                # Actualizar atributos
                for key, value in data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                
                session.commit()
                
                # Invalidar caché
                self._invalidate_cache(id)
                
                logger.info(f"✅ Actualizado {self.model_class.__name__} ID={id}")
                return True
        
        except Exception as e:
            logger.error(f"Error en update {self.model_class.__name__}({id}): {e}")
            return False
    
    def delete(self, id: int) -> bool:
        """Elimina un registro (soft delete si tiene campo 'activo')"""
        try:
            with self.db_engine.get_session() as session:
                entity = session.query(self.model_class).filter_by(id=id).first()
                
                if not entity:
                    return False
                
                # Soft delete si es posible
                if hasattr(entity, 'activo'):
                    entity.activo = False
                    logger.info(f"🔒 Soft delete {self.model_class.__name__} ID={id}")
                else:
                    session.delete(entity)
                    logger.info(f"🗑️ Hard delete {self.model_class.__name__} ID={id}")
                
                session.commit()
                self._invalidate_cache(id)
                return True
        
        except Exception as e:
            logger.error(f"Error en delete {self.model_class.__name__}({id}): {e}")
            return False
    
    # ==================== UTILIDADES ====================
    
    def exists(self, id: int) -> bool:
        """Verifica si existe un registro"""
        try:
            with self.db_engine.get_session() as session:
                return session.query(self.model_class).filter_by(id=id).count() > 0
        except Exception as e:
            logger.error(f"Error en exists: {e}")
            return False
    
    def count(self, filters: Optional[Dict] = None) -> int:
        """Cuenta registros con filtros opcionales"""
        try:
            with self.db_engine.get_session() as session:
                query = session.query(self.model_class)
                
                if filters:
                    query = query.filter_by(**filters)
                
                return query.count()
        except Exception as e:
            logger.error(f"Error en count: {e}")
            return 0
    
    def _to_dict(self, entity) -> Dict:
        """Convierte una entidad SQLAlchemy a diccionario"""
        if entity is None:
            return {}
        
        # Usar inspector de SQLAlchemy
        mapper = inspect(entity)
        
        result = {}
        for column in mapper.mapper.column_attrs:
            value = getattr(entity, column.key)
            
            # Convertir datetime a string
            if isinstance(value, datetime):
                value = value.isoformat()
            
            result[column.key] = value
        
        # Agregar ID si existe
        if hasattr(entity, 'id'):
            result['id'] = entity.id
        
        return result
    
    def _invalidate_cache(self, id: Optional[int] = None):
        """Invalida el caché"""
        if id:
            # Invalidar solo el registro específico
            cache_key = f"{self.model_class.__name__}:{id}"
            self._cache.pop(cache_key, None)
        else:
            # Invalidar todo el caché del modelo
            prefix = f"{self.model_class.__name__}:"
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                self._cache.pop(key, None)
    
    def clear_cache(self):
        """Limpia todo el caché"""
        self._cache.clear()
        logger.debug(f"Cache cleared for {self.model_class.__name__}")
    
    def enable_cache(self):
        """Habilita el caché"""
        self._cache_enabled = True
    
    def disable_cache(self):
        """Deshabilita el caché"""
        self._cache_enabled = False
        self._cache.clear()
    
    # ==================== QUERY HELPERS ====================
    
    def find_one(self, **filters) -> Optional[Dict]:
        """Busca un solo registro por filtros"""
        try:
            with self.db_engine.get_session() as session:
                entity = session.query(self.model_class).filter_by(**filters).first()
                return self._to_dict(entity) if entity else None
        except Exception as e:
            logger.error(f"Error en find_one: {e}")
            return None
    
    def find_many(self, limit: Optional[int] = None, offset: int = 0, 
                  order_by: Optional[str] = None, **filters) -> List[Dict]:
        """Busca múltiples registros con paginación"""
        try:
            with self.db_engine.get_session() as session:
                query = session.query(self.model_class)
                
                # Aplicar filtros CON VALIDACIÓN
                if filters:
                    valid_filters = {}
                    
                    for key, value in filters.items():
                        if hasattr(self.model_class, key):
                            valid_filters[key] = value
                        else:
                            logger.warning(f"⚠️ Filtro ignorado: '{key}' no existe en {self.model_class.__name__}")
                    
                    if valid_filters:
                        query = query.filter_by(**valid_filters)
                    else:
                        logger.warning(f"⚠️ Ningún filtro válido para {self.model_class.__name__}")
                        
                # Ordenamiento
                if order_by:
                    if order_by.startswith('-'):
                        # Descendente
                        column = order_by[1:]
                        if hasattr(self.model_class, column):
                            query = query.order_by(getattr(self.model_class, column).desc())
                    else:
                        # Ascendente
                        if hasattr(self.model_class, order_by):
                            query = query.order_by(getattr(self.model_class, order_by))
                
                # Paginación
                if offset > 0:
                    query = query.offset(offset)
                if limit:
                    query = query.limit(limit)
                
                entities = query.all()
                results  = [self._to_dict(e) for e in entities]
        
                logger.debug(f"🔍 {self.model_class.__name__}.find_many() → {len(results)} resultados")
                return results
            
        except Exception as e:
            logger.error(f"❌ Error en find_many {self.model_class.__name__}: {e}", exc_info=True)
            return []
    
    def bulk_create(self, data_list: List[Dict]) -> int:
        """Crea múltiples registros en una transacción"""
        try:
            with self.db_engine.get_session() as session:
                entities = [self.model_class(**data) for data in data_list]
                session.bulk_save_objects(entities)
                session.commit()
                
                self._invalidate_cache()
                
                logger.info(f"✅ Bulk created {len(data_list)} {self.model_class.__name__}")
                return len(data_list)
        
        except Exception as e:
            logger.error(f"Error en bulk_create: {e}")
            return 0
    
    def bulk_update(self, updates: List[Dict]) -> int:
        """
        Actualiza múltiples registros.
        updates = [{'id': 1, 'campo': 'valor'}, ...]
        """
        try:
            count = 0
            with self.db_engine.get_session() as session:
                for update_data in updates:
                    id = update_data.pop('id')
                    entity = session.query(self.model_class).filter_by(id=id).first()
                    
                    if entity:
                        for key, value in update_data.items():
                            if hasattr(entity, key):
                                setattr(entity, key, value)
                        count += 1
                
                session.commit()
                self._invalidate_cache()
                
                logger.info(f"✅ Bulk updated {count} {self.model_class.__name__}")
                return count
        
        except Exception as e:
            logger.error(f"Error en bulk_update: {e}")
            return 0
    
    # ==================== TRANSACCIONES ====================
    
    def execute_in_transaction(self, func, *args, **kwargs):
        """
        Ejecuta una función dentro de una transacción.
        Si la función falla, hace rollback automático.
        """
        try:
            with self.db_engine.get_session() as session:
                result = func(session, *args, **kwargs)
                session.commit()
                self._invalidate_cache()
                return result
        
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise