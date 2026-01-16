# src/bvc_gestor/main.py
"""
Punto de entrada principal de la aplicación PYME
"""
import sys
from pathlib import Path

# Añadir el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont

from .ui.windows.main_window import MainWindow
from .utils.logger import logger
from .database.engine import get_database
from .core.app_state import AppState
from .core.error_handler import GlobalExceptionHandler  # NUEVO IMPORT

class BVCGestorApp:
    """Clase principal de la aplicación"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.app_state = None
        
        # CONFIGURAR MANEJADOR GLOBAL DE EXCEPCIONES - NUEVO
        self.setup_global_exception_handler()
    
    def setup_global_exception_handler(self):
        """Configurar manejador global de excepciones"""
        logger.info("Configurando manejador global de excepciones...")
        GlobalExceptionHandler.setup_global_exception_handler()
    
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
                logger.info("Conexión a base de datos exitosa")
                
                # Crear tablas si no existen
                db_engine.create_tables()
                logger.info("Tablas de base de datos verificadas")
                
                # Preguntar si se deben cargar datos iniciales
                self._preguntar_inicializacion_datos(db_engine)
                
            else:
                logger.error("✗ Error conectando a base de datos")
                
                # MOSTRAR ERROR AMIGABLE EN VEZ DE SALIR - NUEVO
                self._show_database_error()
                return False
            return True
        except Exception as e:
            logger.error(f"✗ Error configurando base de datos: {str(e)}")
            
            # MOSTRAR ERROR AMIGABLE - NUEVO
            self._show_database_error(e)
            return False
    
    def _show_database_error(self, error=None):
        """Mostrar error de base de datos de forma amigable"""
        try:
            error_msg = str(error) if error else "No se puede conectar a la base de datos"
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error de Base de Datos")
            msg_box.setText("No se puede conectar a la base de datos")
            msg_box.setInformativeText(
                f"Error: {error_msg[:150]}\n\n"
                "Posibles causas:\n"
                "• La base de datos no está ejecutándose\n"
                "• Credenciales incorrectas\n"
                "• Problemas de red\n\n"
                "La aplicación puede funcionar en modo limitado."
            )
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Retry | 
                QMessageBox.StandardButton.Ignore
            )
            
            result = msg_box.exec()
            return result == QMessageBox.StandardButton.Retry
            
        except Exception as e:
            logger.error(f"No se pudo mostrar error de BD: {e}")
            return False
    
    def _preguntar_inicializacion_datos(self, db_engine):
        """Preguntar al usuario si desea cargar datos iniciales"""
        try:
            # Verificar si ya hay datos
            session = db_engine.get_session()
            from .database.models_sql import ClienteDB
            
            # Contar clientes existentes
            count_clientes = session.query(ClienteDB).filter_by(estatus=True).count()
            session.close()
            
            if count_clientes > 0:
                logger.info(f"Base de datos ya tiene {count_clientes} clientes")
                return
            
            # Solo preguntar si no hay clientes
            logger.info("Base de datos vacía detectada")
            
            # Si es la primera ejecución, cargar datos automáticamente
            self._cargar_datos_iniciales(db_engine)
            
        except Exception as e:
            logger.error(f"Error verificando datos existentes: {e}")
    
    def _cargar_datos_iniciales(self, db_engine):
        """Cargar datos iniciales automáticamente"""
        try:
            logger.info("Cargando datos iniciales...")
            
            # Importar el inicializador
            from .utils.data_initializer import DataInitializer
            
            # Crear e inicializar
            initializer = DataInitializer()
            initializer.run()
            
            logger.info("✅ Datos iniciales cargados exitosamente")
            
            # Mostrar mensaje en UI (opcional)
            if self.app:
                QMessageBox.information(
                    None,
                    "Datos Iniciales Cargados",
                    "Se han cargado datos de prueba en la base de datos:\n\n"
                    "• 10 Bancos venezolanos\n"
                    "• 8 Casas de Bolsa\n"
                    "• 10 Activos bursátiles\n"
                    "• 10 Clientes de ejemplo\n"
                    "• Configuración básica\n\n"
                    "¡Ya puedes comenzar a usar la aplicación!"
                )
                
        except ImportError:
            logger.warning("Módulo data_initializer no encontrado, saltando carga de datos")
        except Exception as e:
            logger.error(f"Error cargando datos iniciales: {str(e)}")
    
    def setup_app_state(self):
        """Configurar estado de la aplicación con servicios reales"""
        logger.info("Configurando estado de la aplicación...")
        self.app_state = AppState()
        
        # Obtener la sesión de la DB ya configurada
        try:
            db_session = get_database().get_session()
            self.app_state.initialize_services(db_session)
            logger.info("Estado y Servicios (Portfolio/Ordenes) inicializados")
        except Exception as e:
            logger.error(f"Error inicializando servicios: {e}")
            # Inicializar con estado degradado
            self.app_state.initialize_services(None)
            logger.warning("Servicios inicializados en modo degradado")
    
    def setup_application(self):
        """Configurar aplicación PyQt6"""
        logger.info("Configurando aplicación PyQt6...")
        
        # Crear aplicación
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("PYME")
        self.app.setApplicationVersion("1.0")
        self.app.setOrganizationName("PYME")
        
        # Configurar estilo
        self.app.setStyle('Fusion')
        
        # Configurar fuente
        try:
            # Configurar fuente directamente sin QFontDatabase
            app_font = QFont("Sans Serif", 10)
            self.app.setFont(app_font)
            logger.info("Fuente configurada: Sans Serif, 10pt")
            
        except Exception as e:
            logger.warning(f"No se pudo configurar fuente: {e}")
            # Usar fuente por defecto
        
        logger.info("Aplicación PyQt6 configurada")
    
    def create_main_window(self):
        """Crear ventana principal"""
        logger.info("Creando ventana principal...")
        
        try:
            self.main_window = MainWindow(self.app_state)
            self.main_window.setWindowTitle("PYME - Gestor de Inversiones")
            self.main_window.resize(1400, 800)
            logger.info("Ventana principal creada")
        except Exception as e:
            logger.error(f"Error creando ventana principal: {e}")
            raise
    
    def run(self):
        """Ejecutar aplicación"""
        try:
            # Configurar componentes
            self.setup_logging()
            
            if not self.setup_database():
                logger.warning("Base de datos no disponible - modo degradado")
                # NO SALIR - continuar en modo degradado
            
            self.setup_app_state()
            self.setup_application()
            self.create_main_window()
            
            # Mostrar ventana principal
            self.main_window.show()
            logger.info("✅ Aplicación iniciada exitosamente")
            
            # Ejecutar loop principal
            return self.app.exec()
            
        except Exception as e:
            # Este bloque ahora capturará errores durante la inicialización
            logger.error(f"Error crítico durante inicialización: {str(e)}", exc_info=True)
            
            # Mostrar error y salir limpiamente
            QMessageBox.critical(
                None,
                "Error de Inicialización",
                f"No se pudo iniciar la aplicación:\n\n{str(e)[:200]}\n\n"
                "Por favor, verifique la configuración e intente nuevamente."
            )
            return 1

def main():
    """Función principal de entrada"""
    app = BVCGestorApp()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())