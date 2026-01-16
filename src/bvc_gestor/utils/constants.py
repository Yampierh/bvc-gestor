# src/bvc_gestor/utils/constants.py
"""
Constantes globales de la aplicación para Venezuela
"""
import os
from pathlib import Path
from enum import Enum

# Obtener el directorio base del proyecto (BVC-GESTOR/)
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Rutas de datos (relativas a BASE_DIR)
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src" / "bvc_gestor"

# Rutas de datos específicas
DATABASE_DIR = DATA_DIR / "database"
REPORTS_DIR = DATA_DIR / "reports"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"
CONFIG_DIR = DATA_DIR / "config"

# Asegurar que existen los directorios
def create_directories():
    """Crear directorios necesarios si no existen"""
    directories = [DATABASE_DIR, REPORTS_DIR, EXPORTS_DIR, BACKUPS_DIR, CONFIG_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Crear directorios inmediatamente
create_directories()

# Enums para Venezuela
class Moneda(str, Enum):
    BOLIVAR = "BS"
    DOLAR = "USD"
    EURO = "EUR"

class TipoInversor(str, Enum):
    NATURAL = "Natural"
    JURIDICA = "Jurídica"

class PerfilRiesgo(str, Enum):
    CONSERVADOR = "Conservador"
    MODERADO = "Moderado"
    AGRESIVO = "Agresivo"
    
class EstadoOrden(Enum):
    BORRADOR = "Borrador"                    # Creada pero no confirmada
    ESPERANDO_FONDOS = "Esperando Fondos"    # NUEVO - Esperando depósito
    PENDIENTE = "Pendiente"                  # En el mercado
    PARCIALMENTE_EJECUTADA = "Parcialmente Ejecutada"
    EJECUTADA = "Ejecutada"
    CANCELADA = "Cancelada"
    RECHAZADA = "Rechazada"
    
class TipoOrden(str, Enum):
    COMPRA = "Compra"
    VENTA = "Venta"
    
class TipoOperacion(str, Enum):
    MERCADO = "Mercado"
    LIMITADA = "Limitada"
    

class TipoMovimiento(str, Enum):
    DEPOSITO = "Deposito" # DEPOSITO: Banco → Casa Bolsa
    RETIRO = "Retiro" # RETIRO: Casa Bolsa → Banco
    COMISION = "Comision" # COMISION: Cobro de comisión
    DIVIDENDO = "Dividendo" # DIVIDENDO: Pago de dividendos


class EstadoMovimiento(Enum):
    PENDIENTE = "Pendiente"           # Registrado pero no confirmado
    EN_TRANSITO = "En Tránsito"       # Transferencia en proceso
    COMPLETADO = "Completado"         # Ya reflejado en cuenta
    RECHAZADO = "Rechazado" 

# Comisiones BVC (valores de ejemplo)
COMISION_BASE = 0.005  # 0.5%
IVA = 0.16  # 16%
COMISION_TOTAL = COMISION_BASE * (1 + IVA)

# Horario bursátil Venezuela (UTC-4)
HORA_APERTURA = "9:30"
HORA_CIERRE = "14:00"

# Valores por defecto
DEFAULT_MONEDA = Moneda.BOLIVAR
DEFAULT_PERFIL_RIESGO = PerfilRiesgo.MODERADO
DEFAULT_TIPO_INVERSOR = TipoInversor.NATURAL