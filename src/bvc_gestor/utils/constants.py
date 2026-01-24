# src/bvc_gestor/utils/constants.py
"""
Constantes y Enumeraciones del sistema
ACTUALIZADO: Agregados enums para módulo de operaciones
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


# =========================================================
#  ENUMS EXISTENTES
# =========================================================

class TipoInversor(Enum):
    """Tipo de inversor según legislación venezolana"""
    NATURAL = "Natural"
    JURIDICA = "Juridica"


class TipoOrden(Enum):
    """Tipo de orden bursátil"""
    MERCADO = "Mercado"
    LIMITADA = "Limitada"
    COMPRA = 'Compra'
    VENTA = "Venta"


# =========================================================
#  ENUMS ACTUALIZADOS PARA OPERACIONES
# =========================================================

class EstadoOrden(Enum):
    """
    Estados posibles de una orden bursátil
    ACTUALIZADO: Agregado ESPERANDO_FONDOS
    """
    BORRADOR = "Borrador"                           # Creada pero no confirmada
    ESPERANDO_FONDOS = "Esperando Fondos"          # Esperando depósito (NUEVO)
    PENDIENTE = "Pendiente"                         # Enviada al mercado
    PARCIALMENTE_EJECUTADA = "Parcialmente Ejecutada"  # Ejecutada parcialmente
    EJECUTADA = "Ejecutada"                         # Completamente ejecutada
    CANCELADA = "Cancelada"                         # Cancelada por el usuario
    RECHAZADA = "Rechazada"                         # Rechazada por el sistema


class TipoMovimiento(Enum):
    """
    Tipos de movimientos de fondos
    NUEVO: Para gestión de depósitos y retiros
    """
    DEPOSITO = "Deposito"      # Transferencia Banco → Casa de Bolsa
    RETIRO = "Retiro"          # Transferencia Casa de Bolsa → Banco
    COMISION = "Comision"      # Cobro de comisión
    DIVIDENDO = "Dividendo"    # Pago de dividendos
    AJUSTE = "Ajuste"          # Ajuste manual de saldo


class EstadoMovimiento(Enum):
    """
    Estados de un movimiento de fondos
    NUEVO: Ciclo de vida de depósitos/retiros
    """
    PENDIENTE = "Pendiente"        # Registrado pero no ejecutado
    EN_TRANSITO = "En Transito"    # Transferencia en proceso
    COMPLETADO = "Completado"      # Reflejado en cuenta
    RECHAZADO = "Rechazado"        # Transferencia falló
    CANCELADO = "Cancelado"        # Cancelado antes de ejecutar


class TipoRelacionOrdenMovimiento(Enum):
    """
    Tipo de relación entre orden y movimiento
    NUEVO: Para vincular depósitos con órdenes
    """
    DEPOSITO_PARA_COMPRA = "Deposito para Compra"
    RETIRO_POST_VENTA = "Retiro post Venta"


class MercadoActivo(Enum):
    """
    Tipo de mercado del activo
    NUEVO: Clasificación de instrumentos
    """
    ACCIONES = "Acciones"
    BONOS = "Bonos"
    ETF = "ETF"
    OPCIONES = "Opciones"
    FUTUROS = "Futuros"


class FuentePrecio(Enum):
    """
    Fuente de donde proviene el precio
    NUEVO: Para auditoría de precios
    """
    SCRAPING_BVC = "Scraping BVC"
    MANUAL = "Manual"
    API = "API"
    IMPORTACION = "Importacion"


# =========================================================
#  CONSTANTES DE COMISIONES (VALORES POR DEFECTO)
# =========================================================

class ComisionesDefault:
    """
    Valores por defecto de comisiones en Venezuela
    Estos valores pueden ser sobrescritos en la tabla config_comisiones
    """
    CORRETAJE = 0.005      # 0.5% - Comisión del corredor
    BVC = 0.0005           # 0.05% - Comisión de la Bolsa
    CVV = 0.0005           # 0.05% - Comisión de CVV
    IVA = 0.16             # 16% - IVA sobre comisiones


# =========================================================
#  CONSTANTES DE VALIDACIÓN
# =========================================================

class LimitesOperaciones:
    """Límites y validaciones para operaciones"""
    CANTIDAD_MINIMA_ACCIONES = 1
    CANTIDAD_MAXIMA_ACCIONES = 999999999
    PRECIO_MINIMO = 0.01
    PRECIO_MAXIMO = 999999999.99
    MONTO_MINIMO_OPERACION = 100.00  # Bs. mínimo por operación


# =========================================================
#  CONSTANTES DE FORMATO
# =========================================================

class FormatoMoneda:
    """Formatos para mostrar moneda"""
    VES = "Bs. {amount:,.2f}"
    USD = "$ {amount:,.2f}"
    EUR = "€ {amount:,.2f}"


class FormatoPorcentaje:
    """Formatos para mostrar porcentajes"""
    SIMPLE = "{value:.2f}%"
    CON_SIGNO = "{sign}{value:.2f}%"


# =========================================================
#  CONSTANTES DE TIEMPO
# =========================================================

class TiempoLiquidacion:
    """Tiempos de liquidación en días hábiles"""
    T_PLUS_0 = 0  # Mismo día
    T_PLUS_1 = 1  # Día siguiente
    T_PLUS_2 = 2  # Dos días después (estándar BVC)
    T_PLUS_3 = 3  # Tres días después


# =========================================================
#  CONSTANTES DE SISTEMA
# =========================================================

class Monedas:
    """Monedas soportadas"""
    VES = "VES"  # Bolívar venezolano
    USD = "USD"  # Dólar estadounidense
    EUR = "EUR"  # Euro
    
    @classmethod
    def todas(cls):
        return [cls.VES, cls.USD, cls.EUR]
    
    @classmethod
    def principal(cls):
        return cls.VES


class TiposCuenta:
    """Tipos de cuentas bancarias"""
    CORRIENTE = "Corriente"
    AHORRO = "Ahorro"
    NOMINA = "Nomina"
    
    @classmethod
    def todas(cls):
        return [cls.CORRIENTE, cls.AHORRO, cls.NOMINA]


# =========================================================
#  MENSAJES DE ERROR ESTÁNDAR
# =========================================================

class MensajesError:
    """Mensajes de error estándar del sistema"""
    
    # Validaciones generales
    CAMPO_REQUERIDO = "Este campo es requerido"
    VALOR_INVALIDO = "El valor ingresado no es válido"
    FORMATO_INVALIDO = "El formato no es válido"
    
    # Operaciones
    SALDO_INSUFICIENTE = "Saldo insuficiente para realizar la operación"
    POSICION_INSUFICIENTE = "No tiene suficientes acciones para vender"
    ORDEN_NO_ENCONTRADA = "La orden especificada no existe"
    PRECIO_INVALIDO = "El precio debe ser mayor a cero"
    CANTIDAD_INVALIDA = "La cantidad debe ser mayor a cero"
    
    # Movimientos
    MOVIMIENTO_YA_COMPLETADO = "Este movimiento ya fue completado"
    MOVIMIENTO_YA_CANCELADO = "Este movimiento fue cancelado"
    REFERENCIA_DUPLICADA = "Ya existe un movimiento con esta referencia"
    
    # Sistema
    ERROR_BASE_DATOS = "Error al acceder a la base de datos"
    ERROR_CONEXION = "Error de conexión"
    ERROR_PERMISOS = "No tiene permisos para realizar esta acción"


class MensajesExito:
    """Mensajes de éxito estándar"""
    
    ORDEN_CREADA = "Orden creada exitosamente"
    ORDEN_EJECUTADA = "Orden ejecutada exitosamente"
    ORDEN_CANCELADA = "Orden cancelada exitosamente"
    
    DEPOSITO_REGISTRADO = "Depósito registrado exitosamente"
    DEPOSITO_CONFIRMADO = "Depósito confirmado exitosamente"
    RETIRO_REGISTRADO = "Retiro registrado exitosamente"
    
    PRECIO_ACTUALIZADO = "Precio actualizado exitosamente"
    PRECIOS_ACTUALIZADOS = "Precios actualizados exitosamente"
    
    GUARDADO_EXITOSO = "Guardado exitosamente"
    ELIMINADO_EXITOSO = "Eliminado exitosamente"


# =========================================================
#  COLORES PARA UI (COMPLEMENTA styles.qss)
# =========================================================

class ColoresEstado:
    """
    Colores para badges y estados en la UI
    Coinciden con los estilos en styles.qss
    """
    # Estados de orden
    BORRADOR = "#666666"
    ESPERANDO_FONDOS = "#FF9800"  # Naranja
    PENDIENTE = "#2196F3"          # Azul
    EJECUTADA = "#4CAF50"          # Verde
    CANCELADA = "#666666"          # Gris
    RECHAZADA = "#F44336"          # Rojo
    
    # Ganancia/Pérdida
    GANANCIA = "#4CAF50"           # Verde
    PERDIDA = "#F44336"            # Rojo
    NEUTRO = "#888888"             # Gris
    
    # Acento principal
    PRIMARIO = "#FF6B00"           # Naranja (color del sistema)
    SECUNDARIO = "#2196F3"         # Azul


# =========================================================
#  CONFIGURACIÓN DE SCRAPING
# =========================================================

class ConfigScraping:
    """Configuración para web scraping de la BVC"""
    
    # URLs (actualizar con la real de la BVC)
    URL_BVC_BASE = "https://www.bolsadecaracas.com"
    URL_PRECIOS = f"{URL_BVC_BASE}/precios"
    
    # Configuración de requests
    TIMEOUT = 10  # segundos
    MAX_RETRIES = 3
    DELAY_ENTRE_REQUESTS = 2  # segundos (rate limiting)
    
    # Headers
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Configuración de actualización
    INTERVALO_ACTUALIZACION_MINUTOS = 15  # Cada cuántos minutos actualizar
    HORARIO_MERCADO_INICIO = "09:00"
    HORARIO_MERCADO_FIN = "15:00"


# =========================================================
#  RUTAS DE ARCHIVOS
# =========================================================

class RutasArchivos:
    """Rutas estándar para archivos del sistema"""
    
    # Exports
    EXPORTS_PDF = "data/exports/pdf"
    EXPORTS_CSV = "data/exports/csv"
    EXPORTS_EXCEL = "data/exports/excel"
    
    # PDFs de operaciones
    PDF_ORDENES = "data/exports/pdf/operaciones/ordenes"
    PDF_DEPOSITOS = "data/exports/pdf/operaciones/depositos"
    PDF_REPORTES_VENTA = "data/exports/pdf/operaciones/reportes_venta"
    PDF_COMPROBANTES = "data/exports/pdf/comprobantes"
    
    # Logs
    LOGS = "data/logs"
    
    # Imports
    IMPORTS = "data/imports"
    IMPORTS_PLANTILLAS = "data/imports/plantillas"
    
    # Data
    DATA_TICKERS = "data/tickers_bvc.csv"
    DATA_BANCOS = "data/bancos.csv"
    DATA_CASAS_BOLSA = "data/casas_bolsa.csv"


# =========================================================
#  CONFIGURACIÓN DE LOGGING
# =========================================================

class ConfigLogging:
    """Configuración de logging"""
    
    NIVEL_DEFAULT = "INFO"
    FORMATO = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"
    
    # Niveles por módulo
    NIVEL_OPERACIONES = "INFO"
    NIVEL_SCRAPING = "DEBUG"
    NIVEL_BASE_DATOS = "WARNING"


# =========================================================
#  VALIDADORES
# =========================================================

class RegexValidadores:
    """Expresiones regulares para validación"""
    
    # Venezuela
    RIF = r"^[VEJPG]-\d{8,9}-\d$"
    CEDULA = r"^[VE]-\d{7,9}$"
    TELEFONO = r"^(\+58|0)(2|4|5|6)\d{2}-?\d{7}$"
    
    # Financiero
    MONTO = r"^\d+(\.\d{1,2})?$"
    TICKER = r"^[A-Z]{2,5}$"
    
    # General
    EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


# =========================================================
#  CONFIGURACIÓN DE REPORTES
# =========================================================

class ConfigReportes:
    """Configuración para generación de reportes"""
    
    # Formato de fecha en PDFs
    FORMATO_FECHA_PDF = "%d/%m/%Y"
    FORMATO_FECHA_HORA_PDF = "%d/%m/%Y %H:%M:%S"
    
    # Configuración de PDF
    PDF_PAGESIZE = "LETTER"  # o "A4"
    PDF_MARGINS = (20, 20, 20, 20)  # top, right, bottom, left
    
    # Logos y marca de agua
    INCLUIR_LOGO = True
    INCLUIR_MARCA_AGUA = False
    
    # Footer
    TEXTO_FOOTER = "Generado por BVC Gestor"