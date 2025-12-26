# src/bvc_gestor/utils/validators_venezuela.py
"""
Validadores específicos para datos venezolanos
"""
import re
from datetime import datetime
from typing import Optional, Tuple
from .constants import TipoPersona, TipoDocumento

def validar_cedula(cedula: str) -> bool:
    """
    Validar cédula venezolana (V-12345678 o E-12345678)
    Formato: [V|E]-[7-8 dígitos]
    """
    if not cedula:
        return False
    
    patron = r'^[VEve]-?\d{7,8}$'
    if not re.match(patron, cedula):
        return False
    
    # Limpiar guión si existe
    cedula_limpia = cedula.replace('-', '')
    
    # Verificar que no sea una cédula de prueba común
    cedulas_invalidas = ['V-11111111', 'V-22222222', 'V-12345678', 'E-11111111']
    if cedula in cedulas_invalidas or cedula_limpia in cedulas_invalidas:
        return False
    
    return True

def validar_rif(rif: str) -> bool:
    """
    Validar RIF venezolano (J-12345678-9)
    Formato: [J|G|V|E]-[8 dígitos]-[1 dígito verificador]
    """
    if not rif:
        return False
    
    patron = r'^[JGVEPjgvep]-?\d{8}-?\d$'
    if not re.match(patron, rif):
        return False
    
    # Limpiar guiones
    rif_limpio = rif.replace('-', '')
    
    # Verificar dígito verificador (algoritmo simple)
    if len(rif_limpio) == 10:
        tipo = rif_limpio[0].upper()
        numero = rif_limpio[1:9]
        verificador = int(rif_limpio[9])
        
        # Calcular dígito verificador esperado
        multiplicadores = [3, 2, 7, 6, 5, 4, 3, 2]
        suma = 0
        for i, digito in enumerate(numero):
            suma += int(digito) * multiplicadores[i]
        
        resto = suma % 11
        digito_esperado = 11 - resto if resto > 0 else 0
        
        return verificador == digito_esperado
    
    return True  # Si no tiene 10 caracteres, al menos pasa validación básica

def validar_telefono_venezolano(telefono: str) -> bool:
    """
    Validar número de teléfono venezolano
    Formatos aceptados: 0414-1234567, 04141234567, 212-1234567, +584141234567
    """
    if not telefono:
        return False
    
    # Limpiar espacios y guiones
    telefono_limpio = telefono.replace(' ', '').replace('-', '')
    
    # Patrones para teléfonos venezolanos
    patrones = [
        r'^\+58\d{10}$',           # Internacional: +584141234567
        r'^58\d{10}$',             # Internacional sin +: 584141234567
        r'^0\d{10}$',              # Nacional con 0: 04141234567
        r'^0\d{3}-\d{7}$',         # Con guión: 0414-1234567
        r'^0\d{9}$',               # Teléfonos fijos: 02121234567
        r'^0\d{2}-\d{7}$',         # Fijos con guión: 0212-1234567
    ]
    
    for patron in patrones:
        if re.match(patron, telefono_limpio):
            return True
    
    return False

def formatear_telefono(telefono: str) -> str:
    """
    Formatear teléfono venezolano a formato estándar
    """
    if not telefono:
        return ""
    
    # Limpiar
    limpio = re.sub(r'[^\d\+]', '', telefono)
    
    if limpio.startswith('+58'):
        # Ya está en formato internacional
        return f"+58 {limpio[3:6]} {limpio[6:]}"
    elif limpio.startswith('58'):
        # Sin el +
        return f"+58 {limpio[2:5]} {limpio[5:]}"
    elif limpio.startswith('0'):
        # Nacional
        if len(limpio) == 11:  # Móvil: 04141234567
            return f"{limpio[:4]}-{limpio[4:]}"
        elif len(limpio) == 10:  # Fijo: 0212123456
            return f"{limpio[:3]}-{limpio[3:]}"
    
    return telefono  # Devolver original si no coincide

def validar_fecha_venezolana(fecha_str: str) -> Tuple[bool, Optional[datetime]]:
    """
    Validar fecha en formato venezolano (DD/MM/YYYY)
    """
    try:
        fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
        
        # Verificar que no sea futura (para fechas de nacimiento)
        if fecha > datetime.now():
            return False, None
        
        # Verificar edad mínima (18 años para clientes)
        edad = datetime.now().year - fecha.year
        if edad < 18:
            return False, None
            
        return True, fecha
    except ValueError:
        return False, None

def validar_monto_bs(monto: float) -> bool:
    """
    Validar monto en bolívares (no negativo, máximo 10^15)
    """
    return 0 <= monto <= 10**15

def validar_monto_usd(monto: float) -> bool:
    """
    Validar monto en dólares (no negativo, máximo 10^9)
    """
    return 0 <= monto <= 10**9

def extraer_tipo_identificacion(identificacion: str) -> Optional[str]:
    """
    Extraer tipo de identificación de la cadena
    """
    if not identificacion:
        return None
    
    identificacion = identificacion.upper()
    
    if identificacion.startswith('V') or identificacion.startswith('E'):
        return TipoDocumento.CEDULA.value
    elif identificacion.startswith('J') or identificacion.startswith('G'):
        return TipoDocumento.RIF.value
    elif identificacion.startswith('P'):
        return TipoDocumento.PASAPORTE.value
    
    return None

def get_tipo_persona_from_id(identificacion: str) -> TipoPersona:
    """
    Determinar tipo de persona basado en la identificación
    """
    if not identificacion:
        return TipoPersona.NATURAL
    
    identificacion = identificacion.upper()
    
    if identificacion.startswith('J') or identificacion.startswith('G'):
        return TipoPersona.JURIDICA
    else:
        return TipoPersona.NATURAL