"""
Script para probar el módulo de operaciones desde la carpeta views/
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# IMPORTANTE: Subir 4 niveles desde views/ hasta la raíz del proyecto
# views/ → ui/ → bvc_gestor/ → src/ → raíz
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))

# Añadir la raíz del proyecto al path
sys.path.insert(0, project_root)
print(f"✓ Raíz del proyecto añadida al path: {project_root}")

try:
    # Ahora importamos desde src
    from src.bvc_gestor.ui.views.operaciones_module import OperacionesModule
    print("✓ Módulo de operaciones importado correctamente")
    
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
    print("✓ PyQt6 importado correctamente")
    
except ImportError as e:
    print(f"✗ Error importando: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)


class TestWindow(QMainWindow):
    """Ventana de prueba para el módulo"""
    
    def __init__(self):
        super().__init__()
        
        # Configurar ventana
        self.setWindowTitle("Prueba - Módulo de Operaciones")
        self.setGeometry(100, 100, 1000, 700)
        
        # Crear widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Crear e instanciar el módulo
        print("Instanciando OperacionesModule...")
        self.operaciones_module = OperacionesModule()
        
        # Conectar señal de cambio de título
        self.operaciones_module.titulo_changed.connect(self.on_titulo_changed)
        
        # Agregar módulo al layout
        layout.addWidget(self.operaciones_module)
        
        # Mostrar dashboard inicialmente
        self.operaciones_module.mostrar_dashboard()
        
        print("✓ Módulo de operaciones instanciado correctamente")
    
    def on_titulo_changed(self, nuevo_titulo):
        """Actualiza el título de la ventana"""
        self.setWindowTitle(f"Prueba - Módulo de Operaciones: {nuevo_titulo}")


def main():
    """Función principal de prueba"""
    print("=== Iniciando prueba del módulo de operaciones ===")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Directorio del script: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    
    try:
        # Crear ventana de prueba
        window = TestWindow()
        window.show()
        
        print("\n🎯 Funcionalidades disponibles para probar:")
        print("1. Dashboard de operaciones")
        print("2. Combo de selección de inversores")
        print("3. Botón 'Nueva Compra'")
        print("4. Botón 'Nueva Venta'")
        print("\n⚠️  Nota: Los diálogos requieren conexión a DB")
        print("=============================================\n")
        
        # Ejecutar aplicación
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"✗ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    main()