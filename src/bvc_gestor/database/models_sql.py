# src/bvc_gestor/database/models_sql.py
"""
Modelos SQLAlchemy para la base de datos
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, Enum, Numeric, Date, DECIMAL,
    JSON, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func, text
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, date
import re
import logging

from .engine import Base
from ..utils.validators_venezuela import (
    validar_cedula, validar_rif, validar_telefono_venezolano,
    validar_fecha_venezolana, validar_monto_bs, validar_monto_usd
)
from ..utils.constants import (
    TipoPersona, TipoDocumento, PerfilRiesgo,
    EstadoOrden, TipoOrden, TipoOperacion, Moneda
)

logger = logging.getLogger(__name__)

class ClienteDB(Base):
    """Modelo SQLAlchemy para Clientes venezolanos"""
    __tablename__ = "clientes"
    
    # Identificación
    id = Column(String(20), primary_key=True)  # Cédula o RIF
    tipo_persona = Column(Enum(TipoPersona), nullable=False)
    tipo_documento = Column(Enum(TipoDocumento), nullable=False)
    
    # Información personal
    nombre_completo = Column(String(200), nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    lugar_nacimiento = Column(String(100), nullable=True)
    nacionalidad = Column(String(50), default="Venezolana")
    estado_civil = Column(String(50), nullable=True)
    profesion_ocupacion = Column(String(100), nullable=True)
    
    # Información de contacto
    telefono_principal = Column(String(20), nullable=False)
    telefono_secundario = Column(String(20), nullable=True)
    email = Column(String(100), nullable=False)
    direccion = Column(Text, nullable=False)
    ciudad = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)
    codigo_postal = Column(String(10), nullable=True)
    
    # Información financiera
    perfil_riesgo = Column(Enum(PerfilRiesgo), default=PerfilRiesgo.MODERADO)
    limite_inversion_bs = Column(DECIMAL(15, 2), default=0.00)
    limite_inversion_usd = Column(DECIMAL(15, 2), default=0.00)
    ingresos_mensuales_bs = Column(DECIMAL(15, 2), nullable=True)
    ingresos_mensuales_usd = Column(DECIMAL(15, 2), nullable=True)
    
    # Información bancaria
    banco_principal = Column(String(100), nullable=True)
    numero_cuenta = Column(String(50), nullable=True)
    tipo_cuenta = Column(String(30), nullable=True)  # Ahorros, Corriente
    
    # Documentación
    tiene_patrimonio_declarado = Column(Boolean, default=False)
    monto_patrimonio_bs = Column(DECIMAL(15, 2), nullable=True)
    monto_patrimonio_usd = Column(DECIMAL(15, 2), nullable=True)
    
    # Metadatos
    fecha_registro = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    activo = Column(Boolean, default=True)
    notas = Column(Text, nullable=True)
    
    # Relaciones
    cuentas = relationship("CuentaDB", back_populates="cliente", cascade="all, delete-orphan")
    documentos = relationship("DocumentoDB", back_populates="cliente", cascade="all, delete-orphan")
    ordenes = relationship("OrdenDB", back_populates="cliente")
    transacciones = relationship("TransaccionDB", back_populates="cliente")
    movimientos = relationship("MovimientoDB", back_populates="cliente")
    
    # Índices
    __table_args__ = (
        Index('idx_cliente_nombre', 'nombre_completo'),
        Index('idx_cliente_email', 'email'),
        Index('idx_cliente_activo', 'activo'),
        CheckConstraint('limite_inversion_bs >= 0', name='check_limite_bs'),
        CheckConstraint('limite_inversion_usd >= 0', name='check_limite_usd'),
    )
    
    @validates('id')
    def validate_id(self, key, id_value):
        """Validar cédula o RIF venezolano"""
        if self.tipo_persona == TipoPersona.NATURAL:
            if not validar_cedula(id_value):
                raise ValueError(f"Cédula inválida: {id_value}")
        else:
            if not validar_rif(id_value):
                raise ValueError(f"RIF inválido: {id_value}")
        return id_value
    
    @validates('telefono_principal')
    def validate_telefono_principal(self, key, telefono):
        """Validar teléfono venezolano"""
        if not validar_telefono_venezolano(telefono):
            raise ValueError(f"Teléfono inválido: {telefono}")
        return telefono
    
    @validates('email')
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
            'tipo_persona': self.tipo_persona,
            'tipo_documento': self.tipo_documento,
            'nombre_completo': self.nombre_completo,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'edad': self.edad,
            'telefono_principal': self.telefono_principal,
            'email': self.email,
            'perfil_riesgo': self.perfil_riesgo,
            'limite_inversion_bs': float(self.limite_inversion_bs) if self.limite_inversion_bs else 0.0,
            'limite_inversion_usd': float(self.limite_inversion_usd) if self.limite_inversion_usd else 0.0,
            'fecha_registro': self.fecha_registro.isoformat(),
            'activo': self.activo
        }
    
    def __repr__(self):
        return f"<Cliente(id='{self.id}', nombre='{self.nombre_completo}')>"

class CuentaDB(Base):
    """Modelo para cuentas bursátiles de clientes"""
    __tablename__ = "cuentas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(String(20), ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False)
    numero_cuenta = Column(String(50), unique=True, nullable=False)
    tipo_cuenta = Column(String(30), nullable=False)  # Individual, Conjunta, Corporativa
    moneda_base = Column(String(3), default=Moneda.USD)
    
    # Saldos
    saldo_disponible_bs = Column(DECIMAL(15, 2), default=0.00)
    saldo_disponible_usd = Column(DECIMAL(15, 2), default=0.00)
    saldo_bloqueado_bs = Column(DECIMAL(15, 2), default=0.00)
    saldo_bloqueado_usd = Column(DECIMAL(15, 2), default=0.00)
    
    # Estado
    estado = Column(String(20), default='Activa')  # Activa, Suspendida, Cerrada
    fecha_apertura = Column(DateTime, default=func.now())
    fecha_cierre = Column(DateTime, nullable=True)
    
    # Configuración
    permite_margen = Column(Boolean, default=False)
    limite_margen_bs = Column(DECIMAL(15, 2), default=0.00)
    limite_margen_usd = Column(DECIMAL(15, 2), default=0.00)
    
    # Metadatos
    notas = Column(Text, nullable=True)
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="cuentas")
    ordenes = relationship("OrdenDB", back_populates="cuenta")
    transacciones = relationship("TransaccionDB", back_populates="cuenta")
    movimientos = relationship("MovimientoDB", back_populates="cuenta")
    portafolio_items = relationship("PortafolioItemDB", back_populates="cuenta")
    
    __table_args__ = (
        Index('idx_cuenta_cliente', 'cliente_id'),
        Index('idx_cuenta_numero', 'numero_cuenta'),
        CheckConstraint('saldo_disponible_bs >= 0', name='check_saldo_bs'),
        CheckConstraint('saldo_disponible_usd >= 0', name='check_saldo_usd'),
    )
    
    @hybrid_property
    def saldo_total_bs(self):
        return (self.saldo_disponible_bs or 0) + (self.saldo_bloqueado_bs or 0)
    
    @hybrid_property
    def saldo_total_usd(self):
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

class ActivoDB(Base):
    """Modelo para activos bursátiles de la BVC"""
    __tablename__ = "activos"
    
    id = Column(String(20), primary_key=True)  # Símbolo: BNC, EMPV, etc.
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(30), nullable=False)  # Acción, Bono, ETF, etc.
    sector = Column(String(50), nullable=True)
    subsector = Column(String(50), nullable=True)
    
    # Información bursátil
    moneda = Column(String(3), default=Moneda.USD)
    precio_actual = Column(DECIMAL(15, 4), default=0.0000)
    precio_anterior = Column(DECIMAL(15, 4), default=0.0000)
    variacion_diaria = Column(DECIMAL(10, 4), default=0.0000)
    volumen_promedio = Column(Integer, default=0)
    
    # Características
    lote_standard = Column(Integer, default=100)
    lote_minimo = Column(Integer, default=1)
    precio_minimo = Column(DECIMAL(15, 4), nullable=True)
    precio_maximo = Column(DECIMAL(15, 4), nullable=True)
    
    # Estado
    activo = Column(Boolean, default=True)
    fecha_ingreso = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    ordenes = relationship("OrdenDB", back_populates="activo")
    transacciones = relationship("TransaccionDB", back_populates="activo")
    portafolio_items = relationship("PortafolioItemDB", back_populates="activo")
    
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

class OrdenDB(Base):
    """Modelo para órdenes bursátiles"""
    __tablename__ = "ordenes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_orden = Column(String(50), unique=True, nullable=False)
    cliente_id = Column(String(20), ForeignKey('clientes.id'), nullable=False)
    cuenta_id = Column(Integer, ForeignKey('cuentas.id'), nullable=False)
    activo_id = Column(String(20), ForeignKey('activos.id'), nullable=False)
    
    # Tipo de orden
    tipo_orden = Column(Enum(TipoOrden), nullable=False)
    tipo_operacion = Column(Enum(TipoOperacion), nullable=False)
    
    # Detalles
    cantidad = Column(Integer, nullable=False)
    precio = Column(DECIMAL(15, 4), nullable=True)  # Null para órdenes de mercado
    precio_limite = Column(DECIMAL(15, 4), nullable=True)
    
    # Estado
    estado = Column(Enum(EstadoOrden), default=EstadoOrden.PENDIENTE)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_ejecucion = Column(DateTime, nullable=True)
    fecha_vencimiento = Column(DateTime, nullable=True)
    
    # Ejecución
    cantidad_ejecutada = Column(Integer, default=0)
    precio_ejecucion_promedio = Column(DECIMAL(15, 4), nullable=True)
    numero_operacion_bvc = Column(String(50), nullable=True)
    
    # Comisiones
    comision_base = Column(DECIMAL(15, 4), default=0.0000)
    iva_comision = Column(DECIMAL(15, 4), default=0.0000)
    comision_total = Column(DECIMAL(15, 4), default=0.0000)
    
    # Validaciones
    validada = Column(Boolean, default=False)
    motivo_rechazo = Column(Text, nullable=True)
    
    # Metadatos
    notas = Column(Text, nullable=True)
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="ordenes")
    cuenta = relationship("CuentaDB", back_populates="ordenes")
    activo = relationship("ActivoDB", back_populates="ordenes")
    transacciones = relationship("TransaccionDB", back_populates="orden")
    
    __table_args__ = (
        Index('idx_orden_cliente', 'cliente_id'),
        Index('idx_orden_activo', 'activo_id'),
        Index('idx_orden_estado', 'estado'),
        Index('idx_orden_fecha', 'fecha_creacion'),
        CheckConstraint('cantidad > 0', name='check_cantidad_positiva'),
        CheckConstraint('cantidad_ejecutada <= cantidad', name='check_cantidad_ejecutada'),
    )
    
    @hybrid_property
    def monto_total(self):
        if self.precio:
            return self.cantidad * self.precio
        return None
    
    @hybrid_property
    def monto_ejecutado(self):
        if self.precio_ejecucion_promedio and self.cantidad_ejecutada:
            return self.cantidad_ejecutada * self.precio_ejecucion_promedio
        return 0
    
    @hybrid_property
    def porcentaje_ejecutado(self):
        if self.cantidad > 0:
            return (self.cantidad_ejecutada / self.cantidad) * 100
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_orden': self.numero_orden,
            'cliente_id': self.cliente_id,
            'activo_id': self.activo_id,
            'tipo_orden': self.tipo_orden,
            'tipo_operacion': self.tipo_operacion,
            'cantidad': self.cantidad,
            'precio': float(self.precio) if self.precio else None,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'cantidad_ejecutada': self.cantidad_ejecutada,
            'porcentaje_ejecutado': float(self.porcentaje_ejecutado),
            'comision_total': float(self.comision_total) if self.comision_total else 0.0
        }

class TransaccionDB(Base):
    """Modelo para transacciones ejecutadas"""
    __tablename__ = "transacciones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    orden_id = Column(Integer, ForeignKey('ordenes.id'), nullable=True)
    cliente_id = Column(String(20), ForeignKey('clientes.id'), nullable=False)
    cuenta_id = Column(Integer, ForeignKey('cuentas.id'), nullable=False)
    activo_id = Column(String(20), ForeignKey('activos.id'), nullable=False)
    
    # Detalles
    tipo_transaccion = Column(String(20), nullable=False)  # Compra, Venta, Dividendo
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(DECIMAL(15, 4), nullable=False)
    monto_total = Column(DECIMAL(15, 4), nullable=False)
    moneda = Column(String(3), nullable=False)
    
    # Comisiones
    comision_base = Column(DECIMAL(15, 4), default=0.0000)
    iva_comision = Column(DECIMAL(15, 4), default=0.0000)
    comision_total = Column(DECIMAL(15, 4), default=0.0000)
    
    # Operación BVC
    numero_operacion_bvc = Column(String(50), nullable=True)
    fecha_operacion_bvc = Column(DateTime, nullable=True)
    
    # Metadatos
    fecha_transaccion = Column(DateTime, default=func.now())
    notas = Column(Text, nullable=True)
    
    # Relaciones
    orden = relationship("OrdenDB", back_populates="transacciones")
    cliente = relationship("ClienteDB", back_populates="transacciones")
    cuenta = relationship("CuentaDB", back_populates="transacciones")
    activo = relationship("ActivoDB", back_populates="transacciones")
    
    __table_args__ = (
        Index('idx_transaccion_cliente', 'cliente_id'),
        Index('idx_transaccion_fecha', 'fecha_transaccion'),
        Index('idx_transaccion_activo', 'activo_id'),
        Index('idx_transaccion_orden', 'orden_id'),
        CheckConstraint('cantidad > 0', name='check_transaccion_cantidad'),
        CheckConstraint('precio_unitario > 0', name='check_precio_positivo'),
    )
    
    @hybrid_property
    def monto_neto(self):
        """Monto después de comisiones"""
        return self.monto_total - (self.comision_total or 0)
    
    def to_dict(self):
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
            'fecha_transaccion': self.fecha_transaccion.isoformat()
        }

class PortafolioItemDB(Base):
    """Modelo para items en portafolio de clientes"""
    __tablename__ = "portafolio_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(String(20), ForeignKey('clientes.id'), nullable=False)
    cuenta_id = Column(Integer, ForeignKey('cuentas.id'), nullable=False)
    activo_id = Column(String(20), ForeignKey('activos.id'), nullable=False)
    
    # Posición
    cantidad = Column(Integer, default=0)
    costo_promedio = Column(DECIMAL(15, 4), default=0.0000)
    costo_total = Column(DECIMAL(15, 4), default=0.0000)
    
    # Valorización
    precio_actual = Column(DECIMAL(15, 4), default=0.0000)
    valor_mercado = Column(DECIMAL(15, 4), default=0.0000)
    ganancia_perdida = Column(DECIMAL(15, 4), default=0.0000)
    porcentaje_rendimiento = Column(DECIMAL(10, 4), default=0.0000)
    
    # Metadatos
    fecha_ultima_actualizacion = Column(DateTime, default=func.now())
    moneda = Column(String(3), default=Moneda.USD)
    
    # Relaciones
    cliente = relationship("ClienteDB")
    cuenta = relationship("CuentaDB", back_populates="portafolio_items")
    activo = relationship("ActivoDB", back_populates="portafolio_items")
    
    __table_args__ = (
        Index('idx_portafolio_cliente', 'cliente_id'),
        Index('idx_portafolio_activo', 'activo_id'),
        Index('idx_portafolio_cuenta', 'cuenta_id'),
        UniqueConstraint('cliente_id', 'cuenta_id', 'activo_id', name='uq_portafolio_item'),
    )
    
    @hybrid_property
    def porcentaje_portafolio(self):
        # Esto se calcula en relación al total del portafolio
        return 0.0  # Se calcula dinámicamente
    
    def to_dict(self):
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

class MovimientoDB(Base):
    """Modelo para movimientos de efectivo"""
    __tablename__ = "movimientos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(String(20), ForeignKey('clientes.id'), nullable=False)
    cuenta_id = Column(Integer, ForeignKey('cuentas.id'), nullable=False)
    
    # Detalles
    tipo_movimiento = Column(String(30), nullable=False)  # Depósito, Retiro, Comisión, Interés
    monto = Column(DECIMAL(15, 4), nullable=False)
    moneda = Column(String(3), nullable=False)
    concepto = Column(Text, nullable=False)
    
    # Estado
    estado = Column(String(20), default='Procesado')  # Pendiente, Procesado, Rechazado
    fecha_movimiento = Column(DateTime, default=func.now())
    fecha_procesamiento = Column(DateTime, nullable=True)
    
    # Referencias
    numero_referencia = Column(String(50), nullable=True)
    banco_origen = Column(String(100), nullable=True)
    banco_destino = Column(String(100), nullable=True)
    
    # Metadatos
    notas = Column(Text, nullable=True)
    
    # Relaciones
    cliente = relationship("ClienteDB", back_populates="movimientos")
    cuenta = relationship("CuentaDB", back_populates="movimientos")
    
    __table_args__ = (
        Index('idx_movimiento_cliente', 'cliente_id'),
        Index('idx_movimiento_fecha', 'fecha_movimiento'),
        Index('idx_movimiento_tipo', 'tipo_movimiento'),
        CheckConstraint('monto != 0', name='check_monto_no_cero'),
    )
    
    def to_dict(self):
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

class DocumentoDB(Base):
    """Modelo para documentos de clientes"""
    __tablename__ = "documentos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(String(20), ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False)
    
    # Información del documento
    tipo_documento = Column(String(50), nullable=False)  # Cédula, RIF, Estados de cuenta, etc.
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    tamano = Column(Integer, nullable=True)  # En bytes
    formato = Column(String(10), nullable=False)  # pdf, jpg, png, etc.
    
    # Metadatos
    fecha_subida = Column(DateTime, default=func.now())
    fecha_documento = Column(Date, nullable=True)
    descripcion = Column(Text, nullable=True)
    
    # Estado
    verificado = Column(Boolean, default=False)
    fecha_verificacion = Column(DateTime, nullable=True)
    
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

class ConfiguracionDB(Base):
    """Modelo para configuración de la aplicación"""
    __tablename__ = "configuraciones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text, nullable=False)
    tipo = Column(String(20), default='string')  # string, number, boolean, json
    categoria = Column(String(50), default='General')
    descripcion = Column(Text, nullable=True)
    editable = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_config_clave', 'clave'),
        Index('idx_config_categoria', 'categoria'),
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.get_value(),
            'tipo': self.tipo,
            'categoria': self.categoria,
            'descripcion': self.descripcion,
            'editable': self.editable
        }