# src/bvc_gestor/models/cliente.py
"""
Modelo Cliente para Venezuela con validaciones específicas
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
from ..utils.validators_venezuela import validar_cedula, validar_rif, validar_telefono_venezolano

class TipoCliente(str, Enum):
    NATURAL = "Natural"
    JURIDICO = "Jurídico"

class EstadoCivil(str, Enum):
    SOLTERO = "Soltero/a"
    CASADO = "Casado/a"
    DIVORCIADO = "Divorciado/a"
    VIUDO = "Viudo/a"

@dataclass
class Cliente:
    """Cliente del sistema bursátil venezolano"""
    
    # Información básica
    id: str  # Cédula o RIF
    tipo: TipoCliente
    nombre_completo: str
    fecha_nacimiento: Optional[datetime] = None
    estado_civil: Optional[EstadoCivil] = None
    profesion: Optional[str] = None
    
    # Información de contacto
    telefono_principal: str
    telefono_secundario: Optional[str] = None
    email: str
    direccion: str
    ciudad: str
    estado: str
    codigo_postal: Optional[str] = None
    
    # Información financiera
    perfil_riesgo: str = "Moderado"  # Conservador, Moderado, Agresivo
    limite_inversion_bs: float = 0.0
    limite_inversion_usd: float = 0.0
    ingresos_mensuales_bs: Optional[float] = None
    ingresos_mensuales_usd: Optional[float] = None
    
    # Información bancaria
    banco_principal: Optional[str] = None
    numero_cuenta: Optional[str] = None
    tipo_cuenta: Optional[str] = None  # Ahorros, Corriente
    
    # Documentación
    tiene_patrimonio_declarado: bool = False
    monto_patrimonio_bs: Optional[float] = None
    monto_patrimonio_usd: Optional[float] = None
    
    # Metadatos
    fecha_registro: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    activo: bool = True
    notas: Optional[str] = None
    
    # Relaciones (no serializadas en dataclass)
    cuentas: List = field(default_factory=list)
    documentos: List = field(default_factory=list)
    
    def __post_init__(self):
        """Validar datos después de la inicialización"""
        self.validar_datos()
        
    def validar_datos(self):
        """Validar datos del cliente según normas venezolanas"""
        # Validar identificación
        if self.tipo == TipoCliente.NATURAL:
            if not validar_cedula(self.id):
                raise ValueError(f"Cédula inválida: {self.id}")
        else:  # Jurídico
            if not validar_rif(self.id):
                raise ValueError(f"RIF inválido: {self.id}")
        
        # Validar teléfono
        if not validar_telefono_venezolano(self.telefono_principal):
            raise ValueError(f"Teléfono inválido: {self.telefono_principal}")
        
        # Validar email básico
        if '@' not in self.email or '.' not in self.email:
            raise ValueError(f"Email inválido: {self.email}")
    
    def calcular_edad(self) -> Optional[int]:
        """Calcular edad del cliente"""
        if not self.fecha_nacimiento:
            return None
        hoy = datetime.now()
        edad = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad
    
    def obtener_resumen(self) -> dict:
        """Obtener resumen del cliente"""
        return {
            'id': self.id,
            'nombre': self.nombre_completo,
            'tipo': self.tipo.value,
            'telefono': self.telefono_principal,
            'email': self.email,
            'perfil_riesgo': self.perfil_riesgo,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d'),
            'activo': self.activo
        }
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para serialización"""
        data = {
            'id': self.id,
            'tipo': self.tipo.value,
            'nombre_completo': self.nombre_completo,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'estado_civil': self.estado_civil.value if self.estado_civil else None,
            'profesion': self.profesion,
            'telefono_principal': self.telefono_principal,
            'telefono_secundario': self.telefono_secundario,
            'email': self.email,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'estado': self.estado,
            'codigo_postal': self.codigo_postal,
            'perfil_riesgo': self.perfil_riesgo,
            'limite_inversion_bs': self.limite_inversion_bs,
            'limite_inversion_usd': self.limite_inversion_usd,
            'ingresos_mensuales_bs': self.ingresos_mensuales_bs,
            'ingresos_mensuales_usd': self.ingresos_mensuales_usd,
            'banco_principal': self.banco_principal,
            'numero_cuenta': self.numero_cuenta,
            'tipo_cuenta': self.tipo_cuenta,
            'tiene_patrimonio_declarado': self.tiene_patrimonio_declarado,
            'monto_patrimonio_bs': self.monto_patrimonio_bs,
            'monto_patrimonio_usd': self.monto_patrimonio_usd,
            'fecha_registro': self.fecha_registro.isoformat(),
            'fecha_actualizacion': self.fecha_actualizacion.isoformat(),
            'activo': self.activo,
            'notas': self.notas
        }
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Cliente':
        """Crear cliente desde diccionario"""
        # Convertir strings a enums
        if 'tipo' in data:
            data['tipo'] = TipoCliente(data['tipo'])
        if 'estado_civil' in data and data['estado_civil']:
            data['estado_civil'] = EstadoCivil(data['estado_civil'])
        
        # Convertir strings a datetime
        date_fields = ['fecha_nacimiento', 'fecha_registro', 'fecha_actualizacion']
        for field in date_fields:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)