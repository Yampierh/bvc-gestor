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
import re
import logging

from .engine import Base
from ..utils.validators_venezuela import (
    validar_cedula, validar_rif, validar_telefono_venezolano
)
from ..utils.constants import (
    TipoPersona, TipoDocumento, PerfilRiesgo,
    EstadoOrden, TipoOrden, TipoOperacion, Moneda
)

logger = logging.getLogger(__name__)

class AuditMixin:
    """Añade fechas de auditoría y estado a todas las tablas de forma automática"""
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    # El campo 'activo' debe estar aquí para que todas las tablas tengan soft-delete
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

class BancoDB(Base, AuditMixin):
    """Modelo para bancos venezolanos"""
    __tablename__ = "bancos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    rif: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)  # RIF del banco
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # Nombre del banco
    codigo_banco: Mapped[Optional[str]] = mapped_column(String(10), nullable=True) # Código del banco
    pais: Mapped[str] = mapped_column(String(50), default="Venezuela") # País del banco
    activo: Mapped[bool] = mapped_column(Boolean, default=True) # Estado del banco en el sistema
    
    def __repr__(self):
        return f"<Banco(id='{self.id}', nombre='{self.nombre}')>"

class CasaBolsaDB(Base, AuditMixin):
    """Modelo para casas de bolsa venezolanas"""
    __tablename__ = "casas_bolsa"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    rif: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)  # RIF de la casa de bolsa
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # Nombre de la casa de bolsa
    codigo_casa: Mapped[Optional[str]] = mapped_column(String(10), nullable=True) # Código de la casa de bolsa
    pais: Mapped[str] = mapped_column(String(50), default="Venezuela") # País de la casa de bolsa
    activo: Mapped[bool] = mapped_column(Boolean, default=True) # Estado en el sistema
    
    def __repr__(self):
        return f"<CasaBolsa(id='{self.id}', nombre='{self.nombre}')>"

class ClienteDB(Base, AuditMixin):
    """Modelo SQLAlchemy para Clientes venezolanos"""
    __tablename__ = "clientes"
    
    # Identificación
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    documento_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False) # Cédula, RIF o Pasaporte
    tipo_persona: Mapped[TipoPersona] = mapped_column(SQLAlchemyEnum(TipoPersona), nullable=False) # Natural o Jurídica
    tipo_documento: Mapped[TipoDocumento] = mapped_column(SQLAlchemyEnum(TipoDocumento), nullable=False) # Cédula, RIF, Pasaporte
    
    # Información personal
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False) # Nombre completo o razón social
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True) # Nullable para personas jurídicas
    lugar_nacimiento: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Ciudad y estado
    nacionalidad: Mapped[str] = mapped_column(String(50), default="Venezolana") # Nacionalidad del cliente
    estado_civil: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Soltero, Casado, etc.
    profesion_ocupacion: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Profesión u ocupación
    
    # Información de contacto
    telefono: Mapped[str] = mapped_column(String(20), nullable=False) # Teléfono principal
    telefono_secundario: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # Teléfono secundario
    email: Mapped[str] = mapped_column(String(100), nullable=False) # Email principal
    direccion: Mapped[str] = mapped_column(Text, nullable=False) # Dirección completa
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False) # Ciudad
    estado: Mapped[str] = mapped_column(String(100), nullable=False) # Estado o provincia
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(10), nullable=True) # Código postal
    
    # Información financiera
    perfil_riesgo: Mapped[PerfilRiesgo] = mapped_column(SQLAlchemyEnum(PerfilRiesgo), default=PerfilRiesgo.MODERADO) # Perfil de riesgo
    id_banco: Mapped[Optional[int]] = mapped_column(ForeignKey('bancos.id')) # Banco asociado por defecto
    tipo_cuenta: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # Ahorros, Corriente
    numero_cuenta: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Número de cuenta bancaria
    id_casa_bolsa: Mapped[Optional[int]] = mapped_column(ForeignKey('casas_bolsa.id')) # Casa de bolsa asociada por defecto
    
    # Metadatos
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relaciones
    cuentas = relationship("CuentaDB", back_populates="cliente", cascade="all, delete-orphan") # Cuentas bursátiles
    documentos = relationship("DocumentoDB", back_populates="cliente", cascade="all, delete-orphan") # Documentos asociados
    ordenes = relationship("OrdenDB", back_populates="cliente") # Órdenes bursátiles
    transacciones = relationship("TransaccionDB", back_populates="cliente") # Transacciones ejecutadas
    movimientos = relationship("MovimientoDB", back_populates="cliente") # Movimientos de cuenta
    banco = relationship("BancoDB") # Banco asociado
    casa_bolsa = relationship("CasaBolsaDB") # Casa de bolsa asociada
    
    # Índices
    __table_args__ = (
        Index('idx_cliente_nombre', 'nombre_completo'), # Índice para búsquedas por nombre
        Index('idx_cliente_email', 'email'), # Índice para búsquedas por email
        Index('idx_cliente_tipo_documento', 'tipo_documento'),  # Índice para búsquedas por tipo de documento
        Index('idx_cliente_tipo_persona', 'tipo_persona'), # Índice para búsquedas por tipo de persona
    )
    
    @validates('documento_id') # Validar cédula o RIF según tipo de persona
    def validate_id(self, key, id_value):
        """Validar cédula o RIF venezolano"""
        if self.tipo_persona == TipoPersona.NATURAL:
            if not validar_cedula(id_value):
                raise ValueError(f"Cédula inválida: {id_value}")
        if self.tipo_persona == TipoPersona.JURIDICA:
            if not validar_rif(id_value):
                raise ValueError(f"RIF inválido: {id_value}")
        return id_value
    
    @validates('telefono') # Validar teléfono principal
    def validate_telefono_principal(self, key, telefono):
        """Validar teléfono venezolano"""
        if not validar_telefono_venezolano(telefono):
            raise ValueError(f"Teléfono inválido: {telefono}")
        return telefono
    
    @validates('email') # Validar formato de email
    def validate_email(self, key, email):
        """Validar formato de email"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError(f"Email inválido: {email}")
        return email
    
    @hybrid_property
    def edad(self):
        """Calcular edad del cliente"""
        if not self.fecha_nacimiento:
            return None
        today = date.today()
        age = today.year - self.fecha_nacimiento.year
        if (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            age -= 1
        return age
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'tipo_persona': self.tipo_persona.value,
            'tipo_documento': self.tipo_documento.value,
            'nombre_completo': self.nombre_completo,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'edad': self.edad,
            'telefono_principal': self.telefono_principal,
            'email': self.email,
            'perfil_riesgo': self.perfil_riesgo.value,
            'limite_inversion_bs': float(self.limite_inversion_bs) if self.limite_inversion_bs else 0.0,
            'limite_inversion_usd': float(self.limite_inversion_usd) if self.limite_inversion_usd else 0.0,
            'fecha_registro': self.fecha_registro.isoformat(),
            'activo': self.activo
        }
    
    def __repr__(self):
        return f"<Cliente(id='{self.id}', nombre='{self.nombre_completo}')>"

class CuentaDB(Base, AuditMixin):
    """Modelo para cuentas bursátiles de clientes"""
    __tablename__ = "cuentas"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    cliente_id: Mapped[Integer] = mapped_column(Integer, ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False) # Cliente propietario
    numero_cuenta: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # Número único de cuenta
    tipo_cuenta: Mapped[str] = mapped_column(String(30), nullable=False)  # Individual, Conjunta, Corporativa
    moneda_base: Mapped[str] = mapped_column(String(3), default=Moneda.DOLAR.value)
    
    # Saldos
    saldo_disponible_bs: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.00) # Saldo disponible en Bs
    saldo_disponible_usd: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.00) # Saldo disponible en USD
    saldo_bloqueado_bs: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.00) # Saldo bloqueado en Bs
    saldo_bloqueado_usd: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.00) # Saldo bloqueado en USD
    
    # Estado
    estado: Mapped[str] = mapped_column(String(20), default='Activa')  # Activa, Suspendida, Cerrada
    fecha_apertura: Mapped[datetime] = mapped_column(DateTime, default=func.now()) # Fecha de apertura
    fecha_cierre: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True) # Fecha de cierre
    
    # Configuración
    permite_margen: Mapped[bool] = mapped_column(Boolean, default=False) # Si permite operaciones con margen
    limite_margen_bs: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.00) # Límite de margen en Bs
    limite_margen_usd: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.00) # Límite de margen en USD
    
    # Metadatos
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="cuentas") # Cliente propietario
    ordenes = relationship("OrdenDB", back_populates="cuenta") # Órdenes asociadas
    transacciones = relationship("TransaccionDB", back_populates="cuenta") # Transacciones asociadas
    movimientos = relationship("MovimientoDB", back_populates="cuenta") # Movimientos de cuenta
    portafolio_items = relationship("PortafolioItemDB", back_populates="cuenta") # Items en portafolio
    
    # Índices y restricciones 
    __table_args__ = (
        Index('idx_cuenta_cliente', 'cliente_id'),  # Índice para búsquedas por cliente
        Index('idx_cuenta_numero', 'numero_cuenta'), # Índice para búsquedas por número de cuenta
        CheckConstraint('saldo_disponible_bs >= 0', name='check_saldo_bs'),
        CheckConstraint('saldo_disponible_usd >= 0', name='check_saldo_usd'),
    )
    
    @hybrid_property
    def saldo_total_bs(self): # Suma de saldo disponible y bloqueado en Bs
        return (self.saldo_disponible_bs or 0) + (self.saldo_bloqueado_bs or 0)
    
    @hybrid_property
    def saldo_total_usd(self): # Suma de saldo disponible y bloqueado en USD
        return (self.saldo_disponible_usd or 0) + (self.saldo_bloqueado_usd or 0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'numero_cuenta': self.numero_cuenta,
            'tipo_cuenta': self.tipo_cuenta,
            'moneda_base': self.moneda_base,
            'saldo_disponible_bs': float(self.saldo_disponible_bs),
            'saldo_disponible_usd': float(self.saldo_disponible_usd),
            'saldo_total_bs': float(self.saldo_total_bs),
            'saldo_total_usd': float(self.saldo_total_usd),
            'estado': self.estado,
            'fecha_apertura': self.fecha_apertura.isoformat()
        }

class ActivoDB(Base, AuditMixin):
    """Modelo para activos bursátiles"""
    __tablename__ = "activos"
    
    #
    id: Mapped[str] = mapped_column(String(15), primary_key=True)  # Símbolo: BNC, EMPV, etc.
    nombre: Mapped[str] = mapped_column(String(150), nullable=False) # Nombre completo del activo
    rif: Mapped[Optional[str]] = mapped_column(String(15), nullable=False)  # RIF de la emopresa del activo
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)  # Acción, Bono, ETF, etc.
    sector: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Sector económico
    subsector: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Subsector económico
    
    # Información bursátil
    moneda: Mapped[str] = mapped_column(String(3), default=Moneda.BOLIVAR.value) # Moneda de cotización
    precio_actual: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.00000000) # Último precio conocido
    
    # Características
    lote_standard: Mapped[int] = mapped_column(Integer, default=100) # Tamaño del lote estándar
    lote_minimo: Mapped[int] = mapped_column(Integer, default=1) # Tamaño del lote mínimo
    precio_minimo: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True) # Precio mínimo permitido
    precio_maximo: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True) # Precio máximo permitido
    
    # Relaciones
    ordenes = relationship("OrdenDB", back_populates="activo") # Órdenes asociadas
    transacciones = relationship("TransaccionDB", back_populates="activo")  # Transacciones asociadas
    portafolio_items = relationship("PortafolioItemDB", back_populates="activo") # Items en portafolio
    
    __table_args__ = (
        Index('idx_activo_nombre', 'nombre'),
        Index('idx_activo_tipo', 'tipo'),
        Index('idx_activo_sector', 'sector'),
        Index('idx_activo_activo', 'activo'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'sector': self.sector,
            'moneda': self.moneda,
            'precio_actual': float(self.precio_actual),
            'precio_anterior': float(self.precio_anterior),
            'variacion_diaria': float(self.variacion_diaria),
            'lote_standard': self.lote_standard,
            'activo': self.activo
        }

class OrdenDB(Base, AuditMixin):
    """Modelo para órdenes bursátiles"""
    __tablename__ = "ordenes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    numero_orden: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # Número único de orden
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey('clientes.id'), nullable=False) # Cliente que realiza la orden
    cuenta_id: Mapped[int] = mapped_column(Integer, ForeignKey('cuentas.id'), nullable=False) # Cuenta asociada
    activo_id: Mapped[str] = mapped_column(String(20), ForeignKey('activos.id'), nullable=False) # Activo objeto de la orden
    
    # Tipo de orden
    tipo_orden: Mapped[TipoOrden] = mapped_column(SQLAlchemyEnum(TipoOrden), nullable=False) # Compra o Venta
    tipo_operacion: Mapped[TipoOperacion] = mapped_column(SQLAlchemyEnum(TipoOperacion), nullable=False) # Mercado o Limitada
    
    # Detalles
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False) # Cantidad de acciones
    precio_limite: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True) # Precio límite para órdenes limitadas
    
    # Estado
    estado: Mapped[EstadoOrden] = mapped_column(SQLAlchemyEnum(EstadoOrden), default=EstadoOrden.PENDIENTE) # Estado de la orden
    fecha_ejecucion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True) # Fecha de ejecución
    fecha_vencimiento: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True) # Fecha de vencimiento de la orden
    
    # Ejecución
    cantidad_ejecutada: Mapped[int] = mapped_column(Integer, default=0) # Cantidad ya ejecutada
    precio_ejecucion_promedio: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True) # Precio promedio de ejecución
    numero_operacion_bvc: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Número de operación en la BVC
    
    # Comisiones
    comision_base: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.00) # Comisión base
    iva_comision: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=0.00) # IVA sobre la comisión
    
    # Tasa BCV al momento de la orden
    tasa_bcv_snapshot: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), nullable=True)  # Tasa BCV al momento de la orden
    
    # Metadatos
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Notas adicionales
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="ordenes") # Cliente que realizó la orden
    cuenta = relationship("CuentaDB", back_populates="ordenes") # Cuenta asociada a la orden
    activo = relationship("ActivoDB", back_populates="ordenes") # Activo objeto de la orden
    transacciones = relationship("TransaccionDB", back_populates="orden") # Transacciones asociadas a la orden
    
    # Índices y restricciones
    __table_args__ = (
        Index('idx_orden_cliente', 'cliente_id'), # Índice para búsquedas por cliente
        Index('idx_orden_activo', 'activo_id'), # Índice para búsquedas por activo
        Index('idx_orden_estado', 'estado'), # Índice para búsquedas por estado
        Index('idx_orden_fecha', 'fecha_registro'), # Índice para búsquedas por fecha
        CheckConstraint('cantidad > 0', name='check_cantidad_positiva'), # Cantidad debe ser positiva
        CheckConstraint('cantidad_ejecutada <= cantidad', name='check_cantidad_ejecutada'), # Ejecutada no puede exceder cantidad
    )
    
    
    @hybrid_property
    def monto_total(self): # Monto total de la orden (cantidad * precio)
        if self.precio:
            return self.cantidad * self.precio
        return None
    
    @hybrid_property
    def monto_ejecutado(self): # Monto ya ejecutado (cantidad_ejecutada * precio_ejecucion_promedio)
        if self.precio_ejecucion_promedio and self.cantidad_ejecutada:
            return self.cantidad_ejecutada * self.precio_ejecucion_promedio
        return 0
    
    @hybrid_property # Porcentaje ejecutado
    def porcentaje_ejecutado(self):
        if self.cantidad > 0:
            return (self.cantidad_ejecutada / self.cantidad) * 100
        return 0
    
    def to_dict(self): # Convertir a diccionario
        return {
            'id': self.id,
            'numero_orden': self.numero_orden,
            'cliente_id': self.cliente_id,
            'activo_id': self.activo_id,
            'tipo_orden': self.tipo_orden.value,
            'tipo_operacion': self.tipo_operacion.value,
            'cantidad': self.cantidad,
            'precio': float(self.precio) if self.precio else None,
            'estado': self.estado.value,
            'fecha_creacion': self.fecha_registro.isoformat(),
            'cantidad_ejecutada': self.cantidad_ejecutada,
            'porcentaje_ejecutado': float(self.porcentaje_ejecutado),
            'comision_total': float(self.comision_total) if self.comision_total else 0.0
        }

class TransaccionDB(Base, AuditMixin):
    """Modelo para transacciones ejecutadas"""
    __tablename__ = "transacciones"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    orden_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('ordenes.id'), nullable=True) # Orden asociada
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey('clientes.id'), nullable=False) # Cliente asociado
    cuenta_id: Mapped[int] = mapped_column(Integer, ForeignKey('cuentas.id'), nullable=False) # Cuenta asociada
    activo_id: Mapped[str] = mapped_column(String(20), ForeignKey('activos.id'), nullable=False) # Activo transaccionado
    
    # Detalles
    tipo_transaccion: Mapped[str] = mapped_column(String(20), nullable=False)  # Compra, Venta, Dividendo
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False) # Cantidad de acciones
    precio_unitario: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), nullable=False) # Precio por acción
    monto_total: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), nullable=False) # Monto total de la transacción
    moneda: Mapped[str] = mapped_column(String(3), nullable=False) # Moneda de la transacción
    
    # Comisiones
    comision_base: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), default=0.00) # Comisión base
    iva_comision: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), default=0.00) # IVA sobre la comisión
    comision_total: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), default=0.00) # Comisión total
    
    # Operación BVC
    numero_operacion_bvc: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Número de operación en la BVC
    fecha_operacion_bvc: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True) # Fecha de la operación en la BVC
    
    # Metadatos
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Notas adicionales
    
    # Relaciones
    orden = relationship("OrdenDB", back_populates="transacciones") # Orden asociada
    cliente = relationship("ClienteDB", back_populates="transacciones") # Cliente asociado
    cuenta = relationship("CuentaDB", back_populates="transacciones") # Cuenta asociada
    activo = relationship("ActivoDB", back_populates="transacciones") # Activo transaccionado
    
    # Índices y restricciones
    __table_args__ = (
        Index('idx_transaccion_cliente', 'cliente_id'), # Índice para búsquedas por cliente
        Index('idx_transaccion_fecha', 'fecha_registro'), # Índice para búsquedas por fecha
        Index('idx_transaccion_activo', 'activo_id'), # Índice para búsquedas por activo
        Index('idx_transaccion_orden', 'orden_id'), # Índice para búsquedas por orden
        CheckConstraint('cantidad > 0', name='check_transaccion_cantidad'), # Cantidad debe ser positiva
        CheckConstraint('precio_unitario > 0', name='check_precio_positivo'), # Precio unitario debe ser positivo
    )
    
    @hybrid_property
    def monto_neto(self):
        """Monto después de comisiones"""
        return self.monto_total - (self.comision_total or 0)
    
    def to_dict(self): # Convertir a diccionario
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'activo_id': self.activo_id,
            'tipo_transaccion': self.tipo_transaccion,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'monto_total': float(self.monto_total),
            'monto_neto': float(self.monto_neto),
            'comision_total': float(self.comision_total) if self.comision_total else 0.0,
            'numero_operacion_bvc': self.numero_operacion_bvc,
            'fecha_registro': self.fecha_registro.isoformat()
        }

class PortafolioItemDB(Base, AuditMixin):
    """Modelo para items en portafolio de clientes"""
    __tablename__ = "portafolio_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey('clientes.id'), nullable=False) # Cliente propietario
    cuenta_id: Mapped[int] = mapped_column(Integer, ForeignKey('cuentas.id'), nullable=False) # Cuenta asociada
    activo_id: Mapped[str] = mapped_column(String(20), ForeignKey('activos.id'), nullable=False) # Activo en el portafolio
    
    # Posición
    cantidad: Mapped[int] = mapped_column(Integer, default=0) # Cantidad de acciones poseídas
    costo_promedio: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), default=0.0000) # Costo promedio por acción
    costo_total: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), default=0.0000) # Costo total de la posición
    
    # Valorización
    precio_actual: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), default=0.0000) # Precio actual del activo
    valor_mercado: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), default=0.0000) # Valor de mercado de la posición
    ganancia_perdida: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), default=0.0000) # Ganancia o pérdida no realizada
    porcentaje_rendimiento: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), default=0.0000) # % de rendimiento de la posición
    
    # Metadatos
    moneda: Mapped[str] = mapped_column(String(3), default=Moneda.BOLIVAR.value) # Moneda de la posición
    
    # Relaciones
    cliente = relationship("ClienteDB") # Sin back_populates necesario
    cuenta = relationship("CuentaDB", back_populates="portafolio_items") # Cuenta asociada
    activo = relationship("ActivoDB", back_populates="portafolio_items") # Activo en el portafolio
    
    # Índices y restricciones
    __table_args__ = (
        Index('idx_portafolio_cliente', 'cliente_id'), # Índice para búsquedas por cliente
        Index('idx_portafolio_activo', 'activo_id'), # Índice para búsquedas por activo
        Index('idx_portafolio_cuenta', 'cuenta_id'), # Índice para búsquedas por cuenta
        UniqueConstraint('cliente_id', 'cuenta_id', 'activo_id', name='uq_portafolio_item'), # Unicidad por cliente, cuenta y activo
    )
    
    @hybrid_property
    def porcentaje_portafolio(self):
        # Esto se calcula en relación al total del portafolio
        return 0.0  # Se calcula dinámicamente
    
    def to_dict(self): # Convertir a diccionario
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'activo_id': self.activo_id,
            'cantidad': self.cantidad,
            'costo_promedio': float(self.costo_promedio),
            'costo_total': float(self.costo_total),
            'precio_actual': float(self.precio_actual),
            'valor_mercado': float(self.valor_mercado),
            'ganancia_perdida': float(self.ganancia_perdida),
            'porcentaje_rendimiento': float(self.porcentaje_rendimiento),
            'moneda': self.moneda
        }

class MovimientoDB(Base, AuditMixin):
    """Modelo para movimientos de efectivo"""
    __tablename__ = "movimientos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey('clientes.id'), nullable=False) # Cliente asociado
    cuenta_id: Mapped[int] = mapped_column(Integer, ForeignKey('cuentas.id'), nullable=False) # Cuenta asociada
    
    # Detalles
    tipo_movimiento: Mapped[str] = mapped_column(String(30), nullable=False)  # Depósito, Retiro, Comisión, Interés
    monto: Mapped[Decimal] = mapped_column(DECIMAL(15, 4), nullable=False) # Monto del movimiento
    moneda: Mapped[str] = mapped_column(String(3), nullable=False) # Moneda del movimiento
    concepto: Mapped[str] = mapped_column(Text, nullable=False) # Descripción del movimiento
    
    # Estado
    estado: Mapped[str] = mapped_column(String(20), default='Procesado')  # Pendiente, Procesado, Rechazado
    fecha_movimiento: Mapped[datetime] = mapped_column(DateTime, default=func.now()) # Fecha del movimiento
    fecha_procesamiento: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True) # Fecha de procesamiento
    
    # Referencias
    numero_referencia: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Número de referencia externo
    banco_origen: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Banco de origen
    banco_destino: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Banco de destino
    
    # Metadatos
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="movimientos") # Cliente asociado
    cuenta = relationship("CuentaDB", back_populates="movimientos") # Cuenta asociada
    
    # Índices y restricciones
    __table_args__ = (
        Index('idx_movimiento_cliente', 'cliente_id'), # Índice para búsquedas por cliente
        Index('idx_movimiento_fecha', 'fecha_movimiento'), # Índice para búsquedas por fecha
        Index('idx_movimiento_tipo', 'tipo_movimiento'), # Índice para búsquedas por tipo de movimiento
        CheckConstraint('monto != 0', name='check_monto_no_cero'), # Monto no puede ser cero
    )
    
    def to_dict(self): # Convertir a diccionario
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'tipo_movimiento': self.tipo_movimiento,
            'monto': float(self.monto),
            'moneda': self.moneda,
            'concepto': self.concepto,
            'estado': self.estado,
            'fecha_movimiento': self.fecha_movimiento.isoformat(),
            'numero_referencia': self.numero_referencia
        }

class DocumentoDB(Base, AuditMixin):
    """Modelo para documentos de clientes"""
    __tablename__ = "documentos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID interno
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False) # Cliente asociado
    
    # Información del documento
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False)  # Cédula, RIF, Estados de cuenta, etc.
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False) # Nombre original del archivo
    ruta_archivo: Mapped[str] = mapped_column(String(500), nullable=False) # Ruta en el sistema de archivos o URL
    tamano: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # En bytes
    formato: Mapped[str] = mapped_column(String(10), nullable=False)  # pdf, jpg, png, etc.
    
    # Metadatos
    fecha_subida: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    fecha_documento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Estado
    verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="documentos")
    
    __table_args__ = (
        Index('idx_documento_cliente', 'cliente_id'),
        Index('idx_documento_tipo', 'tipo_documento'),
        Index('idx_documento_fecha', 'fecha_documento'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'tipo_documento': self.tipo_documento,
            'nombre_archivo': self.nombre_archivo,
            'formato': self.formato,
            'fecha_subida': self.fecha_subida.isoformat(),
            'verificado': self.verificado
        }

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