# scripts/validate_styles.py
"""
Script para validar sintaxis CSS en estilos
"""
import re
import sys
from pathlib import Path

def validate_css_syntax(css: str) -> list:
    """Validar sintaxis CSS básica"""
    errors = []
    
    # Dividir por bloques
    blocks = re.findall(r'([^{]+)\{([^}]+)\}', css, re.DOTALL)
    
    for selector, content in blocks:
        selector = selector.strip()
        
        # Validar selector vacío
        if not selector:
            errors.append(f"Selector vacío encontrado")
            continue
        
        # Validar propiedades
        lines = content.strip().split(';')
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                prop, value = line.split(':', 1)
                prop = prop.strip()
                value = value.strip()
                
                # Validar propiedad vacía
                if not prop:
                    errors.append(f"Propiedad vacía en selector: {selector}")
                
                # Validar valor vacío
                if not value:
                    errors.append(f"Valor vacío para propiedad '{prop}' en selector: {selector}")
    
    return errors

def check_file(file_path: Path):
    """Validar un archivo de estilos"""
    print(f"\n🔍 Validando: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar bloques CSS (entre comillas triples o simples)
        css_blocks = []
        
        # Buscar en strings Python
        patterns = [
            r'"""([\s\S]*?)"""',  # Triple comillas dobles
            r"'''([\s\S]*?)'''",  # Triple comillas simples
            r'"([\s\S]*?)"',      # Comillas dobles
            r"'([\s\S]*?)'",      # Comillas simples
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Solo validar si parece CSS (contiene {})
                if '{' in match and '}' in match:
                    css_blocks.append(match)
        
        if not css_blocks:
            print("  ⚠️  No se encontraron bloques CSS")
            return
        
        print(f"  📄 Encontrados {len(css_blocks)} bloque(s) CSS")
        
        for i, css in enumerate(css_blocks, 1):
            errors = validate_css_syntax(css)
            if errors:
                print(f"  ❌ Bloque {i} tiene {len(errors)} error(es):")
                for error in errors[:3]:  # Mostrar solo primeros 3
                    print(f"    • {error}")
                if len(errors) > 3:
                    print(f"    • ... y {len(errors)-3} más")
            else:
                print(f"  ✅ Bloque {i} válido")
    
    except Exception as e:
        print(f"  ❌ Error leyendo archivo: {e}")

def main():
    """Función principal"""
    print("🧪 Validando sintaxis CSS en estilos...")
    
    project_root = Path(__file__).parent.parent
    styles_dir = project_root / "src" / "bvc_gestor" / "ui" / "styles"
    
    if not styles_dir.exists():
        print(f"❌ Directorio no encontrado: {styles_dir}")
        return 1
    
    # Archivos a validar
    files_to_check = [
        styles_dir / "components" / "buttons.py",
        styles_dir / "components" / "tables.py",
        styles_dir / "components" / "cards.py",
        styles_dir / "components" / "sidebar.py",
        styles_dir / "components" / "topbar.py",
        styles_dir / "components" / "statusbar.py",
        styles_dir / "components" / "forms.py",
        styles_dir / "components" / "dialogs.py",
        styles_dir / "__init__.py",  # StyleManager
    ]
    
    for file_path in files_to_check:
        if file_path.exists():
            check_file(file_path)
        else:
            print(f"\n⚠️  Archivo no encontrado: {file_path.name}")
    
    print("\n🎯 RECOMENDACIONES:")
    print("  1. Verificar que todos los selectores CSS tengan contenido")
    print("  2. Asegurar que todas las propiedades tengan valores")
    print("  3. Verificar comillas y corchetes balanceados")
    print("  4. Probar con un validador CSS online")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())