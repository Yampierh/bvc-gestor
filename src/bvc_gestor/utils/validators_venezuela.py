# src/bvc_gestor/utils/validators_venezuela.py
"""
Validadores específicos para datos venezolanos
"""
import re
from typing import Optional


def validar_rif(rif_cedula: str) -> bool:
    """
    Validar RIF venezolano (J-12345678-9)
    Formato: [J|G]-[8 dígitos]-[1 dígito verificador]
    """
    if not rif_cedula:
        return False
    
    patron = r'^[JGjg]-?\d{8}-?\d$'
    if not re.match(patron, rif_cedula):
        return False
    
    # Limpiar guiones
    rif_limpio = rif_cedula.replace('-', '')
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

def validar_email(email: str) -> bool:
    """
    Validar formato de correo electrónico
    """
    if not email:
        return False
    
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))

def validar_telefono(telefono: str) -> bool:
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

def validar_nmro_cuenta_bancaria(cuenta: str) -> bool:
    """
    Validar número de cuenta bancaria venezolano (20 dígitos)
    """
    if not cuenta:
        return False
    
    patron = r'^\d{20}$'
    return bool(re.match(patron, cuenta))

def formatear_nmro_cuenta_bancaria(cuenta: str) -> str:
    """
    Formatear número de cuenta bancaria a bloques de 4 dígitos
    Ejemplo: 01234567890123456789 -> 0123 4567 8901 2345 6789
    """
    if not cuenta or len(cuenta) != 20 or not cuenta.isdigit():
        return cuenta
    
    bloques = [cuenta[i:i+4] for i in range(0, 20, 4)]
    return ' '.join(bloques)

