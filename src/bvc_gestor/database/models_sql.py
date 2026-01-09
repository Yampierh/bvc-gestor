# src/bvc_gestor/database/models_sql.py
"""
Modelos SQLAlchemy para la base de datos
"""
from sqlalchemy import (
    Integer, String, Boolean, DateTime,
    Text, ForeignKey, Enum as SQLAlchemyEnum, Date, DECIMAL,
    CheckConstraint, Index, UniqueConstraint
)

from sqlalchemy.orm import relationship, validates, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import logging

from .engine import Base
from ..utils.validators_venezuela import validar_telefono, validar_rif, validar_nmro_cuenta_bancaria, validar_email
from ..utils.constants import (
    TipoInversor, EstadoOrden, TipoOrden
)

logger = logging.getLogger(__name__)

class AuditMixin:
    """Añade fechas de auditoría y estado a todas las tablas de forma automática"""
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    # El campo 'estatus' debe estar aquí para que todas las tablas tengan soft-delete
    estatus: Mapped[bool] = mapped_column(Boolean, default=True)

class BancoDB(Base, AuditMixin):
    """Modelo para bancos venezolanos"""
    __tablename__ = "bancos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    rif: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)  # RIF del banco
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # Nombre del banco
    codigo: Mapped[str] = mapped_column(String(4), unique=True, nullable=False) # Código del banco

class CasaBolsaDB(Base, AuditMixin):
    """Modelo para casas de bolsa venezolanas"""
    __tablename__ = "casas_bolsa"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    rif: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)  # RIF de la casa de bolsa
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # Nombre de la casa de bolsa
    sector: Mapped[str] = mapped_column(String(100), nullable=True) # Sector económico
    tipo_entidad: Mapped[str] = mapped_column(String(50), nullable=False) # Tipo de entidad: Casa de Bolsa, CVV, etc.

class ClienteDB(Base, AuditMixin):
    """Modelo SQLAlchemy para Clientes venezolanos"""
    __tablename__ = "clientes"
    
    # Identificación
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False) # Nombre completo o razón social
    tipo_inversor: Mapped[TipoInversor] = mapped_column(SQLAlchemyEnum(TipoInversor), nullable=False) # Natural o Jurídica
    rif_cedula: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False) # RIF o Cédula
    
    #Control de Vigencia
    fecha_vencimiento_rif: Mapped[Optional[date]] = mapped_column(Date, nullable=True) # Fecha de vencimiento del RIF
    
    # Perfil de Inversión
    perfil_riesgo: Mapped[str] = mapped_column(String(50), default="Moderado") # Conservador, Moderado, Agresivo
    
    # Contacto
    telefono: Mapped[str] = mapped_column(String(20), nullable=False) # Teléfono principal
    email: Mapped[str] = mapped_column(String(100), nullable=False) # Email principal
    direccion_fiscal: Mapped[str] = mapped_column(Text, nullable=False) # Dirección fiscal completa
    ciudad_estado: Mapped[str] = mapped_column(String(100), nullable=False) # Ciudad y estado de residencia
    
    # Relaciones
    cuentas_bancarias = relationship("CuentaBancariaDB", back_populates="cliente")
    cuentas = relationship("CuentaBursatilDB", back_populates="cliente")
    documentos = relationship("DocumentoDB", back_populates="cliente")
    
    # Índices
    __table_args__ = (
        Index('idx_cliente_nombre', 'nombre_completo'), # Índice para búsquedas por nombre
        Index('idx_cliente_rif', 'rif_cedula'), # Índice para búsquedas por RIF o cédula
        Index('idx_cliente_tipo_inversor', 'tipo_inversor'), # Índice para búsquedas por tipo de inversor
    )

    def validar_rif(self, key, rif_cedula): # Validar RIF
        if not validar_rif(rif_cedula):
            raise ValueError(f"RIF/Cédula inválido: {rif_cedula}")
        return rif_cedula
    
    @validates('telefono') # Validar teléfono principal
    def validate_telefono_principal(self, key, telefono):
        if not validar_telefono(telefono):
            raise ValueError(f"Teléfono inválido: {telefono}")
        return telefono
    
    @validates('email') # Validar formato de email
    def validate_email(self, key, email):
        """Validar formato de email"""
        if not validar_email(email):
            raise ValueError(f"Email inválido: {email}")
        return email
    
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'tipo_inversor': self.tipo_inversor.value,
            'rif_cedula': self.rif_cedula,
            'fecha_vencimiento_rif': self.fecha_vencimiento_rif,
            'perfil_riesgo': self.perfil_riesgo,
            'direccion_fiscal': self.direccion_fiscal,
            'ciudad_estado': self.ciudad_estado,
            'nombre_completo': self.nombre_completo,
            'telefono': self.telefono,
            'email': self.email,
            'fecha_registro': self.fecha_registro.isoformat(),
            'estatus': self.estatus
        }
    
    def __repr__(self):
        return f"<Cliente(id='{self.id}', nombre='{self.nombre_completo}')>"

class CuentaBancariaDB(Base, AuditMixin):
    """Cuentas bancarias asociadas a clientes"""
    __tablename__ = "cuentas_bancarias"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    banco_id: Mapped[int] = mapped_column(ForeignKey("bancos.id"), nullable=False)
    
    numero_cuenta: Mapped[str] = mapped_column(String(20), unique=True, nullable=False) # Número de cuenta bancaria
    tipo_cuenta: Mapped[str] = mapped_column(String(30), default="Ahorros") # Ahorros, Corriente, Nómina
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="cuentas_bancarias")
    banco = relationship("BancoDB")
    
    @validates('numero_cuenta') # Validar número de cuenta bancaria
    def validate_numero_cuenta(self, key, numero_cuenta):
        if not validar_nmro_cuenta_bancaria(numero_cuenta):
            raise ValueError(f"Número de cuenta bancaria inválido: {numero_cuenta}")
        return numero_cuenta

class CuentaBursatilDB(Base, AuditMixin):
    """Cuentas registradas en Casas de Bolsa y Caja Venezolana de Valores"""
    __tablename__ = "cuentas_bursatiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False) # Cliente asociado
    casa_bolsa_id: Mapped[int] = mapped_column(ForeignKey("casas_bolsa.id"), nullable=False) # Casa de bolsa asociada
    
    # El dato más importante
    subcuenta_cvv: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # ID en la Caja Venezolana de Valores
    tipo_cuenta: Mapped[str] = mapped_column(String(30), default="Individual") # Individual, Conjunta, Jurídica
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="cuentas")
    saldos = relationship("SaldoDB", back_populates="cuenta", cascade="all, delete-orphan")
    movimientos = relationship("MovimientoDB", back_populates="cuenta")
    
    # Índices y restricciones 
    __table_args__ = (
        Index('idx_cuenta_cliente', 'cliente_id'),
        Index('idx_cuenta_casa_bolsa', 'casa_bolsa_id'),
        Index('idx_subcuenta_cvv', 'subcuenta_cvv')
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'subcuenta_cvv': self.subcuenta_cvv,
            'cliente_id': self.cliente_id,
            'tipo_cuenta': self.tipo_cuenta,
            'casa_bolsa_id': self.casa_bolsa_id
        }

class SaldoDB(Base, AuditMixin):
    """Balances por moneda para cada cuenta bursátil"""
    __tablename__ = "saldos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bursatiles.id"), nullable=False)
    
    moneda: Mapped[str] = mapped_column(String(3), nullable=False) # 'VES', 'USD', 'EUR'
    
    # Saldo que el cliente puede usar ya mismo
    disponible: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0)
    
    # Dinero comprometido en órdenes de compra que aún no se han ejecutado
    bloqueado: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0)
    
    cuenta = relationship("CuentaBursatilDB", back_populates="saldos")
    
    __table_args__ = (
        UniqueConstraint('cuenta_id', 'moneda', name='uq_cuenta_moneda'),
    )

class ActivoDB(Base, AuditMixin):
    """Acciones, Bonos y otros títulos de la BVC"""
    __tablename__ = "activos"
    
    # Identificación del activo
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    rif: Mapped[str] = mapped_column(String(15), nullable=False)  # RIF
    nombre: Mapped[str] = mapped_column(String(150), nullable=False) # Nombre completo del activo
    ticker: Mapped[str] = mapped_column(String(20), unique=True, nullable=False) # Símbolo en la bolsa
    sector: Mapped[str] = mapped_column(String(100), nullable=True) # Sector económico
    

    ordenes = relationship("OrdenDB", back_populates="activo") # Órdenes asociadas al activo

    __table_args__ = (
        Index('idx_activo_nombre', 'nombre'),
        Index('idx_activo_sector', 'sector'),
        Index('idx_activo_ticker', 'ticker'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'rif': self.rif,
            'nombre': self.nombre,
            'estatus': self.estatus
        }

class OrdenDB(Base, AuditMixin):
    """Instrucción de compra o venta"""
    __tablename__ = "ordenes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bursatiles.id"), nullable=False)
    activo_id: Mapped[str] = mapped_column(ForeignKey("activos.ticker"), nullable=False)
    
    tipo: Mapped[TipoOrden] = mapped_column(SQLAlchemyEnum(TipoOrden)) # Compra o Venta
    cantidad_total: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_limite: Mapped[Decimal] = mapped_column(DECIMAL(20, 8)) # El precio máximo/mínimo que acepta
    
    estado: Mapped[EstadoOrden] = mapped_column(SQLAlchemyEnum(EstadoOrden), default="Pendiente")
    fecha_vencimiento: Mapped[date] = mapped_column(Date)
    
    # Relaciones
    transacciones = relationship("TransaccionDB", back_populates="orden") # Transacciones asociadas a la orden
    activo = relationship("ActivoDB", back_populates="ordenes") # Activo asociado
    
    # Índices y restricciones
    __table_args__ = (
        Index('idx_orden_cliente', 'cliente_id'), # Índice para búsquedas por cliente
        Index('idx_orden_activo', 'activo_id'), # Índice para búsquedas por activo
        Index('idx_orden_estado', 'estado'), # Índice para búsquedas por estado
        Index('idx_orden_fecha', 'fecha_registro'), # Índice para búsquedas por fecha
    )

    
    def to_dict(self): # Convertir a diccionario
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'cantidad_total': self.cantidad_total,
            'precio_limite': float(self.precio_limite),
            'cliente_id': self.cliente_id,
            'activo_id': self.activo_id,
            'estado': self.estado.value,
            'fecha_creacion': self.fecha_registro.isoformat(),
        }

class TransaccionDB(Base, AuditMixin):
    """El 'calce' real en la bolsa con su desglose legal"""
    __tablename__ = "transacciones"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    
    cantidad_ejecutada: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_ejecucion: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    monto_bruto: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False) # Cantidad x Precio
    
    # Desglose de Comisiones (Crucial para el software)
    comision_corretaje: Mapped[Decimal] = mapped_column(DECIMAL(20, 8))
    comision_bvc: Mapped[Decimal] = mapped_column(DECIMAL(20, 8))
    comision_cvv: Mapped[Decimal] = mapped_column(DECIMAL(20, 8))
    iva: Mapped[Decimal] = mapped_column(DECIMAL(20, 8))
    
    monto_neto: Mapped[Decimal] = mapped_column(DECIMAL(20, 8)) # Monto final cobrado/pagado
    
    tasa_bcv: Mapped[Decimal] = mapped_column(DECIMAL(20, 4)) # Tasa del momento del calce
    numero_operacion_bvc: Mapped[str] = mapped_column(String(50)) # ID que da la bolsa
    
    orden = relationship("OrdenDB", back_populates="transacciones")
    
    # Índices y restricciones
    __table_args__ = (
        Index('idx_transaccion_fecha', 'fecha_registro'), # Índice para búsquedas por fecha
        Index('idx_transaccion_numero_bvc', 'numero_operacion_bvc'), # Índice para búsquedas por número de operación BVC
        CheckConstraint('cantidad_ejecutada > 0', name='check_transaccion_cantidad'), # Cantidad debe ser positiva
        CheckConstraint('precio_ejecucion > 0', name='check_precio_positivo'), # Precio unitario debe ser positivo
    )
    
    def to_dict(self): # Convertir a diccionario
        return {
            'id': self.id,
            'orden_id': self.orden_id,
            'cantidad_ejecutada': self.cantidad_ejecutada,
            'precio_ejecucion': float(self.precio_ejecucion),
            'monto_bruto': float(self.monto_bruto),
            'comision_corretaje': float(self.comision_corretaje),
            'monto_neto': float(self.monto_neto),
            'numero_operacion_bvc': self.numero_operacion_bvc,
            'fecha_registro': self.fecha_registro.isoformat()
        }

class PortafolioItemDB(Base, AuditMixin):
    """Resumen consolidado de activos por cuenta"""
    __tablename__ = "portafolio_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bursatiles.id"), nullable=False)
    activo_id: Mapped[str] = mapped_column(ForeignKey("activos.ticker"), nullable=False)
    
    cantidad: Mapped[int] = mapped_column(Integer, default=0) # Total de acciones que posee
    
    # El "Costo Promedio" es vital para saber si hay ganancia o pérdida
    costo_promedio: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0) 
    
    # Relaciones
    cuenta = relationship("CuentaBursatilDB")
    activo = relationship("ActivoDB")
    
    
    # Índices y restricciones
    __table_args__ = (
        Index('idx_portafolio_cuenta', 'cuenta_id'),
        Index('idx_portafolio_activo', 'activo_id'),
        UniqueConstraint('cuenta_id', 'activo_id', name='uq_cuenta_activo'),
    )
    
    @hybrid_property
    def porcentaje_portafolio(self):
        # Esto se calcula en relación al total del portafolio
        return 0.0  # Se calcula dinámicamente
    
    def to_dict(self): # Convertir a diccionario
        return {
            'id': self.id,
            'cuenta_id': self.cuenta_id,
            'activo_id': self.activo_id,
            'cantidad': self.cantidad,
            'costo_promedio': float(self.costo_promedio),
            'fecha_registro': self.fecha_registro.isoformat()
}

class MovimientoDB(Base, AuditMixin):
    """Registro de depósitos, retiros y cobro de comisiones"""
    __tablename__ = "movimientos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True) # ID interno
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bursatiles.id"), nullable=False) # Cuenta asociada
    
    tipo: Mapped[str] = mapped_column(String(20)) # 'Deposito', 'Retiro', 'Comision', 'Dividendo'
    monto: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False)
    tasa_bcv: Mapped[Decimal] = mapped_column(DECIMAL(20, 4), nullable=False) # Tasa del día del movimiento
    referencia: Mapped[Optional[str]] = mapped_column(String(100)) # Número de transferencia bancaria
    
    cuenta = relationship("CuentaBursatilDB", back_populates="movimientos")
    
    def to_dict(self): # Convertir a diccionario
        return {
            'id': self.id,
            'cuenta_id': self.cuenta_id,
            'tipo': self.tipo,
            'monto': float(self.monto),
            'moneda': self.moneda,
            'tasa_bcv': float(self.tasa_bcv),
            'fecha_registro': self.fecha_registro.isoformat()
        }

class DocumentoDB(Base, AuditMixin):
    """Modelo para documentos de clientes"""
    __tablename__ = "documentos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False) # Cliente asociado
    
    # Información del documento
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False)  # Cédula, RIF, Estados de cuenta, etc.
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False) # Nombre original del archivo
    ruta_archivo: Mapped[str] = mapped_column(String(500), nullable=False) # Ruta en el sistema de archivos o URL
    fecha_subida: Mapped[datetime] = mapped_column(DateTime, default=func.now()) # Fecha de subida del documento
    verificado: Mapped[bool] = mapped_column(Boolean, default=False) # Si el documento ha sido verificado
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="documentos")
    
    __table_args__ = (
        Index('idx_documento_cliente', 'cliente_id'),
        Index('idx_documento_tipo', 'tipo_documento'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'tipo_documento': self.tipo_documento,
            'nombre_archivo': self.nombre_archivo,
            'fecha_subida': self.fecha_subida.isoformat(),
            'verificado': self.verificado
        }

class PrecioHistoricoDB(Base):
    """Historial de precios de cierre para análisis de mercado"""
    __tablename__ = "precios_historicos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activo_id: Mapped[str] = mapped_column(ForeignKey("activos.ticker"), nullable=False)
    
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    precio_cierre: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    tasa_bcv: Mapped[Decimal] = mapped_column(DECIMAL(20, 4), nullable=False) # Para ver el precio en $ de ese día
    
    __table_args__ = (
        Index('idx_precio_activo_fecha', 'activo_id', 'fecha'),
    )

class ConfiguracionComisionesDB(Base, AuditMixin):
    """Tasas vigentes para cálculos automáticos"""
    __tablename__ = "config_comisiones"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50)) # 'Corretaje', 'BVC', 'CVV', 'IVA'
    valor_porcentaje: Mapped[Decimal] = mapped_column(DECIMAL(10, 4)) # Ej: 0.0100 para 1%
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

class ConfiguracionDB(Base, AuditMixin):
    """Modelo para configuración de la aplicación"""
    __tablename__ = "configuraciones"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    clave: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # Clave única de configuración
    valor: Mapped[str] = mapped_column(Text, nullable=False) # Valor almacenado como string
    tipo: Mapped[str] = mapped_column(String(20), default='string')  # string, number, boolean, json
    categoria: Mapped[str] = mapped_column(String(50), default='General') # Categoría de la configuración
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Descripción de la configuración
    editable: Mapped[bool] = mapped_column(Boolean, default=True) # Si puede ser editada desde la UI
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=func.now()) # Fecha de creación
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now()) # Fecha de última actualización
    
    # Índices
    __table_args__ = (
        Index('idx_config_clave', 'clave'), # Índice para búsquedas por clave
        Index('idx_config_categoria', 'categoria'), # Índice para búsquedas por categoría
    )
    
    def get_value(self):
        """Obtener valor convertido según tipo"""
        if self.tipo == 'number':
            try:
                return float(self.valor)
            except ValueError:
                return 0.0
        elif self.tipo == 'boolean':
            return self.valor.lower() in ('true', '1', 'yes', 'si')
        elif self.tipo == 'json':
            try:
                import json
                return json.loads(self.valor)
            except:
                return {}
        else:
            return self.valor
    
    def to_dict(self): # Convertir a diccionario
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.get_value(),
            'tipo': self.tipo,
            'categoria': self.categoria,
            'descripcion': self.descripcion,
            'editable': self.editable
        }