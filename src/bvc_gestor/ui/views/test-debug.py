"""
Script de prueba con mejor manejo de errores para debug
"""

import sys
import os
import logging
import traceback

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Subir hasta la raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

print("=" * 60)
print("DEBUG - Iniciando prueba del dashboard")
print("=" * 60)

try:
    # Importar primero solo lo básico para debug
    print("1. Importando PyQt6...")
    from PyQt6.QtWidgets import QApplication
    print("   ✓ PyQt6 importado")
    
    print("\n2. Intentando importar operaciones_dashboard directamente...")
    from src.bvc_gestor.ui.views.operaciones_dashboard import OperacionesDashboard
    
    # Probar solo el dashboard primero
    app = QApplication(sys.argv)
    
    print("\n3. Creando instancia de OperacionesDashboard...")
    try:
        dashboard = OperacionesDashboard()
        print(f"   ✓ Dashboard creado: {dashboard}")
        
        # Verificar si combo_inversor existe
        if hasattr(dashboard, 'combo_inversor'):
            print(f"   ✓ combo_inversor existe: {dashboard.combo_inversor}")
            if dashboard.combo_inversor:
                print("   ✓ combo_inversor NO es None")
            else:
                print("   ✗ combo_inversor es None!")
        else:
            print("   ✗ combo_inversor NO existe como atributo!")
            
        # Mostrar dashboard
        dashboard.show()
        
        print("\n4. Dashboard mostrado correctamente")
        print("\n✅ PRUEBA EXITOSA - El problema está en otra parte")
        
    except Exception as e:
        print(f"\n✗ Error al crear dashboard: {e}")
        traceback.print_exc()
    
    # Mantener la app abierta
    sys.exit(app.exec())
    
except ImportError as e:
    print(f"\n✗ Error de importación: {e}")
    traceback.print_exc()
    sys.exit(1)