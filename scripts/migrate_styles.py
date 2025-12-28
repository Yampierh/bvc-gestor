# scripts/migrate_styles.py
"""
Script para analizar estilos hardcodeados en el proyecto
"""
import os
import re
from pathlib import Path
import sys

def find_hardcoded_styles(file_path: str):
    """Encontrar estilos hardcodeados en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Intentar con otra codificación si falla
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    
    # Patrones para buscar setStyleSheet
    patterns = [
        r'\.setStyleSheet\s*\(\s*"""([\s\S]*?)"""\s*\)',
        r'\.setStyleSheet\s*\(\s*\'\'\'([\s\S]*?)\'\'\'\s*\)',
        r'\.setStyleSheet\s*\(\s*"([\s\S]*?)"\s*\)',
        r'\.setStyleSheet\s*\(\s*\'([\s\S]*?)\'\s*\)',
        r'setStyleSheet\s*\(\s*"""([\s\S]*?)"""\s*\)',
        r'setStyleSheet\s*\(\s*\'\'\'([\s\S]*?)\'\'\'\s*\)',
        r'setStyleSheet\s*\(\s*"([\s\S]*?)"\s*\)',
        r'setStyleSheet\s*\(\s*\'([\s\S]*?)\'\s*\)',
    ]
    
    styles = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        styles.extend(matches)
    
    # También buscar estilos inline en widgets
    inline_patterns = [
        r'QLabel\s*\([^)]*\)\.setStyleSheet\s*\([^)]+\)',
        r'QPushButton\s*\([^)]*\)\.setStyleSheet\s*\([^)]+\)',
        r'setStyle\s*\([^)]+\)',
    ]
    
    for pattern in inline_patterns:
        matches = re.findall(pattern, content)
        if matches:
            styles.append(f"[INLINE STYLE] {matches[0][:100]}...")
    
    return styles

def analyze_project():
    """Analizar proyecto completo para estilos hardcodeados"""
    project_root = Path(__file__).parent.parent
    
    # Buscar específicamente en src/bvc_gestor/ui/
    ui_dir = project_root / "src" / "bvc_gestor" / "ui"
    
    if not ui_dir.exists():
        print(f"❌ Directorio no encontrado: {ui_dir}")
        return {}
    
    results = {}
    
    # Archivos específicos que sabemos que tienen estilos
    target_files = [
        "main_window.py",
        "sidebar.py", 
        "topbar.py",
        "statusbar.py",
        "widgets/dashboard_widget.py",
        "widgets/clientes_widget.py",
        "widgets/ordenes_widget.py",
        "styles/dark.py",
        "styles/light.py"
    ]
    
    for target in target_files:
        file_path = ui_dir / target
        if file_path.exists():
            styles = find_hardcoded_styles(str(file_path))
            if styles:
                relative_path = file_path.relative_to(project_root)
                results[str(relative_path)] = {
                    'count': len(styles),
                    'styles': styles[:3]  # Mostrar solo primeros 3
                }
    
    # También buscar en otros archivos .py
    for root, dirs, files in os.walk(ui_dir):
        # Excluir __pycache__
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py') and file not in [Path(p).name for p in results.keys()]:
                file_path = Path(root) / file
                styles = find_hardcoded_styles(str(file_path))
                
                if styles:
                    relative_path = file_path.relative_to(project_root)
                    results[str(relative_path)] = {
                        'count': len(styles),
                        'styles': styles[:2]
                    }
    
    return results

def generate_report(results):
    """Generar reporte de estilos hardcodeados"""
    if not results:
        return "✅ No se encontraron estilos hardcodeados"
    
    report = []
    report.append("=" * 80)
    report.append("REPORTE DE ESTILOS HARCODEADOS - BVC-GESTOR")
    report.append("=" * 80)
    report.append("")
    
    total_files = len(results)
    total_styles = sum(data['count'] for data in results.values())
    
    report.append("📊 RESUMEN:")
    report.append(f"  • Archivos con estilos hardcodeados: {total_files}")
    report.append(f"  • Total de bloques de estilo: {total_styles}")
    report.append("")
    
    # Ordenar por cantidad de estilos (descendente)
    sorted_results = sorted(results.items(), key=lambda x: x[1]['count'], reverse=True)
    
    report.append("📋 ARCHIVOS A MIGRAR (por prioridad):")
    for i, (file_path, data) in enumerate(sorted_results, 1):
        report.append(f"\n  {i}. 📄 {file_path}")
        report.append(f"     • Bloques de estilo: {data['count']}")
        
        # Analizar si tiene colores hardcodeados
        colors_used = set()
        for style in data['styles']:
            # Buscar colores hex
            hex_colors = re.findall(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})', str(style))
            colors_used.update(f"#{c}" for c in hex_colors)
            
            # Buscar colores Qt
            qt_colors = re.findall(r'Qt\.GlobalColor\.(\w+)', str(style))
            colors_used.update(f"Qt.{c}" for c in qt_colors)
        
        if colors_used:
            colors_list = list(colors_used)[:5]  # Mostrar hasta 5 colores
            if len(colors_used) > 5:
                colors_list.append(f"... (+{len(colors_used)-5} más)")
            report.append(f"     • Colores usados: {', '.join(colors_list)}")
        
        # Mostrar ejemplo pequeño
        if data['styles']:
            example = str(data['styles'][0])
            if len(example) > 100:
                example = example[:100] + "..."
            report.append(f"     • Ejemplo: {example}")
    
    report.append("")
    report.append("🎯 PLAN DE ACCIÓN RECOMENDADO:")
    report.append("  1. Crear sistema centralizado de estilos (StyleManager)")
    report.append("  2. Definir paleta de colores unificada")
    report.append("  3. Migrar archivos en este orden:")
    
    # Recomendar orden de migración
    priority_order = [
        "sidebar.py", "topbar.py", "main_window.py",  # Interfaz principal
        "dashboard_widget.py",  # Dashboard
        "clientes_widget.py", "ordenes_widget.py",  # Módulos principales
        "statusbar.py",  # Barra estado
        "dark.py", "light.py"  # Archivos de tema existentes
    ]
    
    for i, filename in enumerate(priority_order, 1):
        for file_path in results:
            if filename in file_path:
                report.append(f"     {i}. {file_path}")
    
    report.append("")
    report.append("⚠️  ADVERTENCIA:")
    report.append("  No migrar todo a la vez. Empezar con sidebar.py como prueba.")
    
    return "\n".join(report)

def main():
    """Función principal"""
    print("🔍 Analizando estilos hardcodeados en BVC-GESTOR...")
    print("   (Buscando en src/bvc_gestor/ui/)\n")
    
    results = analyze_project()
    
    report = generate_report(results)
    print(report)
    
    # Guardar reporte
    report_path = Path(__file__).parent / "style_analysis_report.txt"
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Reporte guardado en: {report_path}")
    except Exception as e:
        print(f"\n⚠️  No se pudo guardar reporte: {e}")
    
    return 0 if results else 1

if __name__ == "__main__":
    sys.exit(main())