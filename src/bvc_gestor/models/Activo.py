# src/bvc_gestor/models/activo.py
"""
Modelo Activo para instrumentos bursátiles BVC
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum

class TipoActivo(str, Enum):
    ACCION = "Acción"
    BONO = "Bono"
    ETF = "ETF"
    FONDO = "Fondo de Inversión"
    DEUDA = "Título de Deuda"

@dataclass
class Activo:
    """Activo bursátil de la BVC"""
    
    id: str  # Símbolo: BNC, EMPV, etc.
    nombre: str
    tipo: TipoActivo
    sector: Optional[str] = None
    subsector: Optional[str] = None
    
    # Información bursátil
    moneda: str = "USD"
    precio_actual: Decimal = Decimal('0.00')
    precio_anterior: Decimal = Decimal('0.00')
    variacion_diaria: Decimal = Decimal('0.00')
    volumen_promedio: int = 0
    
    # Características
    lote_standard: int = 100
    lote_minimo: int = 1
    precio_minimo: Optional[Decimal] = None
    precio_maximo: Optional[Decimal] = None
    
    # Estado
    activo: bool = True
    fecha_ingreso: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validar datos"""
        if self.precio_actual < 0:
            raise ValueError("El precio no puede ser negativo")
        
        if self.lote_standard <= 0:
            raise ValueError("El lote estándar debe ser mayor a cero")
    
    @property
    def variacion_porcentaje(self) -> Decimal:
        """Calcular variación porcentual"""
        if self.precio_anterior > 0:
            return ((self.precio_actual - self.precio_anterior) / self.precio_anterior) * Decimal('100')
        return Decimal('0.00')
    
    def actualizar_precio(self, nuevo_precio: Decimal):
        """Actualizar precio del activo"""
        self.precio_anterior = self.precio_actual
        self.precio_actual = nuevo_precio
        self.variacion_diaria = self.precio_actual - self.precio_anterior
        self.fecha_actualizacion = datetime.now()
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo.value,
            'sector': self.sector,
            'subsector': self.subsector,
            'moneda': self.moneda,
            'precio_actual': float(self.precio_actual),
            'precio_anterior': float(self.precio_anterior),
            'variacion_diaria': float(self.variacion_diaria),
            'variacion_porcentaje': float(self.variacion_porcentaje),
            'volumen_promedio': self.volumen_promedio,
            'lote_standard': self.lote_standard,
            'activo': self.activo,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Activo':
        """Crear activo desde diccionario"""
        # Convertir strings a enums
        if 'tipo' in data:
            data['tipo'] = TipoActivo(data['tipo'])
        
        # Convertir strings a Decimal
        decimal_fields = ['precio_actual', 'precio_anterior', 'variacion_diaria',
                        'precio_minimo', 'precio_maximo']
        for field in decimal_fields:
            if field in data and data[field] is not None:
                data[field] = Decimal(str(data[field]))
        
        # Convertir strings a datetime
        date_fields = ['fecha_ingreso', 'fecha_actualizacion']
        for field in date_fields:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)