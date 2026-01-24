# src/bvc_gestor/database/models_sql.py
"""
Modelos SQLAlchemy para la base de datos BVC Gestor

ESTRUCTURA GENERAL:
1. Mixin de Auditoría - Campos comunes para todas las tablas
2. Tablas de Catálogo (Maestros) - Datos de referencia
3. Clientes y Cuentas - Información de inversores
4. Títulos y Mercado - Instrumentos financieros
5. Operaciones Bursátiles - Órdenes y transacciones
6. Movimientos Financieros - Depósitos y retiros
7. Portafolio y Posiciones - Inversiones de clientes
8. Soporte y Configuración - Documentos y parámetros
"""

# ============================================================================
# IMPORTS Y CONFIGURACIÓN
# ============================================================================

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


# ============================================================================
# 1. MIXIN DE AUDITORÍA
# ============================================================================

class AuditMixin:
    """
    Mixin que añade campos de auditoría automáticos a todas las tablas.
    
    Propósito: Eliminar duplicación de código para campos comunes.
    Se hereda automáticamente por todas las clases de modelo.
    """
    # Fecha de creación del registro (se establece automáticamente)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now()  # Usa la función NOW() de la base de datos
    )
    
    # Fecha de última actualización (se actualiza automáticamente)
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),  # Valor inicial
        onupdate=func.now()         # Se actualiza en cada modificación
    )
    
    # Soft-delete: en lugar de borrar físicamente, marcamos como inactivo
    estatus: Mapped[bool] = mapped_column(Boolean, default=True)


# ============================================================================
# 2. TABLAS CATÁLOGO (DATOS MAESTROS)
# ============================================================================

class BancoDB(Base, AuditMixin):
    """
    Modelo para bancos venezolanos registrados.
    
    Propósito: Catálogo de instituciones bancarias donde los clientes
    tienen cuentas. Se usa para validar transferencias y depósitos.
    """
    __tablename__ = "bancos"  # Nombre real de la tabla en la BD
    
    # ID único interno (clave primaria)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # RIF del banco (formato J-00000000-0) - Único en el sistema
    rif: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    
    # Nombre comercial del banco (ej: 'Banco de Venezuela')
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Código bancario de 4 dígitos (ej: '0102' para Banco de Venezuela)
    codigo: Mapped[str] = mapped_column(String(4), unique=True, nullable=False)
    
    # Relaciones: Una banco tiene muchas cuentas bancarias
    cuentas_bancarias = relationship("CuentaBancariaDB", back_populates="banco")


class CasaBolsaDB(Base, AuditMixin):
    """
    Modelo para casas de bolsa venezolanas autorizadas.
    
    Propósito: Entidades donde los clientes tienen cuentas de inversión
    para operar en la Bolsa de Valores de Caracas.
    """
    __tablename__ = "casas_bolsa"
    
    # ID único interno
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # RIF de la casa de bolsa
    rif: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    
    # Nombre comercial (ej: 'Bancamérica Casa de Bolsa')
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Sector económico principal (opcional)
    sector: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Tipo de entidad financiera
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Relaciones: Una casa de bolsa tiene muchas cuentas bursátiles
    cuentas_bursatiles = relationship("CuentaBursatilDB", back_populates="casa_bolsa")


# ============================================================================
# 3. CLIENTES Y CUENTAS
# ============================================================================

class ClienteDB(Base, AuditMixin):
    """
    Modelo para clientes/inversores del sistema.
    
    Propósito: Almacenar información personal, fiscal y de contacto
    de todos los clientes que operan en la bolsa.
    """
    __tablename__ = "clientes"
    
    # ID único interno
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Nombre completo (personas naturales) o razón social (jurídicas)
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Tipo de inversor según regulación venezolana
    tipo_inversor: Mapped[TipoInversor] = mapped_column(
        SQLAlchemyEnum(TipoInversor), 
        nullable=False
    )
    
    # Identificación fiscal: RIF para jurídicos, cédula para naturales
    rif_cedula: Mapped[str] = mapped_column(
        String(20), 
        unique=True,      # No puede haber duplicados
        index=True,       # Índice para búsquedas rápidas
        nullable=False
    )
    
    # Información de contacto
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Información fiscal
    direccion_fiscal: Mapped[str] = mapped_column(Text, nullable=False)
    ciudad_estado: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # ==========================================
    # RELACIONES (con otras tablas)
    # ==========================================
    
    # Un cliente puede tener múltiples cuentas bancarias
    cuentas_bancarias = relationship("CuentaBancariaDB", back_populates="cliente")
    
    # Un cliente puede tener múltiples cuentas bursátiles
    cuentas_bursatiles = relationship("CuentaBursatilDB", back_populates="cliente")
    
    # Un cliente puede tener múltiples documentos
    documentos = relationship("DocumentoDB", back_populates="cliente")
    
    # Un cliente puede realizar múltiples órdenes
    ordenes = relationship("OrdenDB", back_populates="cliente")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índice para búsquedas por nombre (mejora rendimiento)
        Index('idx_cliente_nombre', 'nombre_completo'),
        
        # Índice para búsquedas por RIF/cédula
        Index('idx_cliente_rif', 'rif_cedula'),
        
        # Índice para filtrar por tipo de inversor
        Index('idx_cliente_tipo_inversor', 'tipo_inversor'),
    )
    
    # ==========================================
    # VALIDACIONES DE DATOS
    # ==========================================
    
    @validates('email')
    def validate_email(self, key: str, email: str) -> str:
        """Valida que el email tenga formato correcto"""
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError(f"Email inválido: {email}")
        return email
    
    @validates('rif_cedula')
    def validate_rif_cedula(self, key: str, rif_cedula: str) -> str:
        """Valida que el RIF/cédula no esté vacío"""
        if not rif_cedula or len(rif_cedula.strip()) < 3:
            raise ValueError("RIF/Cédula no puede estar vacío")
        return rif_cedula.strip()
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """
        Convierte el objeto a diccionario para serialización.
        
        Usado en: APIs, exportación, logs, respuestas de UI.
        """
        return {
            'id': self.id,
            'tipo_inversor': self.tipo_inversor.value,  # .value para enum
            'rif_cedula': self.rif_cedula,
            'direccion_fiscal': self.direccion_fiscal,
            'ciudad_estado': self.ciudad_estado,
            'nombre_completo': self.nombre_completo,
            'telefono': self.telefono,
            'email': self.email,
            'fecha_registro': self.fecha_registro.isoformat(),  # ISO para JSON
            'estatus': self.estatus
        }
    
    def __repr__(self) -> str:
        """Representación para debugging"""
        return f"<ClienteDB(id={self.id}, rif_cedula='{self.rif_cedula}', nombre='{self.nombre_completo}')>"


class CuentaBancariaDB(Base, AuditMixin):
    """
    Cuentas bancarias asociadas a clientes.
    
    Propósito: Registrar las cuentas bancarias donde los clientes
    reciben y envían fondos para sus operaciones bursátiles.
    """
    __tablename__ = "cuentas_bancarias"
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Cliente dueño de la cuenta
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id"),  # Referencia a tabla clientes
        nullable=False
    )
    
    # Banco donde está la cuenta
    banco_id: Mapped[int] = mapped_column(
        ForeignKey("bancos.id"),
        nullable=False
    )
    
    # Número de cuenta (ej: 0102-1234-56-1234567890)
    numero_cuenta: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Tipo de cuenta bancaria
    tipo_cuenta: Mapped[str] = mapped_column(String(30), default="Corriente")
    
    # Indica si es la cuenta principal del cliente
    default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con cliente
    cliente = relationship("ClienteDB", back_populates="cuentas_bancarias")
    
    # Relación con banco
    banco = relationship("BancoDB", back_populates="cuentas_bancarias")
    
    # Una cuenta bancaria puede tener múltiples movimientos
    movimientos = relationship("MovimientoDB", back_populates="cuenta_bancaria")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para búsquedas frecuentes
        Index('idx_cuenta_bancaria_cliente', 'cliente_id'),
        Index('idx_cuenta_bancaria_numero', 'numero_cuenta'),
        
        # Restricción: no puede haber misma cuenta en mismo banco
        UniqueConstraint('banco_id', 'numero_cuenta', name='uq_banco_numero_cuenta'),
    )


class CuentaBursatilDB(Base, AuditMixin):
    """
    Cuentas de inversión en casas de bolsa.
    
    Propósito: Representa la cuenta donde un cliente mantiene
    sus títulos y saldos para operar en la bolsa.
    """
    __tablename__ = "cuentas_bursatiles"
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Cliente dueño de la cuenta
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    
    # Casa de bolsa donde está abierta la cuenta
    casa_bolsa_id: Mapped[int] = mapped_column(ForeignKey("casas_bolsa.id"), nullable=False)
    
    # Número de cuenta bursátil (asignado por la casa de bolsa)
    cuenta: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Indica si es la cuenta principal para operaciones
    default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con cliente
    cliente = relationship("ClienteDB", back_populates="cuentas_bursatiles")
    
    # Relación con casa de bolsa
    casa_bolsa = relationship("CasaBolsaDB", back_populates="cuentas_bursatiles")
    
    # Una cuenta bursátil tiene múltiples saldos (uno por moneda)
    saldos = relationship("SaldoDB", back_populates="cuenta", cascade="all, delete-orphan")
    
    # Una cuenta bursátil tiene múltiples movimientos
    movimientos = relationship("MovimientoDB", back_populates="cuenta_bursatil")
    
    # Una cuenta bursátil tiene múltiples órdenes
    ordenes = relationship("OrdenDB", back_populates="cuenta")
    
    # Una cuenta bursátil tiene múltiples items en portafolio
    portafolio = relationship("PortafolioItemDB", back_populates="cuenta")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para consultas frecuentes
        Index('idx_cuenta_cliente', 'cliente_id'),
        Index('idx_cuenta_casa_bolsa', 'casa_bolsa_id'),
        Index('idx_cuenta', 'cuenta')
    )
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'cuenta': self.cuenta,
            'cliente_id': self.cliente_id,
            'casa_bolsa_id': self.casa_bolsa_id,
            'default': self.default
        }
    
    def __repr__(self) -> str:
        return f"<CuentaBursatilDB(id={self.id}, cuenta='{self.cuenta}', cliente_id={self.cliente_id})>"


class SaldoDB(Base, AuditMixin):
    """
    Balances monetarios por moneda para cada cuenta bursátil.
    
    Propósito: Llevar contabilidad de los fondos en diferentes estados:
    disponible, en tránsito (depósitos pendientes) y bloqueado (para órdenes).
    """
    __tablename__ = "saldos"
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Cuenta bursátil a la que pertenece el saldo
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bursatiles.id"), nullable=False)
    
    # Moneda del saldo (ISO 4217: VES, USD, EUR)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default='VES')
    
    # ==========================================
    # TRES TIPOS DE SALDOS (contabilidad bursátil)
    # ==========================================
    
    # Dinero disponible para usar inmediatamente
    disponible: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=Decimal('0.0'))
    
    # Dinero en proceso de depósito (aún no confirmado)
    en_transito: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=Decimal('0.0'))
    
    # Dinero reservado para órdenes pendientes de ejecución
    bloqueado: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=Decimal('0.0'))
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con cuenta bursátil
    cuenta = relationship("CuentaBursatilDB", back_populates="saldos")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Restricción: una cuenta solo puede tener un registro por moneda
        UniqueConstraint('cuenta_id', 'moneda', name='uq_cuenta_moneda'),
        
        # Los saldos no pueden ser negativos
        CheckConstraint('disponible >= 0', name='check_disponible_positivo'),
        CheckConstraint('en_transito >= 0', name='check_transito_positivo'),
        CheckConstraint('bloqueado >= 0', name='check_bloqueado_positivo'),
    )
    
    # ==========================================
    # PROPIEDADES CALCULADAS
    # ==========================================
    
    @property
    def saldo_proyectado(self) -> Decimal:
        """
        Saldo total proyectado: disponible + en_transito - bloqueado.
        
        Representa el saldo que tendrá el cliente una vez se confirmen
        los depósitos pendientes y se ejecuten las órdenes.
        """
        return self.disponible + self.en_transito - self.bloqueado
    
    @property
    def saldo_total(self) -> Decimal:
        """Saldo total incluyendo todos los estados"""
        return self.disponible + self.en_transito + self.bloqueado
    
    # ==========================================
    # MÉTODOS DE OPERACIÓN
    # ==========================================
    
    def bloquear_fondos(self, monto: Decimal) -> bool:
        """
        Bloquea fondos para una orden pendiente.
        
        Retorna: True si se pudo bloquear, False si saldo insuficiente.
        """
        if self.disponible >= monto:
            self.disponible -= monto
            self.bloqueado += monto
            return True
        return False
    
    def liberar_fondos(self, monto: Decimal) -> None:
        """Libera fondos previamente bloqueados"""
        if self.bloqueado >= monto:
            self.bloqueado -= monto
            self.disponible += monto
        else:
            raise ValueError("Fondos bloqueados insuficientes")
    
    def confirmar_deposito(self, monto: Decimal) -> None:
        """Confirma un depósito que estaba en tránsito"""
        if self.en_transito >= monto:
            self.en_transito -= monto
            self.disponible += monto
        else:
            raise ValueError("Fondos en tránsito insuficientes")
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'cuenta_id': self.cuenta_id,
            'moneda': self.moneda,
            'disponible': float(self.disponible),
            'en_transito': float(self.en_transito),
            'bloqueado': float(self.bloqueado),
            'saldo_proyectado': float(self.saldo_proyectado),
            'saldo_total': float(self.saldo_total)
        }
    
    def __repr__(self) -> str:
        return f"<SaldoDB(cuenta_id={self.cuenta_id}, moneda='{self.moneda}', disponible={self.disponible})>"


# ============================================================================
# 4. TÍTULOS Y MERCADO
# ============================================================================

class TituloDB(Base, AuditMixin):
    """
    Instrumentos financieros negociables en la BVC.
    
    Propósito: Catálogo de acciones, bonos y otros valores
    que se pueden comprar/vender en la bolsa.
    """
    __tablename__ = "titulos"
    
    # ==========================================
    # IDENTIFICACIÓN
    # ==========================================
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # RIF de la empresa emisora
    rif: Mapped[str] = mapped_column(String(15), nullable=False)
    
    # Nombre completo del título
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    
    # Símbolo bursátil (ej: 'BVCC' para Banco de Venezuela)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    
    # ==========================================
    # CLASIFICACIÓN
    # ==========================================
    
    # Sector económico (Financiero, Industrial, etc.)
    sector: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Tipo de mercado (Acciones, Bonos, ETF)
    mercado: Mapped[str] = mapped_column(String(10), default='Acciones')
    
    # Tipo de renta (Variable, Fija)
    tipo: Mapped[str] = mapped_column(String(15), default='Renta Variable')
    
    # ==========================================
    # ESTADO DE MERCADO
    # ==========================================
    
    # Indica si el título está activo o suspendido en la BVC
    estado_mercado: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Un título puede estar en múltiples órdenes
    ordenes = relationship("OrdenDB", back_populates="titulo")
    
    # Un título puede estar en múltiples portafolios
    portafolio_items = relationship("PortafolioItemDB", back_populates="titulo")
    
    # Un título tiene múltiples precios en el tiempo
    precios = relationship("PrecioTituloDB", back_populates="titulo")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para búsquedas frecuentes
        Index('idx_titulo_nombre', 'nombre'),
        Index('idx_titulo_sector', 'sector'),
        Index('idx_titulo_ticker', 'ticker'),
        Index('idx_titulo_mercado', 'mercado'),
        Index('idx_titulo_tipo', 'tipo'),
    )
    
    # ==========================================
    # PROPIEDADES CALCULADAS
    # ==========================================
    
    @property
    def precio_actual(self) -> Optional[Decimal]:
        """
        Obtiene el precio actual más reciente.
        
        Nota: Ya no almacenamos precio_actual como campo separado.
        Lo calculamos dinámicamente desde la tabla de precios.
        """
        if self.precios:
            # Filtrar precios actuales (tipo='ACTUAL')
            precios_actuales = [p for p in self.precios if p.tipo == 'ACTUAL']
            if precios_actuales:
                # Ordenar por fecha descendente y tomar el más reciente
                precios_actuales.sort(key=lambda x: x.fecha_hora, reverse=True)
                return precios_actuales[0].precio
        return None
    
    @property
    def fecha_actualizacion_precio(self) -> Optional[datetime]:
        """Obtiene la fecha del último precio actual"""
        if self.precios:
            precios_actuales = [p for p in self.precios if p.tipo == 'ACTUAL']
            if precios_actuales:
                precios_actuales.sort(key=lambda x: x.fecha_hora, reverse=True)
                return precios_actuales[0].fecha_hora
        return None
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'rif': self.rif,
            'nombre': self.nombre,
            'ticker': self.ticker,
            'sector': self.sector,
            'mercado': self.mercado,
            'tipo': self.tipo,
            'precio_actual': float(self.precio_actual) if self.precio_actual else None,
            'fecha_actualizacion_precio': (
                self.fecha_actualizacion_precio.isoformat() 
                if self.fecha_actualizacion_precio else None
            ),
            'estado_mercado': self.estado_mercado,
            'estatus': self.estatus
        }
    
    def __repr__(self) -> str:
        return f"<TituloDB(id={self.id}, ticker='{self.ticker}', nombre='{self.nombre}')>"


class PrecioTituloDB(Base, AuditMixin):
    """
    Historial de precios de títulos (actuales e históricos).
    
    CAMBIO IMPORTANTE: Unificamos precios_actuales y precios_historicos
    en una sola tabla con campo 'tipo' para diferenciar.
    
    Propósito: Almacenar todos los precios de mercado con sus metadatos.
    """
    __tablename__ = "precios_titulos"
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Título al que pertenece el precio
    titulo_id: Mapped[int] = mapped_column(ForeignKey("titulos.id"), nullable=False)
    
    # ==========================================
    # INFORMACIÓN DEL PRECIO
    # ==========================================
    
    # Fecha y hora del precio
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Precio del título
    precio: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    
    # Volumen negociado (opcional para históricos)
    volumen: Mapped[int] = mapped_column(Integer, default=0)
    
    # Tasa BCV del momento (para conversiones)
    tasa_bcv: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 4))
    
    # ==========================================
    # CAMPOS ESPECÍFICOS PARA PRECIOS DEL DÍA
    # ==========================================
    
    # Variación porcentual respecto al día anterior
    variacion: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 4))
    
    # Precios del día de operación
    precio_apertura: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8))
    precio_maximo: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8))
    precio_minimo: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8))
    
    # ==========================================
    # METADATOS
    # ==========================================
    
    # Tipo de precio: ACTUAL, HISTORICO_CIERRE, HISTORICO_INTRADIA
    tipo: Mapped[str] = mapped_column(String(20), default='ACTUAL')
    
    # Fuente del precio (API, scraping manual, etc.)
    fuente: Mapped[str] = mapped_column(String(50), default='MANUAL')
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con título
    titulo = relationship("TituloDB", back_populates="precios")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índice compuesto para búsquedas por título y fecha
        Index('idx_precio_titulo_fecha', 'titulo_id', 'fecha_hora'),
        
        # Índice para filtrar por tipo de precio
        Index('idx_precio_tipo', 'tipo'),
        
        # El precio siempre debe ser positivo
        CheckConstraint('precio > 0', name='check_precio_positivo'),
    )
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'titulo_id': self.titulo_id,
            'fecha_hora': self.fecha_hora.isoformat(),
            'precio': float(self.precio),
            'volumen': self.volumen,
            'tasa_bcv': float(self.tasa_bcv) if self.tasa_bcv else None,
            'variacion': float(self.variacion) if self.variacion else None,
            'precio_apertura': float(self.precio_apertura) if self.precio_apertura else None,
            'precio_maximo': float(self.precio_maximo) if self.precio_maximo else None,
            'precio_minimo': float(self.precio_minimo) if self.precio_minimo else None,
            'tipo': self.tipo,
            'fuente': self.fuente
        }
    
    def __repr__(self) -> str:
        return f"<PrecioTituloDB(titulo_id={self.titulo_id}, precio={self.precio}, tipo='{self.tipo}')>"


# ============================================================================
# 5. OPERACIONES BURSÁTILES
# ============================================================================

class OrdenDB(Base, AuditMixin):
    """
    Instrucción de compra o venta de títulos.
    
    Propósito: Representar la intención de un cliente de operar
    en el mercado. Una orden puede ejecutarse parcial o totalmente.
    """
    __tablename__ = "ordenes"
    
    # ==========================================
    # IDENTIFICACIÓN
    # ==========================================
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Cliente que crea la orden
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    
    # Cuenta bursátil desde la que se opera
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_bursatiles.id"), nullable=False)
    
    # Cuenta bancaria para cobros/pagos (opcional al crear)
    cuenta_bancaria_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cuentas_bancarias.id"), 
        nullable=True
    )
    
    # Título a comprar/vender
    titulo_id: Mapped[int] = mapped_column(ForeignKey("titulos.id"), nullable=False)
    
    # ==========================================
    # DETALLES DE LA ORDEN
    # ==========================================
    
    # Tipo: COMPRA o VENTA
    tipo: Mapped[TipoOrden] = mapped_column(SQLAlchemyEnum(TipoOrden))
    
    # Cantidad total de títulos a operar
    cantidad_total: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Precio límite: máximo para compra, mínimo para venta
    precio_limite: Mapped[Decimal] = mapped_column(DECIMAL(20, 8))
    
    # Estado actual de la orden
    estado: Mapped[EstadoOrden] = mapped_column(
        SQLAlchemyEnum(EstadoOrden), 
        default=EstadoOrden.PENDIENTE
    )
    
    # Fecha hasta la que es válida la orden
    fecha_vencimiento: Mapped[date] = mapped_column(Date)
    
    # ==========================================
    # INFORMACIÓN ADICIONAL
    # ==========================================
    
    # Observaciones del cliente o operador
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Comisiones estimadas (calculadas al crear)
    comision_estimada: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)
    
    # Monto total estimado (incluyendo comisiones)
    monto_total_estimado: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con cliente
    cliente = relationship("ClienteDB", back_populates="ordenes")
    
    # Relación con cuenta bursátil
    cuenta = relationship("CuentaBursatilDB", back_populates="ordenes")
    
    # Relación con cuenta bancaria
    cuenta_bancaria = relationship("CuentaBancariaDB")
    
    # Relación con título
    titulo = relationship("TituloDB", back_populates="ordenes")
    
    # Una orden puede generar múltiples transacciones (ejecución parcial)
    transacciones = relationship("TransaccionDB", back_populates="orden")
    
    # Una orden puede estar vinculada a múltiples movimientos de fondos
    movimientos_vinculados = relationship("OrdenMovimientoDB", back_populates="orden")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para consultas frecuentes
        Index('idx_orden_cliente', 'cliente_id'),
        Index('idx_orden_titulo', 'titulo_id'),
        Index('idx_orden_estado', 'estado'),
        Index('idx_orden_fecha', 'fecha_registro'),
        Index('idx_orden_cuenta', 'cuenta_id'),
        Index('idx_orden_vencimiento', 'fecha_vencimiento'),
        
        # La cantidad debe ser positiva
        CheckConstraint('cantidad_total > 0', name='check_orden_cantidad'),
    )
    
    # ==========================================
    # VALIDACIONES
    # ==========================================
    
    @validates('fecha_vencimiento')
    def validate_fecha_vencimiento(self, key: str, fecha_vencimiento: date) -> date:
        """Valida que la fecha de vencimiento no sea en el pasado"""
        if fecha_vencimiento < date.today():
            raise ValueError("La fecha de vencimiento no puede ser en el pasado")
        return fecha_vencimiento
    
    # ==========================================
    # PROPIEDADES CALCULADAS
    # ==========================================
    
    @property
    def cantidad_ejecutada(self) -> int:
        """Cantidad total ya ejecutada en transacciones"""
        return sum(t.cantidad_ejecutada for t in self.transacciones)
    
    @property
    def cantidad_pendiente(self) -> int:
        """Cantidad que falta por ejecutar"""
        return max(0, self.cantidad_total - self.cantidad_ejecutada)
    
    @property
    def porcentaje_ejecutado(self) -> float:
        """Porcentaje de la orden ya ejecutado"""
        if self.cantidad_total == 0:
            return 0.0
        return (self.cantidad_ejecutada / self.cantidad_total) * 100
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'cantidad_total': self.cantidad_total,
            'cantidad_ejecutada': self.cantidad_ejecutada,
            'cantidad_pendiente': self.cantidad_pendiente,
            'porcentaje_ejecutado': self.porcentaje_ejecutado,
            'precio_limite': float(self.precio_limite) if self.precio_limite else None,
            'cliente_id': self.cliente_id,
            'cuenta_id': self.cuenta_id,
            'titulo_id': self.titulo_id,
            'estado': self.estado.value,
            'fecha_creacion': self.fecha_registro.isoformat(),
            'fecha_vencimiento': self.fecha_vencimiento.isoformat(),
            'comision_estimada': float(self.comision_estimada) if self.comision_estimada else None,
            'monto_total_estimado': float(self.monto_total_estimado) if self.monto_total_estimado else None,
        }
    
    def __repr__(self) -> str:
        return f"<OrdenDB(id={self.id}, tipo='{self.tipo}', estado='{self.estado}', cantidad={self.cantidad_total})>"


class TransaccionDB(Base, AuditMixin):
    """
    Ejecución real de una orden en la bolsa (calce).
    
    Propósito: Registrar cada ejecución parcial o total de una orden,
    con todos los detalles financieros (comisiones, tasas, etc.).
    """
    __tablename__ = "transacciones"
    
    # ==========================================
    # IDENTIFICACIÓN
    # ==========================================
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Orden que generó esta transacción
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    
    # ==========================================
    # EJECUCIÓN
    # ==========================================
    
    # Cantidad realmente ejecutada
    cantidad_ejecutada: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Precio al que se ejecutó
    precio_ejecucion: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    
    # Monto bruto (cantidad × precio)
    monto_bruto: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    
    # ==========================================
    # DESGLOSE DE COMISIONES (CRUCIAL PARA BVC)
    # ==========================================
    
    # Comisión de la casa de bolsa (corretaje)
    comision_corretaje: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=Decimal('0.0'))
    
    # Comisión de la Bolsa de Valores de Caracas
    comision_bvc: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=Decimal('0.0'))
    
    # Comisión de la Caja Venezolana de Valores
    comision_cvv: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=Decimal('0.0'))
    
    # IVA sobre las comisiones
    iva: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=Decimal('0.0'))
    
    # ==========================================
    # TOTALES
    # ==========================================
    
    # Monto neto (bruto + todas las comisiones)
    monto_neto: Mapped[Decimal] = mapped_column(DECIMAL(20, 8))
    
    # ==========================================
    # INFORMACIÓN DE MERCADO
    # ==========================================
    
    # Tasa BCV al momento de la ejecución
    tasa_bcv: Mapped[Decimal] = mapped_column(DECIMAL(20, 4))
    
    # Número único de operación asignado por la BVC
    numero_operacion_bvc: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con orden
    orden = relationship("OrdenDB", back_populates="transacciones")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para consultas frecuentes
        Index('idx_transaccion_fecha', 'fecha_registro'),
        Index('idx_transaccion_numero_bvc', 'numero_operacion_bvc'),
        Index('idx_transaccion_orden', 'orden_id'),
        
        # Restricciones de integridad
        CheckConstraint('cantidad_ejecutada > 0', name='check_transaccion_cantidad'),
        CheckConstraint('precio_ejecucion > 0', name='check_precio_positivo'),
    )
    
    # ==========================================
    # PROPIEDADES CALCULADAS
    # ==========================================
    
    @property
    def total_comisiones(self) -> Decimal:
        """Suma de todas las comisiones"""
        return self.comision_corretaje + self.comision_bvc + self.comision_cvv + self.iva
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
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
            'total_comisiones': float(self.total_comisiones),
            'monto_neto': float(self.monto_neto),
            'tasa_bcv': float(self.tasa_bcv),
            'numero_operacion_bvc': self.numero_operacion_bvc,
            'fecha_registro': self.fecha_registro.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<TransaccionDB(id={self.id}, orden_id={self.orden_id}, cantidad={self.cantidad_ejecutada}, precio={self.precio_ejecucion})>"


# ============================================================================
# 6. MOVIMIENTOS FINANCIEROS
# ============================================================================

class MovimientoDB(Base, AuditMixin):
    """
    Depósitos, retiros y transferencias de fondos.
    
    Propósito: Registrar cada movimiento de dinero entre cuentas
    bancarias y cuentas bursátiles.
    """
    __tablename__ = "movimientos"
    
    # ==========================================
    # IDENTIFICACIÓN
    # ==========================================
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Cuenta bursátil afectada
    cuenta_bursatil_id: Mapped[int] = mapped_column(
        ForeignKey("cuentas_bursatiles.id"), 
        nullable=False
    )
    
    # Cuenta bancaria origen/destino
    cuenta_bancaria_id: Mapped[int] = mapped_column(
        ForeignKey("cuentas_bancarias.id"), 
        nullable=False
    )
    
    # ==========================================
    # DETALLES DEL MOVIMIENTO
    # ==========================================
    
    # Tipo: DEPOSITO o RETIRO
    tipo: Mapped[TipoMovimiento] = mapped_column(SQLAlchemyEnum(TipoMovimiento), nullable=False)
    
    # Monto del movimiento
    monto: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    
    # Moneda del movimiento
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default='VES')
    
    # ==========================================
    # ESTADO Y FECHAS
    # ==========================================
    
    # Estado actual del movimiento
    estado: Mapped[EstadoMovimiento] = mapped_column(
        SQLAlchemyEnum(EstadoMovimiento), 
        default=EstadoMovimiento.PENDIENTE
    )
    
    # Fecha en que se solicitó
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Fecha en que se completó (si aplica)
    fecha_completado: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # ==========================================
    # INFORMACIÓN DE AUDITORÍA
    # ==========================================
    
    # Referencia bancaria (número de depósito/transferencia)
    referencia_bancaria: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Ruta al comprobante digital
    comprobante_ruta: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Observaciones del operador
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Tasa BCV al momento del movimiento
    tasa_bcv: Mapped[Decimal] = mapped_column(DECIMAL(20, 4), nullable=False)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con cuenta bursátil
    cuenta_bursatil = relationship("CuentaBursatilDB", back_populates="movimientos")
    
    # Relación con cuenta bancaria
    cuenta_bancaria = relationship("CuentaBancariaDB", back_populates="movimientos")
    
    # Un movimiento puede estar vinculado a múltiples órdenes
    ordenes_vinculadas = relationship("OrdenMovimientoDB", back_populates="movimiento")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para consultas frecuentes
        Index('idx_movimiento_fecha', 'fecha_solicitud'),
        Index('idx_movimiento_estado', 'estado'),
        Index('idx_movimiento_tipo', 'tipo'),
        Index('idx_movimiento_cuenta_bursatil', 'cuenta_bursatil_id'),
        Index('idx_movimiento_cuenta_bancaria', 'cuenta_bancaria_id'),
        
        # El monto siempre debe ser positivo
        CheckConstraint('monto > 0', name='check_movimiento_monto_positivo'),
    )
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
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
    
    def __repr__(self) -> str:
        return f"<MovimientoDB(id={self.id}, tipo='{self.tipo}', monto={self.monto}, estado='{self.estado}')>"


class OrdenMovimientoDB(Base):  # NOTA: No hereda AuditMixin (solo tabla de relación)
    """
    Tabla de relación entre órdenes y movimientos de fondos.
    
    CAMBIO IMPORTANTE: Solo tabla de relación, sin campos de auditoría.
    
    Propósito: Vincular depósitos con órdenes de compra que los financian,
    y retiros con órdenes de venta que los generan.
    """
    __tablename__ = "ordenes_movimientos"
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Orden vinculada
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    
    # Movimiento vinculado
    movimiento_id: Mapped[int] = mapped_column(ForeignKey("movimientos.id"), nullable=False)
    
    # Tipo de relación
    tipo_relacion: Mapped[str] = mapped_column(String(30), nullable=False)
    # Valores posibles: 'DEPOSITO_PARA_COMPRA', 'RETIRO_POST_VENTA'
    
    # Fecha en que se creó la relación
    fecha_asociacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con orden
    orden = relationship("OrdenDB", back_populates="movimientos_vinculados")
    
    # Relación con movimiento
    movimiento = relationship("MovimientoDB", back_populates="ordenes_vinculadas")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para consultas frecuentes
        Index('idx_orden_movimiento_orden', 'orden_id'),
        Index('idx_orden_movimiento_movimiento', 'movimiento_id'),
        
        # Evitar relaciones duplicadas
        UniqueConstraint('orden_id', 'movimiento_id', name='uq_orden_movimiento'),
    )
    
    def __repr__(self) -> str:
        return f"<OrdenMovimientoDB(orden_id={self.orden_id}, movimiento_id={self.movimiento_id}, tipo='{self.tipo_relacion}')>"


# ============================================================================
# 7. PORTAFOLIO Y POSICIONES
# ============================================================================

class PortafolioItemDB(Base, AuditMixin):
    """
    Posiciones de títulos que posee un cliente.
    
    Propósito: Resumen consolidado de las inversiones de un cliente
    en una cuenta bursátil específica.
    """
    __tablename__ = "portafolio_items"
    
    # ==========================================
    # IDENTIFICACIÓN
    # ==========================================
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Cuenta bursátil que posee el título
    cuenta_id: Mapped[int] = mapped_column(
        ForeignKey("cuentas_bursatiles.id"), 
        nullable=False
    )
    
    # Título poseído
    titulo_id: Mapped[int] = mapped_column(ForeignKey("titulos.id"), nullable=False)
    
    # ==========================================
    # POSICIÓN
    # ==========================================
    
    # Cantidad total de títulos poseídos
    cantidad: Mapped[int] = mapped_column(Integer, default=0)
    
    # Costo promedio por título (para cálculo de ganancias)
    costo_promedio: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), default=Decimal('0.0'))
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con cuenta bursátil
    cuenta = relationship("CuentaBursatilDB", back_populates="portafolio")
    
    # Relación con título
    titulo = relationship("TituloDB", back_populates="portafolio_items")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para consultas frecuentes
        Index('idx_portafolio_cuenta', 'cuenta_id'),
        Index('idx_portafolio_titulo', 'titulo_id'),
        
        # Una cuenta no puede tener duplicados del mismo título
        UniqueConstraint('cuenta_id', 'titulo_id', name='uq_cuenta_titulo'),
        
        # La cantidad no puede ser negativa
        CheckConstraint('cantidad >= 0', name='check_cantidad_no_negativa'),
    )
    
    # ==========================================
    # PROPIEDADES CALCULADAS
    # ==========================================
    
    @property
    def valor_actual(self) -> Decimal:
        """Valor actual de la posición (cantidad × precio actual)"""
        if self.titulo and self.titulo.precio_actual:
            return Decimal(self.cantidad) * self.titulo.precio_actual
        return Decimal('0.0')
    
    @property
    def costo_total(self) -> Decimal:
        """Costo total de la posición (cantidad × costo promedio)"""
        return Decimal(self.cantidad) * self.costo_promedio
    
    @property
    def ganancia_perdida(self) -> Decimal:
        """Ganancia/pérdida no realizada (valor actual - costo total)"""
        return self.valor_actual - self.costo_total
    
    @property
    def ganancia_perdida_porcentaje(self) -> Decimal:
        """Porcentaje de ganancia/pérdida"""
        if self.costo_total > 0:
            return ((self.valor_actual / self.costo_total) - 1) * 100
        return Decimal('0.0')
    
    # ==========================================
    # MÉTODOS DE OPERACIÓN
    # ==========================================
    
    def actualizar_posicion(self, cantidad: int, precio_compra: Decimal) -> None:
        """
        Actualiza la posición después de una compra/venta.
        
        Para compras: aumenta cantidad, recalcula costo promedio.
        Para ventas: disminuye cantidad (FIFO o costo promedio).
        """
        if cantidad == 0:
            return
        
        if cantidad > 0:  # COMPRA
            # Calcular nuevo costo promedio
            costo_total_actual = self.costo_total
            costo_nueva_compra = Decimal(cantidad) * precio_compra
            
            self.cantidad += cantidad
            if self.cantidad > 0:
                self.costo_promedio = (costo_total_actual + costo_nueva_compra) / self.cantidad
        
        else:  # VENTA (cantidad negativa)
            cantidad_venta = abs(cantidad)
            if self.cantidad < cantidad_venta:
                raise ValueError("No hay suficientes títulos para vender")
            
            # Método FIFO simplificado: no afecta costo promedio
            self.cantidad -= cantidad_venta
            
            # Si se vendió todo, resetear costo promedio
            if self.cantidad == 0:
                self.costo_promedio = Decimal('0.0')
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'cuenta_id': self.cuenta_id,
            'titulo_id': self.titulo_id,
            'cantidad': self.cantidad,
            'costo_promedio': float(self.costo_promedio),
            'valor_actual': float(self.valor_actual),
            'costo_total': float(self.costo_total),
            'ganancia_perdida': float(self.ganancia_perdida),
            'ganancia_perdida_porcentaje': float(self.ganancia_perdida_porcentaje),
            'fecha_registro': self.fecha_registro.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<PortafolioItemDB(cuenta_id={self.cuenta_id}, titulo_id={self.titulo_id}, cantidad={self.cantidad})>"


# ============================================================================
# 8. SOPORTE Y CONFIGURACIÓN
# ============================================================================

class DocumentoDB(Base, AuditMixin):
    """
    Documentos digitalizados de clientes.
    
    Propósito: Almacenar metadatos de documentos requeridos por regulación
    (cédulas, RIF, estados de cuenta, poderes, etc.).
    """
    __tablename__ = "documentos"
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Cliente dueño del documento
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    
    # ==========================================
    # INFORMACIÓN DEL DOCUMENTO
    # ==========================================
    
    # Tipo de documento (Cédula, RIF, Estados de cuenta, etc.)
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Nombre original del archivo
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Ruta en el sistema de archivos o URL
    ruta_archivo: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Fecha de subida
    fecha_subida: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Si el documento ha sido verificado por administración
    verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación con cliente
    cliente = relationship("ClienteDB", back_populates="documentos")
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para consultas frecuentes
        Index('idx_documento_cliente', 'cliente_id'),
        Index('idx_documento_tipo', 'tipo_documento'),
    )
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'tipo_documento': self.tipo_documento,
            'nombre_archivo': self.nombre_archivo,
            'fecha_subida': self.fecha_subida.isoformat(),
            'verificado': self.verificado
        }
    
    def __repr__(self) -> str:
        return f"<DocumentoDB(id={self.id}, cliente_id={self.cliente_id}, tipo='{self.tipo_documento}')>"


class ConfiguracionDB(Base, AuditMixin):
    """
    Configuración general de la aplicación.
    
    CAMBIO IMPORTANTE: Unificamos config_comisiones y configuraciones
    en una sola tabla con categorías.
    
    Propósito: Almacenar parámetros configurables del sistema,
    incluyendo comisiones, tasas, límites y preferencias.
    """
    __tablename__ = "configuraciones"
    
    # ==========================================
    # IDENTIFICACIÓN
    # ==========================================
    
    # ID único
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Clave única de configuración
    clave: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Valor almacenado (siempre como string)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    
    # ==========================================
    # METADATOS
    # ==========================================
    
    # Tipo de dato para conversión
    tipo: Mapped[str] = mapped_column(String(20), default='string')
    # Valores: string, number, boolean, json
    
    # Categoría para agrupar configuraciones
    categoria: Mapped[str] = mapped_column(String(50), default='General')
    # Valores: General, Comisiones, Seguridad, Reportes, UI
    
    # Descripción para la interfaz de administración
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Si puede ser editada desde la UI
    editable: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # ==========================================
    # CAMPOS ESPECÍFICOS PARA COMISIONES
    # ==========================================
    
    # Para categoría='COMISIONES': indica si aplica a títulos
    aplica_a_titulo: Mapped[Optional[bool]] = mapped_column(Boolean, default=None)
    
    # Para categoría='COMISIONES': valor porcentual
    valor_porcentaje: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 4))
    
    # ==========================================
    # CONFIGURACIÓN DE LA TABLA
    # ==========================================
    
    __table_args__ = (
        # Índices para consultas frecuentes
        Index('idx_config_clave', 'clave'),
        Index('idx_config_categoria', 'categoria'),
        Index('idx_config_clave_categoria', 'clave', 'categoria'),
    )
    
    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def get_value(self):
        """
        Obtiene el valor convertido según el tipo.
        
        Este método es crucial porque almacenamos todo como string
        pero necesitamos tipos específicos en la aplicación.
        """
        if self.tipo == 'number':
            try:
                return float(self.valor)
            except ValueError:
                return 0.0
        elif self.tipo == 'boolean':
            # Convierte string a booleano
            return self.valor.lower() in ('true', '1', 'yes', 'si', 'verdadero')
        elif self.tipo == 'json':
            try:
                import json
                return json.loads(self.valor)
            except:
                return {}
        else:  # string
            return self.valor
    
    def set_value(self, value) -> None:
        """Establece el valor convirtiéndolo a string según tipo"""
        if self.tipo == 'number':
            self.valor = str(float(value))
        elif self.tipo == 'boolean':
            self.valor = 'true' if value else 'false'
        elif self.tipo == 'json':
            import json
            self.valor = json.dumps(value)
        else:
            self.valor = str(value)
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.get_value(),  # Valor convertido
            'tipo': self.tipo,
            'categoria': self.categoria,
            'descripcion': self.descripcion,
            'editable': self.editable,
            'aplica_a_titulo': self.aplica_a_titulo,
            'valor_porcentaje': float(self.valor_porcentaje) if self.valor_porcentaje else None,
        }
    
    def __repr__(self) -> str:
        return f"<ConfiguracionDB(clave='{self.clave}', categoria='{self.categoria}', valor='{self.valor}')>"


# ============================================================================
# 9. CLASE AUXILIAR PARA CÁLCULOS
# ============================================================================

class CalculadoraComisiones:
    """
    Helper para calcular comisiones de operaciones bursátiles.
    
    Propósito: Centralizar la lógica de cálculo de comisiones
    según la regulación venezolana y parámetros configurados.
    """
    
    @staticmethod
    def calcular_comisiones(
        monto_bruto: Decimal,
        tasa_corretaje: Decimal = Decimal('0.005'),   # 0.5%
        tasa_bvc: Decimal = Decimal('0.0005'),        # 0.05%
        tasa_cvv: Decimal = Decimal('0.0003'),        # 0.03%
        tasa_iva: Decimal = Decimal('0.16')           # 16%
    ) -> dict:
        """
        Calcula todas las comisiones para una operación bursátil.
        
        Args:
            monto_bruto: Monto total de la operación (cantidad × precio)
            tasa_*: Tasas de comisión (por defecto valores típicos BVC)
        
        Returns:
            Diccionario con desglose completo de comisiones
        """
        # Comisiones individuales
        comision_corretaje = monto_bruto * tasa_corretaje
        comision_bvc = monto_bruto * tasa_bvc
        comision_cvv = monto_bruto * tasa_cvv
        
        # Subtotal antes de IVA
        subtotal_comisiones = comision_corretaje + comision_bvc + comision_cvv
        
        # IVA sobre las comisiones
        iva = subtotal_comisiones * tasa_iva
        
        # Totales
        total_comisiones = subtotal_comisiones + iva
        
        # Para compras: monto neto = bruto + comisiones
        # Para ventas: monto neto = bruto - comisiones
        # El signo se maneja en la lógica de negocio
        
        return {
            'comision_corretaje': comision_corretaje,
            'comision_bvc': comision_bvc,
            'comision_cvv': comision_cvv,
            'subtotal_comisiones': subtotal_comisiones,
            'iva': iva,
            'total_comisiones': total_comisiones,
            'monto_neto': monto_bruto + total_comisiones,  # Para compras
        }
    
    @staticmethod
    def obtener_tasas_desde_config(configuraciones: list) -> dict:
        """
        Obtiene tasas de comisión desde la tabla de configuraciones.
        
        Args:
            configuraciones: Lista de objetos ConfiguracionDB
        
        Returns:
            Diccionario con tasas para cálculo
        """
        tasas = {
            'tasa_corretaje': Decimal('0.005'),
            'tasa_bvc': Decimal('0.0005'),
            'tasa_cvv': Decimal('0.0003'),
            'tasa_iva': Decimal('0.16'),
        }
        
        # Buscar en configuraciones
        for config in configuraciones:
            if config.categoria == 'COMISIONES' and config.valor_porcentaje:
                clave = config.clave.lower()
                if 'corretaje' in clave:
                    tasas['tasa_corretaje'] = config.valor_porcentaje / 100
                elif 'bvc' in clave:
                    tasas['tasa_bvc'] = config.valor_porcentaje / 100
                elif 'cvv' in clave:
                    tasas['tasa_cvv'] = config.valor_porcentaje / 100
                elif 'iva' in clave:
                    tasas['tasa_iva'] = config.valor_porcentaje / 100
        
        return tasas