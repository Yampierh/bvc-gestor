# scripts/test_style_manager.py
"""
Script para probar el sistema de estilos
"""
import sys
from pathlib import Path

# Añadir el directorio src al path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

def test_color_palette():
    """Probar la paleta de colores"""
    print("🧪 Probando ColorPalette...")
    
    try:
        from bvc_gestor.ui.styles.utils.color_palette import ColorPalette, DynamicColorPalette
        
        # Prueba básica
        primary_light = ColorPalette.get_color('primary', 'light')
        primary_dark = ColorPalette.get_color('primary', 'dark')
        
        print(f"✅ ColorPalette funcionando:")
        print(f"   • primary (light): {primary_light}")
        print(f"   • primary (dark): {primary_dark}")
        
        # Prueba paleta dinámica
        dynamic = DynamicColorPalette('light')
        print(f"   • dynamic.primary (light): {dynamic.primary}")
        
        dynamic.set_theme('dark')
        print(f"   • dynamic.primary (dark): {dynamic.primary}")
        
        # Listar colores
        colors = ColorPalette.list_colors()
        print(f"   • Colores disponibles: {len(colors)}")
        
        # Validar paleta
        if ColorPalette.validate_palette():
            print("✅ Paleta válida")
        else:
            print("❌ Problemas con la paleta")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en ColorPalette: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_style_manager():
    """Probar el StyleManager"""
    print("\n🧪 Probando StyleManager...")
    
    try:
        from bvc_gestor.ui.styles import get_style_manager
        
        # Obtener instancia
        sm = get_style_manager()
        
        print(f"✅ StyleManager obtenido:")
        print(f"   • Tema actual: {sm.current_theme}")
        print(f"   • Modo oscuro: {sm.is_dark}")
        
        # Obtener algunos colores
        colors_to_check = ['primary', 'background', 'text', 'border']
        for color in colors_to_check:
            value = sm.get_color(color)
            print(f"   • {color}: {value}")
        
        # Cambiar tema
        print(f"\n🔄 Cambiando tema...")
        sm.set_theme('dark')
        print(f"   • Tema después de cambiar: {sm.current_theme}")
        print(f"   • primary (dark): {sm.get_color('primary')}")
        
        # Volver a claro
        sm.set_theme('light')
        print(f"   • Tema restaurado: {sm.current_theme}")
        
        # Obtener estilos
        print(f"\n📄 Obteniendo estilos...")
        stylesheet = sm.get_stylesheet()
        print(f"   • Longitud del stylesheet: {len(stylesheet)} caracteres")
        
        # Verificar componentes incluidos
        lines = stylesheet.split('\n')
        button_styles = sum(1 for line in lines if 'QPushButton' in line)
        table_styles = sum(1 for line in lines if 'QTableView' in line or 'QTableWidget' in line)
        
        print(f"   • Estilos de botones: {button_styles} líneas")
        print(f"   • Estilos de tablas: {table_styles} líneas")
        
        # Prueba de componentes específicos
        print(f"\n🔧 Probando componentes específicos...")
        buttons_only = sm.get_stylesheet(components=['buttons'])
        print(f"   • Solo botones: {len(buttons_only)} caracteres")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en StyleManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_components():
    """Probar componentes de estilos"""
    print("\n🧪 Probando componentes...")
    
    try:
        from bvc_gestor.ui.styles.components.buttons import ButtonStyles
        from bvc_gestor.ui.styles.components.tables import TableStyles
        from bvc_gestor.ui.styles.components.sidebar import SidebarStyles
        from bvc_gestor.ui.styles.components.topbar import TopbarStyles
        
        components = {
            'Botones': ButtonStyles,
            'Tablas': TableStyles,
            'Sidebar': SidebarStyles,
            'Topbar': TopbarStyles
        }
        
        for name, component in components.items():
            try:
                styles_light = component.get_styles('light')
                styles_dark = component.get_styles('dark')
                
                print(f"✅ {name}:")
                print(f"   • Light: {len(styles_light)} caracteres")
                print(f"   • Dark: {len(styles_dark)} caracteres")
                
                # Verificar que no estén vacíos
                if len(styles_light.strip()) < 10:
                    print(f"   ⚠️  Estilos light muy cortos!")
                if len(styles_dark.strip()) < 10:
                    print(f"   ⚠️  Estilos dark muy cortos!")
                    
            except Exception as e:
                print(f"❌ Error en {name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando componentes: {e}")
        return False

def test_themes():
    """Probar temas completos"""
    print("\n🧪 Probando temas completos...")
    
    try:
        from bvc_gestor.ui.styles.themes.light_theme import LightTheme
        from bvc_gestor.ui.styles.themes.dark_theme import DarkTheme
        
        # Probar tema claro
        light_stylesheet = LightTheme.get_stylesheet()
        print(f"✅ Tema claro:")
        print(f"   • Longitud: {len(light_stylesheet)} caracteres")
        print(f"   • Variables CSS: {'--bvc-primary:' in light_stylesheet}")
        print(f"   • Contiene botones: {'QPushButton' in light_stylesheet}")
        print(f"   • Contiene tablas: {'QTableView' in light_stylesheet}")
        
        # Probar tema oscuro
        dark_stylesheet = DarkTheme.get_stylesheet()
        print(f"\n✅ Tema oscuro:")
        print(f"   • Longitud: {len(dark_stylesheet)} caracteres")
        print(f"   • Variables CSS: {'--bvc-primary:' in dark_stylesheet}")
        
        # Verificar diferencias
        light_lines = light_stylesheet.split('\n')
        dark_lines = dark_stylesheet.split('\n')
        
        print(f"\n📊 Comparación:")
        print(f"   • Líneas en light: {len(light_lines)}")
        print(f"   • Líneas en dark: {len(dark_lines)}")
        
        # Verificar que los temas sean diferentes
        if light_stylesheet != dark_stylesheet:
            print(f"   ✅ Los temas son diferentes")
        else:
            print(f"   ⚠️  Los temas son idénticos (posible error)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en temas: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Probar integración con PyQt6"""
    print("\n🧪 Probando integración con PyQt6...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
        from PyQt6.QtCore import Qt
        
        # Crear aplicación mínima
        app = QApplication([])
        
        # Crear ventana de prueba
        window = QWidget()
        window.setWindowTitle("Prueba de Estilos BVC-GESTOR")
        window.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Botones con diferentes clases CSS
        btn1 = QPushButton("Botón Primario")
        btn1.setProperty("class", "primary")
        
        btn2 = QPushButton("Botón Secundario")
        btn2.setProperty("class", "secondary")
        
        btn3 = QPushButton("Botón Peligro")
        btn3.setProperty("class", "danger")
        
        btn4 = QPushButton("Botón Outline")
        btn4.setProperty("class", "outline")
        
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addWidget(btn4)
        
        window.setLayout(layout)
        
        # Aplicar estilos usando StyleManager
        from bvc_gestor.ui.styles import get_style_manager
        sm = get_style_manager()
        
        # Aplicar estilos
        sm.apply_stylesheet(window)
        
        print(f"✅ Integración con PyQt6:")
        print(f"   • Aplicación creada")
        print(f"   • Ventana con 4 botones")
        print(f"   • Estilos aplicados")
        
        # No mostramos la ventana, solo verificamos que funcione
        window.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de prueba"""
    print("=" * 60)
    print("PRUEBA DEL SISTEMA DE ESTILOS BVC-GESTOR")
    print("=" * 60)
    
    tests = [
        ("Paleta de colores", test_color_palette),
        ("StyleManager", test_style_manager),
        ("Componentes", test_components),
        ("Temas completos", test_themes),
        ("Integración PyQt6", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name.upper()}")
        print("-" * 40)
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Total: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("\n✨ ¡SISTEMA DE ESTILOS FUNCIONANDO CORRECTAMENTE!")
    else:
        print("\n⚠️  Hay problemas que necesitan atención")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())