# src/bvc_gestor/main.py
"""
Punto de entrada principal de la aplicación BVC-GESTOR
"""
import sys
import os
from pathlib import Path

# Añadir el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .ui.windows.main_window import MainWindow
from .utils.logger import logger
from .database.engine import get_database
from .core.app_state import AppState

class BVCGestorApp:
    """Clase principal de la aplicación"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.app_state = None
        
    def setup_logging(self):
        """Configurar sistema de logging"""
        logger.info("=" * 60)
        logger.info("INICIANDO BVC-GESTOR")
        logger.info("=" * 60)
        logger.info("Configurando sistema de logging...")
    
    def setup_database(self):
        """Configurar base de datos"""
        logger.info("Configurando base de datos...")
        try:
            db_engine = get_database()
            if db_engine.test_connection():
                logger.info("✓ Conexión a base de datos exitosa")
                
                # Crear tablas si no existen
                db_engine.create_tables()
                logger.info("✓ Tablas de base de datos verificadas")
            else:
                logger.error("✗ Error conectando a base de datos")
                return False
            return True
        except Exception as e:
            logger.error(f"✗ Error configurando base de datos: {str(e)}")
            return False
    
    def setup_app_state(self):
        """Configurar estado de la aplicación con servicios reales"""
        logger.info("Configurando estado de la aplicación...")
        self.app_state = AppState()
        
        # Obtener la sesión de la DB ya configurada
        db_session = get_database().get_session()
        self.app_state.initialize_services(db_session)
        
        logger.info("✓ Estado y Servicios (Portfolio/Ordenes) inicializados")
    
    def setup_application(self):
        """Configurar aplicación PyQt6"""
        logger.info("Configurando aplicación PyQt6...")
        
        # Crear aplicación
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("BVC-GESTOR")
        self.app.setApplicationVersion("1.0")
        self.app.setOrganizationName("BVC-Gestor")
        
        # Configurar estilo
        self.app.setStyle('Fusion')
        
        # Configurar fuente
        try:
            # Configurar fuente directamente sin QFontDatabase
            app_font = QFont("Arial", 10)
            self.app.setFont(app_font)
            logger.info("✓ Fuente configurada: Arial")
            
        except Exception as e:
            logger.warning(f"No se pudo configurar fuente: {e}")
            # Usar fuente por defecto
        
        """# Configurar atributos de la aplicación
        try:
            # En PyQt6, el atributo se llama diferente
            # PyQt6: Qt.ApplicationAttribute.AA_UseHighDpiPixmaps
            # Pero verifiquemos qué atributos existen realmente
            self.app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        except AttributeError:
            try:
                # Intentar con el nombre de PyQt5 por compatibilidad
                self.app.setAttribute(Qt.AA_UseHighDpiPixmaps)
            except AttributeError:
                logger.warning("No se pudo configurar atributo AA_UseHighDpiPixmaps")
                # Continuar sin este atributo """
        
        logger.info("✓ Aplicación PyQt6 configurada")
    
    def create_main_window(self):
        """Crear ventana principal"""
        logger.info("Creando ventana principal...")
        
        self.main_window = MainWindow(self.app_state)
        self.main_window.setWindowTitle("PYME - Finanzas de Valores")
        self.main_window.resize(1400, 800)
        
        logger.info("✓ Ventana principal creada")
    
    def run(self):
        """Ejecutar aplicación"""
        try:
            # Configurar componentes
            self.setup_logging()
            
            if not self.setup_database():
                logger.error("No se pudo inicializar la base de datos. Saliendo...")
                return 1
            
            self.setup_app_state()
            self.setup_application()
            self.create_main_window()
            
            # Mostrar ventana principal
            self.main_window.show()
            logger.info("✓ Aplicación iniciada exitosamente")
            
            # Ejecutar loop principal
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"Error crítico en la aplicación: {str(e)}", exc_info=True)
            return 1

def main():
    """Función principal de entrada"""
    app = BVCGestorApp()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())