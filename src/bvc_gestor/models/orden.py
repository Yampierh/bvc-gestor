# src/bvc_gestor/models/orden.py
"""
Modelo Orden para operaciones bursátiles
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
from decimal import Decimal
from ..utils.constants import TipoOrden, TipoOperacion, EstadoOrden

@dataclass
class Orden:
    """Orden bursátil"""
    
    id = int
    numero_orden: str
    cliente_id: str
    cuenta_id: int
    activo_id: str
    
    # Tipo de orden
    tipo_orden: TipoOrden
    tipo_operacion: TipoOperacion
    
    # Detalles
    cantidad: int
    precio: Optional[Decimal] = None  # Null para órdenes de mercado
    precio_limite: Optional[Decimal] = None
    
    # Estado
    estado: EstadoOrden = EstadoOrden.PENDIENTE
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_ejecucion: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    
    # Ejecución
    cantidad_ejecutada: int = 0
    precio_ejecucion_promedio: Optional[Decimal] = None
    numero_operacion_bvc: Optional[str] = None
    
    # Comisiones
    comision_base: Decimal = Decimal('0.00')
    iva_comision: Decimal = Decimal('0.00')
    comision_total: Decimal = Decimal('0.00')
    
    # Validaciones
    validada: bool = False
    motivo_rechazo: Optional[str] = None
    
    # Metadatos
    notas: Optional[str] = None
    
    def __post_init__(self):
        """Validar datos después de inicialización"""
        self.validar_datos()
    
    def validar_datos(self):
        """Validar datos de la orden"""
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        
        if self.tipo_operacion == TipoOperacion.LIMITADA and not self.precio_limite:
            raise ValueError("Las órdenes limitadas requieren precio límite")
        
        if self.precio_limite and self.precio_limite <= 0:
            raise ValueError("El precio límite debe ser mayor a cero")
    
    @property
    def monto_total(self) -> Optional[Decimal]:
        """Calcular monto total de la orden"""
        if self.precio:
            return Decimal(self.cantidad) * self.precio
        return None
    
    @property
    def monto_ejecutado(self) -> Decimal:
        """Calcular monto ejecutado"""
        if self.precio_ejecucion_promedio and self.cantidad_ejecutada:
            return Decimal(self.cantidad_ejecutada) * self.precio_ejecucion_promedio
        return Decimal('0.00')
    
    @property
    def porcentaje_ejecutado(self) -> float:
        """Calcular porcentaje ejecutado"""
        if self.cantidad > 0:
            return (self.cantidad_ejecutada / self.cantidad) * 100
        return 0.0
    
    def calcular_comisiones(self, comision_base_porcentaje: float, iva_porcentaje: float):
        """Calcular comisiones de la orden"""
        if not self.monto_total:
            return
        
        self.comision_base = self.monto_total * Decimal(str(comision_base_porcentaje))
        self.iva_comision = self.comision_base * Decimal(str(iva_porcentaje))
        self.comision_total = self.comision_base + self.iva_comision
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'numero_orden': self.numero_orden,
            'cliente_id': self.cliente_id,
            'activo_id': self.activo_id,
            'tipo_orden': self.tipo_orden.value,
            'tipo_operacion': self.tipo_operacion.value,
            'cantidad': self.cantidad,
            'precio': float(self.precio) if self.precio else None,
            'precio_limite': float(self.precio_limite) if self.precio_limite else None,
            'estado': self.estado.value,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'cantidad_ejecutada': self.cantidad_ejecutada,
            'porcentaje_ejecutado': self.porcentaje_ejecutado,
            'comision_total': float(self.comision_total),
            'validada': self.validada
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Orden':
        """Crear orden desde diccionario"""
        # Convertir strings a enums
        if 'tipo_orden' in data:
            data['tipo_orden'] = TipoOrden(data['tipo_orden'])
        if 'tipo_operacion' in data:
            data['tipo_operacion'] = TipoOperacion(data['tipo_operacion'])
        if 'estado' in data:
            data['estado'] = EstadoOrden(data['estado'])
        
        # Convertir strings a Decimal
        decimal_fields = ['precio', 'precio_limite', 'precio_ejecucion_promedio', 
                        'comision_base', 'iva_comision', 'comision_total']
        for field in decimal_fields:
            if field in data and data[field] is not None:
                data[field] = Decimal(str(data[field]))
        
        # Convertir strings a datetime
        date_fields = ['fecha_creacion', 'fecha_ejecucion', 'fecha_vencimiento']
        for field in date_fields:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)