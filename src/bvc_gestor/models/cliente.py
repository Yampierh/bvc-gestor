# src/bvc_gestor/models/cliente.py
"""
Modelo Cliente para Venezuela con validaciones específicas
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
from ..utils.validators_venezuela import validar_rif, validar_telefono, validar_email, validar_nmro_cuenta_bancaria
from ..utils.constants import TipoInversor, PerfilRiesgo

@dataclass
class Cliente:
    """Cliente del sistema bursátil venezolano"""
    
    # Información básica
    rif_cedula: str
    tipo_inversor: TipoInversor
    nombre_completo: str

    # Información de contacto
    telefono: str
    email: str
    direccion_fiscal: str
    ciudad_estado: str

    
    # Información financiera
    perfil_riesgo: PerfilRiesgo = PerfilRiesgo.MODERADO
    
    # Información bancaria
    banco: Optional[str] = None
    numero_cuenta: Optional[str] = None
    
    # Metadatos
    fecha_registro: datetime = field(default_factory=datetime.now)
    activo: bool = True
    
    # Relaciones (no serializadas en dataclass)
    cuentas: List = field(default_factory=list)
    documentos: List = field(default_factory=list)
    
    def __post_init__(self):
        
        # Validar RIF/Cédula
        if not validar_rif(self.rif_cedula):
            raise ValueError(f"RIF/Cédula inválido: {self.rif_cedula}")
        # Validar teléfono
        if not validar_telefono(self.telefono):
            raise ValueError(f"Teléfono inválido: {self.telefono}")
        
        # Validar email básico
        if not validar_email(self.email):
            raise ValueError(f"Email inválido: {self.email}")
        
    def obtener_resumen(self) -> dict:
        """Obtener resumen del cliente"""
        return {
            'rif_cedula': self.rif_cedula,
            'nombre': self.nombre_completo,
            'tipo_inversor': self.tipo_inversor.value,
            'telefono': self.telefono,
            'email': self.email,
            'perfil_riesgo': self.perfil_riesgo.value,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d'),
            'activo': self.activo
        }
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para serialización"""
        data = {
            'rif_cedula': self.rif_cedula,
            'tipo_inversor': self.tipo_inversor.value,
            'nombre_completo': self.nombre_completo,
            'telefono': self.telefono,
            'email': self.email,
            'direccion_fiscal': self.direccion_fiscal,
            'ciudad_estado': self.ciudad_estado,
            'perfil_riesgo': self.perfil_riesgo.value,
            'banco': self.banco,
            'numero_cuenta': self.numero_cuenta,
            'fecha_registro': self.fecha_registro.isoformat(),
            'activo': self.activo,
        }
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Cliente':
        """Crear cliente desde diccionario"""
        # Convertir strings a enums
        if 'tipo_inversor' in data:
            data['tipo_inversor'] = TipoInversor(data['tipo_inversor'])
        if 'perfil_riesgo' in data:
            data['perfil_riesgo'] = PerfilRiesgo(data['perfil_riesgo'])
        
        return cls(**data)