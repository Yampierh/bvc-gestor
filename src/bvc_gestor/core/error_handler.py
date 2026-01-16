# src/bvc_gestor/core/error_handler.py
"""
Manejador global de excepciones para PYME
Evita cierres abruptos de la aplicación
"""
import sys
import traceback
from typing import Optional, Type, Any
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget
from PyQt6.QtCore import QTimer, Qt

from ..utils.logger import logger


class GlobalExceptionHandler:
    """Manejador global de excepciones no capturadas"""
    
    @staticmethod
    def setup_global_exception_handler():
        """Configurar manejador global de excepciones"""
        def excepthook(exctype: Type[BaseException], value: BaseException, traceback_obj: Any):
            """
            Manejador global para excepciones no capturadas
            
            Args:
                exctype: Tipo de excepción
                value: Instancia de la excepción
                traceback_obj: Objeto traceback
            """
            # 1. Loggear el error crítico
            logger.critical("=" * 60)
            logger.critical("EXCEPCIÓN NO CAPTURADA - APLICACIÓN CONTINUARÁ")
            logger.critical("=" * 60)
            logger.critical(f"Tipo: {exctype.__name__}")
            logger.critical(f"Mensaje: {str(value)}")
            logger.critical("Traceback completo:")
            for line in traceback.format_exception(exctype, value, traceback_obj):
                for subline in line.strip().split('\n'):
                    if subline:
                        logger.critical(f"  {subline}")
            
            # 2. Preparar mensaje para usuario
            error_summary = GlobalExceptionHandler._summarize_error(exctype, value)
            
            # 3. Mostrar diálogo de error de forma segura (evitar loops)
            GlobalExceptionHandler._show_error_dialog_safely(error_summary)
            
            # 4. Llamar al manejador original (opcional, para desarrollo)
            # sys.__excepthook__(exctype, value, traceback_obj)
        
        # Instalar el manejador global
        sys.excepthook = excepthook
        logger.info("✅ Manejador global de excepciones configurado")
    
    @staticmethod
    def _summarize_error(exctype: Type[BaseException], value: BaseException) -> str:
        """Resumir el error para mostrar al usuario"""
        error_type = exctype.__name__
        error_msg = str(value)
        
        # Traducciones amigables para errores comunes
        error_translations = {
            'ConnectionError': 'Error de conexión',
            'OperationalError': 'Error en la base de datos',
            'IntegrityError': 'Error de integridad de datos',
            'AttributeError': 'Error interno del programa',
            'ValueError': 'Datos inválidos',
            'TypeError': 'Tipo de dato incorrecto',
            'FileNotFoundError': 'Archivo no encontrado',
            'PermissionError': 'Permiso denegado',
            'TimeoutError': 'Tiempo de espera agotado',
            'KeyError': 'Clave no encontrada',
        }
        
        # Obtener descripción amigable
        friendly_type = error_translations.get(error_type, error_type)
        
        # Limitar longitud del mensaje
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        
        return f"{friendly_type}: {error_msg}"
    
    @staticmethod
    def _show_error_dialog_safely(error_summary: str):
        """
        Mostrar diálogo de error de forma segura
        Usa QTimer para evitar problemas con el event loop
        """
        try:
            # Usar QTimer para mostrar el diálogo de forma asíncrona
            def show_dialog():
                try:
                    # Crear mensaje de error
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Icon.Critical)
                    msg_box.setWindowTitle("Error Inesperado")
                    msg_box.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
                    
                    # Configurar texto
                    msg_box.setText("Se produjo un error inesperado")
                    msg_box.setInformativeText(
                        f"{error_summary}\n\n"
                        "El programa intentará continuar, pero puede tener "
                        "comportamiento inesperado.\n"
                        "Revise los logs para más detalles."
                    )
                    
                    # Solo botón de Aceptar
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    
                    # Mostrar y eliminar después de cerrar
                    msg_box.exec()
                    
                except Exception as e:
                    # Fallback absoluto si incluso el diálogo falla
                    print(f"ERROR CRÍTICO (fallback): {error_summary}")
                    print(f"Error en diálogo: {e}")
            
            # Programar el diálogo para ejecutarse en el event loop
            QTimer.singleShot(0, show_dialog)
            
        except Exception as e:
            # Fallback si todo falla
            print(f"ERROR CRÍTICO (fallback total): {error_summary}")
            print(f"No se pudo mostrar diálogo: {e}")


class SafeExecutor:
    """Ejecutor seguro para operaciones críticas"""
    
    @staticmethod
    def execute_with_retry(operation, max_retries=3, delay=1000):
        """
        Ejecutar operación con reintentos automáticos
        
        Args:
            operation: Función a ejecutar
            max_retries: Número máximo de reintentos
            delay: Retardo entre reintentos en ms
            
        Returns:
            Resultado de la operación o None si falla
        """
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                logger.warning(f"Intento {attempt + 1}/{max_retries} falló: {e}")
                if attempt < max_retries - 1:
                    # Esperar antes de reintentar
                    QTimer.singleShot(delay, lambda: None)
                    QApplication.processEvents()
                else:
                    logger.error(f"Operación falló después de {max_retries} intentos")
                    return None
        return None