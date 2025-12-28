# scripts/diagnose_styles.py
"""
Script para diagnosticar problemas de estilos
"""
import sys
from pathlib import Path

def check_widget_objects():
    """Revisar widgets críticos para ObjectName y propiedades"""
    print("🔍 Revisando widgets críticos...")
    
    # Widgets que deben tener ObjectName
    critical_widgets = {
        'src/bvc_gestor/ui/sidebar.py': ['Sidebar'],
        'src/bvc_gestor/ui/topbar.py': ['Topbar'],
        'src/bvc_gestor/ui/statusbar.py': ['StatusBar'],
        'src/bvc_gestor/ui/widgets/dashboard_widget.py': ['DashboardWidget', 'MetricCard'],
    }
    
    for file_path_str, widget_classes in critical_widgets.items():
        file_path = Path(__file__).parent.parent / file_path_str
        if not file_path.exists():
            print(f"  ❌ Archivo no encontrado: {file_path_str}")
            continue
        
        print(f"\n📄 {file_path_str}:")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for widget_class in widget_classes:
            # Buscar la clase
            class_pattern = f'class {widget_class}'
            if class_pattern in content:
                print(f"  ✅ Clase {widget_class} encontrada")
                
                # Buscar setObjectName
                if 'setObjectName(' in content:
                    print(f"    ✓ Tiene setObjectName")
                else:
                    print(f"    ❌ NO tiene setObjectName")
                
                # Buscar setProperty para clases CSS
                if 'setProperty(' in content and '"class"' in content:
                    print(f"    ✓ Tiene setProperty para clases CSS")
                else:
                    print(f"    ⚠️  No tiene setProperty para clases CSS")
            else:
                print(f"  ❌ Clase {widget_class} NO encontrada")

def check_style_manager():
    """Revisar StyleManager"""
    print("\n🔍 Revisando StyleManager...")
    
    sm_path = Path(__file__).parent.parent / "src" / "bvc_gestor" / "ui" / "styles" / "__init__.py"
    
    if sm_path.exists():
        with open(sm_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('StyleManager class', 'class StyleManager' in content),
            ('get_style_manager function', 'def get_style_manager()' in content),
            ('apply_stylesheet method', 'def apply_stylesheet' in content),
            ('Component registration', 'register_component' in content),
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
    else:
        print("  ❌ StyleManager no encontrado")

def main():
    """Función principal"""
    print("🩺 DIAGNÓSTICO DE ESTILOS - BVC-GESTOR")
    print("=" * 50)
    
    check_widget_objects()
    check_style_manager()
    
    print("\n🎯 ACCIONES RECOMENDADAS:")
    print("  1. Asegurar que todos los widgets tengan setObjectName()")
    print("  2. Usar setProperty('class', 'nombre-clase') para clases CSS")
    print("  3. Verificar sintaxis CSS en archivos de estilos")
    print("  4. Probar con estilos mínimos primero")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())