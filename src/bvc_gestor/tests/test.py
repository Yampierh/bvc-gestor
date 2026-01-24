# =============================================================================
# SISTEMA DE TESTING STANDALONE PARA MÓDULOS
# =============================================================================

# -----------------------------------------------------------------------------
# 1. TEST DE OPERACIONES MODULE COMPLETO
# Archivo: src/bvc_gestor/tests/test_operaciones_module.py
# -----------------------------------------------------------------------------

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

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


# -----------------------------------------------------------------------------
# 2. TEST DE DASHBOARD SOLO
# Archivo: src/bvc_gestor/tests/test_operaciones_dashboard.py
# -----------------------------------------------------------------------------

from src.bvc_gestor.ui.views.operaciones_dashboard import OperacionesDashboard
from src.bvc_gestor.controllers.operaciones_controller import OperacionesController


def test_dashboard_solo():
    """
    Test del dashboard de operaciones de forma aislada
    """
    print("=" * 60)
    print("TEST: Dashboard de Operaciones (Solo)")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # Cargar estilos
    styles_path = root_dir / "src" / "bvc_gestor" / "ui" / "themes" / "styles.qss"
    if styles_path.exists():
        with open(styles_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    
    # Crear controller
    controller = OperacionesController()
    print(f"✓ Controller creado: {type(controller).__name__}")
    
    # Crear dashboard CON controller
    dashboard = OperacionesDashboard(controller=controller)
    
    # Conectar señales para debug
    dashboard.nueva_compra_clicked.connect(
        lambda: print("📝 Señal: nueva_compra_clicked")
    )
    dashboard.nueva_venta_clicked.connect(
        lambda: print("💰 Señal: nueva_venta_clicked")
    )
    dashboard.inversor_changed.connect(
        lambda id: print(f"👤 Señal: inversor_changed -> ID: {id}")
    )
    
    # Ventana
    window = QMainWindow()
    window.setWindowTitle("Test - Dashboard de Operaciones")
    window.setGeometry(100, 100, 1400, 900)
    window.setCentralWidget(dashboard)
    
    print("✓ Dashboard creado y configurado")
    print("\nPrueba interacciones:")
    print("  - Seleccionar un inversor en el combo")
    print("  - Hacer clic en 'Nueva Compra'")
    print("  - Hacer clic en 'Nueva Venta'")
    
    window.show()
    sys.exit(app.exec())


# -----------------------------------------------------------------------------
# 3. TEST DE DIALOGS
# Archivo: src/bvc_gestor/tests/test_dialogs.py
# -----------------------------------------------------------------------------

from src.bvc_gestor.ui.dialogs.nueva_compra_dialog import NuevaCompraDialog
from src.bvc_gestor.ui.dialogs.nueva_venta_dialog import NuevaVentaDialog


def test_dialog_compra():
    """Test del dialog de nueva compra"""
    print("=" * 60)
    print("TEST: Dialog de Nueva Compra")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # Cargar estilos
    styles_path = root_dir / "src" / "bvc_gestor" / "ui" / "themes" / "styles.qss"
    if styles_path.exists():
        with open(styles_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    
    # Crear dialog con un inversor de prueba
    dialog = NuevaCompraDialog(inversor_id=1)
    
    # Conectar señales
    dialog.orden_creada.connect(
        lambda orden_id: print(f"✓ Orden creada: ID {orden_id}")
    )
    
    print("✓ Dialog creado")
    print("\nPrueba el wizard de 3 pasos:")
    print("  Paso 1: Seleccionar cuentas")
    print("  Paso 2: Ingresar detalles de operación")
    print("  Paso 3: Confirmar y validar saldo")
    
    result = dialog.exec()
    
    if result:
        print("\n✓ Dialog aceptado")
    else:
        print("\n⚠ Dialog cancelado")


def test_dialog_venta():
    """Test del dialog de nueva venta"""
    print("=" * 60)
    print("TEST: Dialog de Nueva Venta")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # Cargar estilos
    styles_path = root_dir / "src" / "bvc_gestor" / "ui" / "themes" / "styles.qss"
    if styles_path.exists():
        with open(styles_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    
    dialog = NuevaVentaDialog(inversor_id=1)
    
    dialog.orden_creada.connect(
        lambda orden_id: print(f"✓ Orden de venta creada: ID {orden_id}")
    )
    
    print("✓ Dialog de venta creado")
    print("\nSelecciona una posición del portafolio y completa el formulario")
    
    result = dialog.exec()
    
    if result:
        print("\n✓ Dialog aceptado")
    else:
        print("\n⚠ Dialog cancelado")


# -----------------------------------------------------------------------------
# 4. TEST DE CONTROLLER SOLO
# Archivo: src/bvc_gestor/tests/test_operaciones_controller.py
# -----------------------------------------------------------------------------

def test_controller():
    """
    Test del controller sin UI
    Prueba métodos de consulta a la base de datos
    """
    print("=" * 60)
    print("TEST: OperacionesController (Sin UI)")
    print("=" * 60)
    
    from src.bvc_gestor.controllers.operaciones_controller import OperacionesController
    
    # Crear controller
    controller = OperacionesController()
    print("✓ Controller creado\n")
    
    # Test 1: Obtener inversores
    print("Test 1: Obtener inversores activos")
    inversores = controller.obtener_inversores_activos()
    print(f"  ✓ Encontrados {len(inversores)} inversores")
    for inv in inversores[:3]:  # Mostrar primeros 3
        print(f"    - {inv['nombre']} ({inv['rif_cedula']})")
    
    if not inversores:
        print("  ⚠ No hay inversores en la BD")
        return
    
    # Test 2: Obtener cuentas del primer inversor
    print(f"\nTest 2: Obtener cuentas del inversor ID {inversores[0]['id']}")
    cuentas_b = controller.obtener_cuentas_bursatiles_cliente(inversores[0]['id'])
    cuentas_ban = controller.obtener_cuentas_bancarias_cliente(inversores[0]['id'])
    print(f"  ✓ Cuentas bursátiles: {len(cuentas_b)}")
    print(f"  ✓ Cuentas bancarias: {len(cuentas_ban)}")
    
    # Test 3: Obtener operaciones recientes
    print(f"\nTest 3: Obtener operaciones recientes")
    operaciones = controller.obtener_operaciones_recientes(
        cliente_id=inversores[0]['id'],
        limite=5
    )
    print(f"  ✓ Operaciones encontradas: {len(operaciones)}")
    for op in operaciones:
        print(f"    - {op['fecha']} | {op['tipo']} | {op['ticker']} | {op['estado']}")
    
    # Test 4: Obtener métricas
    print(f"\nTest 4: Obtener métricas del dashboard")
    metricas = controller.obtener_metricas_dashboard(inversores[0]['id'])
    if metricas:
        print(f"  ✓ Valor portafolio: Bs. {metricas.get('valor_portafolio', 0):,.2f}")
        print(f"  ✓ Operaciones pendientes: {metricas.get('operaciones_pendientes', 0)}")
        print(f"  ✓ G/P: Bs. {metricas.get('ganancia_perdida', 0):,.2f}")
    
    print("\n" + "=" * 60)
    print("Tests del controller completados")
    print("=" * 60)


# -----------------------------------------------------------------------------
# 5. TEST COMPARATIVO (Clientes vs Operaciones)
# Archivo: src/bvc_gestor/tests/test_comparacion_modulos.py
# -----------------------------------------------------------------------------

def test_comparacion_modulos():
    """
    Compara la estructura de ClientesModule vs OperacionesModule
    """
    print("=" * 60)
    print("TEST: Comparación de Módulos")
    print("=" * 60)
    
    from src.bvc_gestor.ui.views.clientes_module import ClientesModule
    from src.bvc_gestor.ui.views.operaciones_module import OperacionesModule
    
    app = QApplication(sys.argv)
    
    # Crear ambos módulos
    clientes = ClientesModule()
    operaciones = OperacionesModule()
    
    print("\n📊 COMPARACIÓN DE ESTRUCTURA:\n")
    
    # Tipo de clase base
    print(f"ClientesModule hereda de: {type(clientes).__bases__[0].__name__}")
    print(f"OperacionesModule hereda de: {type(operaciones).__bases__[0].__name__}")
    
    # Número de vistas
    print(f"\nClientesModule - Vistas: {clientes.count()}")
    print(f"OperacionesModule - Vistas: {operaciones.count()}")
    
    # Controller
    print(f"\nClientesModule tiene controller: {hasattr(clientes, 'controller')}")
    print(f"OperacionesModule tiene controller: {hasattr(operaciones, 'controller')}")
    
    # Atributos
    print(f"\nAtributos de ClientesModule:")
    for attr in dir(clientes):
        if not attr.startswith('_') and 'view' in attr.lower():
            print(f"  - {attr}")
    
    print(f"\nAtributos de OperacionesModule:")
    for attr in dir(operaciones):
        if not attr.startswith('_') and 'view' in attr.lower():
            print(f"  - {attr}")
    
    print("\n" + "=" * 60)


# -----------------------------------------------------------------------------
# 6. SCRIPT MAESTRO UNIFICADO
# Archivo: src/bvc_gestor/tests/run_tests.py
# -----------------------------------------------------------------------------

def menu_tests():
    """
    Menú interactivo para ejecutar diferentes tests
    """
    print("\n" + "=" * 60)
    print("SISTEMA DE TESTING - BVC GESTOR")
    print("=" * 60)
    print("\nSelecciona el test a ejecutar:\n")
    print("1. Módulo de Operaciones Completo")
    print("2. Dashboard de Operaciones (solo)")
    print("3. Dialog de Nueva Compra")
    print("4. Dialog de Nueva Venta")
    print("5. Controller (sin UI)")
    print("6. Comparación de Módulos")
    print("7. Todos los tests (secuencial)")
    print("0. Salir\n")
    
    opcion = input("Opción: ").strip()
    
    if opcion == "1":
        test_operaciones_module()
    elif opcion == "2":
        test_dashboard_solo()
    elif opcion == "3":
        test_dialog_compra()
    elif opcion == "4":
        test_dialog_venta()
    elif opcion == "5":
        test_controller()
    elif opcion == "6":
        test_comparacion_modulos()
    elif opcion == "7":
        print("\nEjecutando todos los tests...\n")
        test_controller()
        input("\nPresiona Enter para continuar con el siguiente test...")
        test_comparacion_modulos()
        input("\nPresiona Enter para continuar con el siguiente test...")
        test_dashboard_solo()
    elif opcion == "0":
        print("Saliendo...")
        return
    else:
        print("Opción inválida")
        menu_tests()


if __name__ == "__main__":
    # Ejecutar menú
    menu_tests()


# -----------------------------------------------------------------------------
# 7. SCRIPT RÁPIDO DE LÍNEA DE COMANDOS
# Archivo: test_quick.py (en la raíz del proyecto)
# -----------------------------------------------------------------------------

"""
Script rápido para testing desde línea de comandos

Uso:
    python test_quick.py module      # Test módulo completo
    python test_quick.py dashboard   # Test solo dashboard
    python test_quick.py compra      # Test dialog compra
    python test_quick.py venta       # Test dialog venta
    python test_quick.py controller  # Test controller
"""

import sys
from pathlib import Path

# Agregar src al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_quick.py [module|dashboard|compra|venta|controller]")
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    # Importar el test correspondiente
    from src.bvc_gestor.tests.run_tests import (
        test_operaciones_module,
        test_dashboard_solo,
        test_dialog_compra,
        test_dialog_venta,
        test_controller
    )
    
    tests = {
        'module': test_operaciones_module,
        'dashboard': test_dashboard_solo,
        'compra': test_dialog_compra,
        'venta': test_dialog_venta,
        'controller': test_controller,
    }
    
    if comando in tests:
        tests[comando]()
    else:
        print(f"Comando '{comando}' no reconocido")
        print("Comandos disponibles: module, dashboard, compra, venta, controller")