# run.py
"""
Script de ejecución principal para PYME
"""
import sys
from pathlib import Path

# Añadir el directorio src al path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def check_dependencies():
    """Verificar dependencias necesarias"""
    try:
        from PyQt6.QtCore import QT_VERSION_STR
        print(f"Qt version: {QT_VERSION_STR}")
        
        import sqlalchemy
        print(f"SQLAlchemy version: {sqlalchemy.__version__}")
        
        import pandas
        print(f"Pandas version: {pandas.__version__}")
        
        return True
    except ImportError as e:
        print(f"Dependencia faltante: {e}")
        print("\nInstale las dependencias con:")
        print("pip install -r requirements.txt")
        return False

def setup_environment():
    """Configurar entorno de la aplicación"""
    # Crear directorios necesarios
    directories = [
        "data/database",
        "data/reports",
        "data/exports",
        "data/backups",
        "data/config",
        "data/logs"
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Verificar archivo .env
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        env_example = Path(__file__).parent / ".env.example"
        if env_example.exists():
            print(f"⚠  Archivo .env no encontrado. Copiando desde .env.example")
            import shutil
            shutil.copy(env_example, env_file)
            print(f" Archivo .env creado. Por favor, configúrelo.")
        else:
            print("⚠  Archivo .env.example no encontrado")

def main():
    """Función principal"""
    print("=" * 60)
    print("PYME - Gestor para compra-venta en la Bolsa de Valores de Caracas")
    print("=" * 60)
    
    # Configurar entorno
    setup_environment()
    
    # Verificar dependencias
    if not check_dependencies():
        return 1
    
    print("\nIniciando aplicación")
    
    try:
        from bvc_gestor.main import main as app_main
        return app_main()
    except ImportError as e:
        print(f"Error importando módulos: {e}")
        print("\nAsegúrese de que la estructura del proyecto sea correcta.")
        return 1
    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())