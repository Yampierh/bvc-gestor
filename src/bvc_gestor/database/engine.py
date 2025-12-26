# src/bvc_gestor/database/engine.py
"""
Motor de base de datos SQLite con SQLAlchemy
"""
import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
from typing import Optional
import logging

from ..utils.constants import DATABASE_DIR
from ..utils.logger import logger

# Base para modelos SQLAlchemy
Base = declarative_base()

class DatabaseEngine:
    """Motor de base de datos SQLite"""
    
    _instance = None
    _engine = None
    _SessionLocal = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._engine:
            self._initialize()
    
    def _initialize(self):
        """Inicializar motor de base de datos"""
        try:
            # Ruta de la base de datos
            db_path = DATABASE_DIR / "bvc_gestor.db"
            
            # Crear directorio si no existe
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # String de conexión SQLite
            db_url = f"sqlite:///{db_path}"
            
            # Crear engine con configuración optimizada
            self._engine = create_engine(
                db_url,
                echo=False,  # Cambiar a True para debug
                poolclass=StaticPool,  # Para SQLite
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,
                },
                # Configuración para mejor rendimiento
                isolation_level="SERIALIZABLE",
            )
            
            # Configurar conexión
            @event.listens_for(self._engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
                cursor.execute("PRAGMA synchronous = NORMAL")
                cursor.execute("PRAGMA cache_size = -2000")  # 2MB cache
                cursor.close()
            
            # Crear session factory
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            logger.info(f"Base de datos inicializada en: {db_path}")
            
            # Probar conexión inmediatamente
            self.test_connection()
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {str(e)}")
            raise
    
    @property
    def engine(self):
        """Obtener engine de SQLAlchemy"""
        return self._engine
    
    @property
    def SessionLocal(self):
        """Obtener factory de sesiones"""
        return self._SessionLocal
    
    def get_session(self) -> Session:
        """Obtener nueva sesión de base de datos"""
        if not self._SessionLocal:
            self._initialize()
        return self._SessionLocal()
    
    def create_tables(self):
        """Crear todas las tablas en la base de datos"""
        try:
            Base.metadata.create_all(bind=self._engine)
            logger.info("Tablas creadas exitosamente")
        except Exception as e:
            logger.error(f"Error creando tablas: {str(e)}")
            raise
    
    def drop_tables(self):
        """Eliminar todas las tablas (solo desarrollo)"""
        try:
            Base.metadata.drop_all(bind=self._engine)
            logger.warning("Todas las tablas eliminadas")
        except Exception as e:
            logger.error(f"Error eliminando tablas: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Probar conexión a la base de datos"""
        try:
            with self._engine.connect() as conn:
                # Usar text() para crear una sentencia SQL ejecutable
                result = conn.execute(text("SELECT 1")).fetchone()
                connected = result[0] == 1
                if connected:
                    logger.info("✓ Conexión a base de datos exitosa")
                return connected
        except Exception as e:
            logger.error(f"Error probando conexión: {str(e)}")
            return False

# Singleton para acceso global
def get_database() -> DatabaseEngine:
    """Obtener instancia del motor de base de datos"""
    return DatabaseEngine()

def get_db():
    """
    Dependency para FastAPI (futuro) o para uso en servicios
    Yields una sesión de base de datos
    """
    db = get_database().get_session()
    try:
        yield db
    finally:
        db.close()