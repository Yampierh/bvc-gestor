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
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import logging

from .engine import Base
from ..utils.constants import (
    TipoInversor, EstadoOrden, TipoOrden, 
    TipoMovimiento, EstadoMovimiento
)

logger = logging.getLogger(__name__)

class AuditMixin:
    """Añade fechas de auditoría y estado a todas las tablas de forma automática"""
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    # El campo 'estatus' debe estar aquí para que todas las tablas tengan soft-delete
    estatus: Mapped[bool] = mapped_column(Boolean, default=True)

#  TABLAS CATÁLOGO
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
    tipo: Mapped[str] = mapped_column(String(50), nullable=False) # Tipo de entidad: Casa de Bolsa, CVV, etc.

#  CLIENTES Y CUENTAS
class ClienteDB(Base, AuditMixin):
    """Modelo SQLAlchemy para Clientes venezolanos"""
    __tablename__ = "clientes"
    
    # Identificación
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False) # Nombre completo o razón social
    tipo_inversor: Mapped[TipoInversor] = mapped_column(SQLAlchemyEnum(TipoInversor), nullable=False) # Natural o Jurídica
    rif_cedula: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False) # RIF o Cédula
    fecha_vencimiento_rif: Mapped[datetime] = mapped_column(DateTime)
    # Perfil de Inversión
    #perfil_riesgo: Mapped[str] = mapped_column(String(50), default="Moderado") # Conservador, Moderado, Agresivo
    
    # Contacto
    telefono: Mapped[str] = mapped_column(String(20), nullable=False) # Teléfono principal
    email: Mapped[str] = mapped_column(String(100), nullable=False) # Email principal
    direccion_fiscal: Mapped[str] = mapped_column(Text, nullable=False) # Dirección fiscal completa
    ciudad_estado: Mapped[str] = mapped_column(String(100), nullable=False) # Ciudad y estado de residencia
    
    # Relaciones
    cuentas_bancarias = relationship("CuentaBancariaDB", back_populates="cliente")
    cuentas_bursatiles = relationship("CuentaBursatilDB", back_populates="cliente")
    documentos = relationship("DocumentoDB", back_populates="cliente")
    ordenes = relationship("OrdenDB", back_populates="cliente")
    
    # Índices
    __table_args__ = (
        Index('idx_cliente_nombre', 'nombre_completo'), # Índice para búsquedas por nombre
        Index('idx_cliente_rif', 'rif_cedula'), # Índice para búsquedas por RIF o cédula
        Index('idx_cliente_tipo_inversor', 'tipo_inversor'), # Índice para búsquedas por tipo de inversor
    )
    
    # Convertir a diccionario
    def to_dict(self):
        return {
            'id': self.id,
            'tipo_inversor': self.tipo_inversor.value,
            'rif_cedula': self.rif_cedula,
            'direccion_fiscal': self.direccion_fiscal,
            'ciudad_estado': self.ciudad_estado,
            'nombre_completo': self.nombre_completo,
            'telefono': self.telefono,
            'email': self.email,
            'fecha_registro': self.fecha_registro.isoformat(),
            'estatus': self.estatus
        }


class CuentaBancariaDB(Base, AuditMixin):
    """Cuentas bancarias asociadas a clientes"""
    __tablename__ = "cuentas_bancarias"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    banco_id: Mapped[int] = mapped_column(ForeignKey("bancos.id"), nullable=False)
    numero_cuenta: Mapped[str] = mapped_column(String(20), unique=True, nullable=False) # Número de cuenta bancaria
    tipo_cuenta: Mapped[str] = mapped_column(String(30), default="Corriente") # Ahorros, Corriente, Nómina
    default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="cuentas_bancarias")
    banco = relationship("BancoDB")
    movimientos = relationship("MovimientoDB", back_populates="cuenta_bancaria")


class CuentaBursatilDB(Base, AuditMixin):
    """Cuentas registradas en Casas de Bolsa y Caja Venezolana de Valores"""
    __tablename__ = "cuentas_bursatiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False) # Cliente asociado
    casa_bolsa_id: Mapped[int] = mapped_column(ForeignKey("casas_bolsa.id"), nullable=False) # Casa de bolsa asociada
    cuenta: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # Numero de Cuenta
    default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relaciones
    cliente = relationship("ClienteDB", back_populates="cuentas_bursatiles")
    casa_bolsa = relationship("CasaBolsaDB")
    saldos = relationship("SaldoDB", back_populates="cuenta", cascade="all, delete-orphan")
    movimientos = relationship("MovimientoDB", back_populates="cuenta_bursatil")
    ordenes = relationship("OrdenDB", back_populates="cuenta")  # NUEVO
    portafolio = relationship("PortafolioItemDB", back_populates="cuenta")  # NUEVO
    
    __table_args__ = (
        Index('idx_cuenta_cliente', 'cliente_id'),
        Index('idx_cuenta_casa_bolsa', 'casa_bolsa_id'),
        Index('idx_cuenta', 'cuenta')
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'cuenta': self.cuenta,
            'cliente_id': self.cliente_id,
            'casa_bolsa_id': self.casa_bolsa_id
        }


class SaldoDB(Base, AuditMixin):
    """Balances por moneda para cada cuenta bursátil"""
    __tablename__ = "saldos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bursatiles.id"), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default='VES') # 'VES', 'USD', 'EUR'
    
    # Saldo que el cliente puede usar ya mismo
    disponible: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0)
    
    # Dinero en camino (depósitos pendientes de confirmar)
    en_transito: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0)
    
    # Dinero comprometido en órdenes de compra que aún no se han ejecutado
    bloqueado: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0)
    
    cuenta = relationship("CuentaBursatilDB", back_populates="saldos")
    
    __table_args__ = (
        UniqueConstraint('cuenta_id', 'moneda', name='uq_cuenta_moneda'),
        CheckConstraint('disponible >= 0', name='check_disponible_positivo'),
        CheckConstraint('en_transito >= 0', name='check_transito_positivo'),
        CheckConstraint('bloqueado >= 0', name='check_bloqueado_positivo'),
    )
    
    @property
    def saldo_proyectado(self) -> Decimal:
        """Saldo total proyectado: disponible + en_transito - bloqueado"""
        return self.disponible + self.en_transito - self.bloqueado
    
    def to_dict(self):
        return {
            'id': self.id,
            'cuenta_id': self.cuenta_id,
            'moneda': self.moneda,
            'disponible': float(self.disponible),
            'en_transito': float(self.en_transito),
            'bloqueado': float(self.bloqueado),
            'saldo_proyectado': float(self.saldo_proyectado)
        }


class ActivoDB(Base, AuditMixin):
    """Acciones, Bonos y otros títulos de la BVC"""
    __tablename__ = "activos"
    
    # Identificación del activo
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    rif: Mapped[str] = mapped_column(String(15), nullable=False)  # RIF
    nombre: Mapped[str] = mapped_column(String(150), nullable=False) # Nombre completo del activo
    ticker: Mapped[str] = mapped_column(String(20), unique=True, nullable=False) # Símbolo en la bolsa
    sector: Mapped[str] = mapped_column(String(100), nullable=True) # Sector económico
    mercado: Mapped[str] = mapped_column(String(50), default='Acciones')  # 'Acciones', 'Bonos', 'ETF'
    precio_actual: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)
    fecha_actualizacion_precio: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estado_mercado: Mapped[bool] = mapped_column(Boolean, default=True)  # Activo/Suspendido en BVC

    # Relaciones
    ordenes = relationship("OrdenDB", back_populates="activo")
    portafolio_items = relationship("PortafolioItemDB", back_populates="activo")
    precios_actuales = relationship("PrecioActualDB", back_populates="activo")
    precios_historicos = relationship("PrecioHistoricoDB", back_populates="activo")

    __table_args__ = (
        Index('idx_activo_nombre', 'nombre'),
        Index('idx_activo_sector', 'sector'),
        Index('idx_activo_ticker', 'ticker'),
        Index('idx_activo_mercado', 'mercado'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'rif': self.rif,
            'nombre': self.nombre,
            'ticker': self.ticker,
            'sector': self.sector,
            'mercado': self.mercado,
            'precio_actual': float(self.precio_actual) if self.precio_actual else None,
            'fecha_actualizacion_precio': self.fecha_actualizacion_precio.isoformat() if self.fecha_actualizacion_precio else None,
            'estado_mercado': self.estado_mercado,
            'estatus': self.estatus
        }


class MovimientoDB(Base, AuditMixin):
    """
    Registro de depósitos, retiros y otros movimientos de fondos
    """
    __tablename__ = "movimientos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cuenta_bursatil_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bursatiles.id"), nullable=False)
    cuenta_bancaria_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bancarias.id"), nullable=False)
    
    tipo: Mapped[TipoMovimiento] = mapped_column(SQLAlchemyEnum(TipoMovimiento), nullable=False)
    monto: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default='VES')
    
    estado: Mapped[EstadoMovimiento] = mapped_column(
        SQLAlchemyEnum(EstadoMovimiento), 
        default=EstadoMovimiento.PENDIENTE
    )
    
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_completado: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Para auditoría
    referencia_bancaria: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    comprobante_ruta: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tasa_bcv: Mapped[Decimal] = mapped_column(DECIMAL(20, 4), nullable=False)
    
    # Relaciones
    cuenta_bursatil = relationship("CuentaBursatilDB", back_populates="movimientos")
    cuenta_bancaria = relationship("CuentaBancariaDB", back_populates="movimientos")
    ordenes_vinculadas = relationship("OrdenMovimientoDB", back_populates="movimiento")
    
    __table_args__ = (
        Index('idx_movimiento_fecha', 'fecha_solicitud'),
        Index('idx_movimiento_estado', 'estado'),
        Index('idx_movimiento_tipo', 'tipo'),
        Index('idx_movimiento_cuenta_bursatil', 'cuenta_bursatil_id'),
        CheckConstraint('monto > 0', name='check_movimiento_monto_positivo'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'cuenta_bursatil_id': self.cuenta_bursatil_id,
            'cuenta_bancaria_id': self.cuenta_bancaria_id,
            'tipo': self.tipo.value,
            'monto': float(self.monto),
            'moneda': self.moneda,
            'estado': self.estado.value,
            'fecha_solicitud': self.fecha_solicitud.isoformat(),
            'fecha_completado': self.fecha_completado.isoformat() if self.fecha_completado else None,
            'referencia_bancaria': self.referencia_bancaria,
            'tasa_bcv': float(self.tasa_bcv)
        }


class OrdenDB(Base, AuditMixin):
    """Instrucción de compra o venta"""
    __tablename__ = "ordenes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bursatiles.id"), nullable=False)
    cuenta_bancaria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cuentas_bancarias.id"), nullable=True)
    activo_id: Mapped[str] = mapped_column(ForeignKey("activos.id"), nullable=False)
    tipo: Mapped[TipoOrden] = mapped_column(SQLAlchemyEnum(TipoOrden)) # Compra o Venta
    cantidad_total: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_limite: Mapped[Decimal] = mapped_column(DECIMAL(20, 8)) # El precio máximo/mínimo que acepta
    estado: Mapped[EstadoOrden] = mapped_column(SQLAlchemyEnum(EstadoOrden), default="Pendiente")
    fecha_vencimiento: Mapped[date] = mapped_column(Date)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comision_estimada: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)
    monto_total_estimado: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="ordenes")
    cuenta = relationship("CuentaBursatilDB", back_populates="ordenes")
    cuenta_bancaria = relationship("CuentaBancariaDB")
    activo = relationship("ActivoDB", back_populates="ordenes")
    transacciones = relationship("TransaccionDB", back_populates="orden")
    movimientos_vinculados = relationship("OrdenMovimientoDB", back_populates="orden")
    
    __table_args__ = (
        Index('idx_orden_cliente', 'cliente_id'),
        Index('idx_orden_activo', 'activo_id'),
        Index('idx_orden_estado', 'estado'),
        Index('idx_orden_fecha', 'fecha_registro'),
        Index('idx_orden_cuenta', 'cuenta_id'),
        CheckConstraint('cantidad_total > 0', name='check_orden_cantidad'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'cantidad_total': self.cantidad_total,
            'precio_limite': float(self.precio_limite) if self.precio_limite else None,
            'cliente_id': self.cliente_id,
            'cuenta_id': self.cuenta_id,
            'activo_id': self.activo_id,
            'estado': self.estado.value,
            'fecha_creacion': self.fecha_registro.isoformat(),
            'comision_estimada': float(self.comision_estimada) if self.comision_estimada else None,
            'monto_total_estimado': float(self.monto_total_estimado) if self.monto_total_estimado else None,
        }


class OrdenMovimientoDB(Base, AuditMixin):
    """
    Relación entre órdenes y movimientos de fondos
    NUEVA: Para vincular depósitos con órdenes que los requieren
    """
    __tablename__ = "ordenes_movimientos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    movimiento_id: Mapped[int] = mapped_column(ForeignKey("movimientos.id"), nullable=False)
    tipo_relacion: Mapped[str] = mapped_column(String(30), nullable=False)
    # Valores: 'DEPOSITO_PARA_COMPRA', 'RETIRO_POST_VENTA'
    
    # Relaciones
    orden = relationship("OrdenDB", back_populates="movimientos_vinculados")
    movimiento = relationship("MovimientoDB", back_populates="ordenes_vinculadas")
    
    __table_args__ = (
        Index('idx_orden_movimiento_orden', 'orden_id'),
        Index('idx_orden_movimiento_movimiento', 'movimiento_id'),
    )


class TransaccionDB(Base, AuditMixin):
    """El 'calce' real en la bolsa con su desglose legal"""
    __tablename__ = "transacciones"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    
    cantidad_ejecutada: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_ejecucion: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    monto_bruto: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False) # Cantidad x Precio
    
    # Desglose de Comisiones (Crucial para el software)
    comision_corretaje: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0)
    comision_bvc: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0)
    comision_cvv: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0)
    iva: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0)
    
    monto_neto: Mapped[Decimal] = mapped_column(DECIMAL(20, 8)) # Monto final cobrado/pagado
    
    tasa_bcv: Mapped[Decimal] = mapped_column(DECIMAL(20, 4)) # Tasa del momento del calce
    numero_operacion_bvc: Mapped[str] = mapped_column(String(50), nullable=True) # ID que da la bolsa
    
    orden = relationship("OrdenDB", back_populates="transacciones")
    
    __table_args__ = (
        Index('idx_transaccion_fecha', 'fecha_registro'),
        Index('idx_transaccion_numero_bvc', 'numero_operacion_bvc'),
        Index('idx_transaccion_orden', 'orden_id'),
        CheckConstraint('cantidad_ejecutada > 0', name='check_transaccion_cantidad'),
        CheckConstraint('precio_ejecucion > 0', name='check_precio_positivo'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'orden_id': self.orden_id,
            'cantidad_ejecutada': self.cantidad_ejecutada,
            'precio_ejecucion': float(self.precio_ejecucion),
            'monto_bruto': float(self.monto_bruto),
            'comision_corretaje': float(self.comision_corretaje),
            'comision_bvc': float(self.comision_bvc),
            'comision_cvv': float(self.comision_cvv),
            'iva': float(self.iva),
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
    costo_promedio: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.0) 
    
    # Relaciones
    cuenta = relationship("CuentaBursatilDB", back_populates="portafolio")
    activo = relationship("ActivoDB", back_populates="portafolio_items")
    
    __table_args__ = (
        Index('idx_portafolio_cuenta', 'cuenta_id'),
        Index('idx_portafolio_activo', 'activo_id'),
        UniqueConstraint('cuenta_id', 'activo_id', name='uq_cuenta_activo'),
        CheckConstraint('cantidad >= 0', name='check_cantidad_no_negativa'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'cuenta_id': self.cuenta_id,
            'activo_id': self.activo_id,
            'cantidad': self.cantidad,
            'costo_promedio': float(self.costo_promedio),
            'fecha_registro': self.fecha_registro.isoformat()
        }


class PrecioActualDB(Base, AuditMixin):
    """
    Precio actual y datos de mercado en tiempo real
    """
    __tablename__ = "precios_actuales"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activo_id: Mapped[int] = mapped_column(ForeignKey("activos.id"), nullable=False)
    
    precio: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    volumen: Mapped[int] = mapped_column(Integer, default=0)
    variacion: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), default=0.0)  # Porcentaje
    
    precio_apertura: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)
    precio_maximo: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)
    precio_minimo: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)
    
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fuente: Mapped[str] = mapped_column(String(50), default='MANUAL')  # 'SCRAPING_BVC', 'MANUAL', 'API'
    
    # Relaciones
    activo = relationship("ActivoDB", back_populates="precios_actuales")
    
    __table_args__ = (
        Index('idx_precio_actual_activo', 'activo_id'),
        Index('idx_precio_actual_fecha', 'fecha_hora'),
        CheckConstraint('precio > 0', name='check_precio_actual_positivo'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'activo_id': self.activo_id,
            'precio': float(self.precio),
            'volumen': self.volumen,
            'variacion': float(self.variacion),
            'precio_apertura': float(self.precio_apertura) if self.precio_apertura else None,
            'precio_maximo': float(self.precio_maximo) if self.precio_maximo else None,
            'precio_minimo': float(self.precio_minimo) if self.precio_minimo else None,
            'fecha_hora': self.fecha_hora.isoformat(),
            'fuente': self.fuente
        }


class PrecioHistoricoDB(Base):
    """Historial de precios de cierre para análisis de mercado"""
    __tablename__ = "precios_historicos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activo_id: Mapped[int] = mapped_column(ForeignKey("activos.id"), nullable=False)
    
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    precio_cierre: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    tasa_bcv: Mapped[Decimal] = mapped_column(DECIMAL(20, 4), nullable=False)
    
    # Relaciones
    activo = relationship("ActivoDB", back_populates="precios_historicos")
    
    __table_args__ = (
        Index('idx_precio_historico_activo_fecha', 'activo_id', 'fecha'),
        UniqueConstraint('activo_id', 'fecha', name='uq_activo_fecha'),
        CheckConstraint('precio_cierre > 0', name='check_precio_historico_positivo'),
    )


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