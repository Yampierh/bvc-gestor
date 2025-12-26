# src/bvc_gestor/utils/constants.py
"""
Constantes globales de la aplicación para Venezuela
"""
import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src" / "bvc_gestor"

# Rutas de datos
DATABASE_DIR = DATA_DIR / "database"
REPORTS_DIR = DATA_DIR / "reports"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"
CONFIG_DIR = DATA_DIR / "config"

# Asegurar que existen los directorios
for directory in [DATABASE_DIR, REPORTS_DIR, EXPORTS_DIR, BACKUPS_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Constantes de negocio para Venezuela
class Moneda:
    BOLIVAR = "Bs"
    DOLAR = "USD"
    EURO = "EUR"
    
class TipoPersona:
    NATURAL = "Natural"
    JURIDICA = "Jurídica"
    
class TipoDocumento:
    CEDULA = "Cédula"
    RIF = "RIF"
    PASAPORTE = "Pasaporte"
    
class PerfilRiesgo:
    CONSERVADOR = "Conservador"
    MODERADO = "Moderado"
    AGRESIVO = "Agresivo"
    
class EstadoOrden:
    PENDIENTE = "Pendiente"
    EJECUTADA = "Ejecutada"
    CANCELADA = "Cancelada"
    RECHAZADA = "Rechazada"
    
class TipoOrden:
    COMPRA = "Compra"
    VENTA = "Venta"
    
class TipoOperacion:
    MERCADO = "Mercado"
    LIMITADA = "Limitada"
    
# Comisiones BVC (valores de ejemplo)
COMISION_BASE = 0.005  # 0.5%
IVA = 0.16  # 16%
COMISION_TOTAL = COMISION_BASE * (1 + IVA)

# Horario bursátil Venezuela (UTC-4)
HORA_APERTURA = "9:30"
HORA_CIERRE = "14:00"