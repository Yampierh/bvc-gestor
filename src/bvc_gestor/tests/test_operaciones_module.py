# -----------------------------------------------------------------------------
# 1. TEST DE OPERACIONES MODULE COMPLETO
# Archivo: src/bvc_gestor/tests/test_operaciones_module.py
# -----------------------------------------------------------------------------

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from src.bvc_gestor.ui.views.operaciones_module import OperacionesModule


def test_operaciones_module():
    """
    Test standalone del módulo completo de operaciones
    """
    print("=" * 60)
    print("TEST: Módulo de Operaciones Completo")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # Cargar estilos
    styles_path = root_dir / "src" / "bvc_gestor" / "ui" / "themes" / "styles.qss"
    if styles_path.exists():
        with open(styles_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
        print("✓ Estilos cargados")
    else:
        print("⚠ Archivo de estilos no encontrado")
    
    # Crear ventana de prueba
    window = QMainWindow()
    window.setWindowTitle("Test - Módulo de Operaciones")
    window.setGeometry(100, 100, 1400, 900)
    
    # Crear módulo
    operaciones_module = OperacionesModule()
    
    # Establecer como widget central
    window.setCentralWidget(operaciones_module)
    
    # Info del módulo
    print(f"✓ Módulo creado: {type(operaciones_module).__name__}")
    print(f"✓ Número de vistas en el stack: {operaciones_module.count()}")
    print(f"✓ Vista actual: index {operaciones_module.currentIndex()}")
    
    if hasattr(operaciones_module, 'controller'):
        print(f"✓ Controller: {type(operaciones_module.controller).__name__}")
    else:
        print("⚠ Controller no encontrado")
    
    window.show()
    
    print("\n" + "=" * 60)
    print("Ventana de prueba abierta")
    print("=" * 60)
    
    sys.exit(app.exec())