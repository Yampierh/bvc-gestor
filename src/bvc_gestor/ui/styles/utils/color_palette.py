# src/bvc_gestor/ui/styles/utils/color_palette.py
"""
Paleta de colores centralizada para la aplicación BVC-GESTOR
"""
from typing import Dict, Any, List


class ColorPalette:
    """Paleta de colores unificada para BVC-GESTOR"""
    
    # ===== PALETA DE COLORES BÁSICA =====
    _COLORS = {
        # Colores primarios (azules BVC)
        'primary': {
            'light': '#2c5aa0',    # Azul principal BVC
            'dark': '#4dabf7'      # Azul claro para oscuro
        },
        'primary_light': {
            'light': '#e7f3ff',    # Azul muy claro
            'dark': '#1e3a5f'      # Azul oscuro
        },
        'primary_dark': {
            'light': '#1e3a5f',    # Azul oscuro
            'dark': '#a5d8ff'      # Azul claro
        },
        
        # Colores secundarios
        'secondary': {
            'light': '#6c757d',    # Gris
            'dark': '#adb5bd'      # Gris claro
        },
        'success': {
            'light': '#28a745',    # Verde
            'dark': '#34ce57'      # Verde claro
        },
        'danger': {
            'light': '#dc3545',    # Rojo
            'dark': '#ff6b6b'      # Rojo claro
        },
        'warning': {
            'light': '#ffc107',    # Amarillo
            'dark': '#ffd43b'      # Amarillo claro
        },
        'info': {
            'light': '#17a2b8',    # Cyan
            'dark': '#3dd5f3'      # Cyan claro
        },
        
        # Colores para estados financieros
        'profit': {
            'light': '#198754',    # Verde ganancia
            'dark': '#20c997'      # Verde ganancia claro
        },
        'loss': {
            'light': '#dc3545',    # Rojo pérdida
            'dark': '#ff6b6b'      # Rojo pérdida claro
        },
        
        # Colores de fondo y superficie
        'background': {
            'light': '#f8f9fa',    # Fondo gris claro
            'dark': '#1a1d21'      # Fondo negro azulado
        },
        'surface': {
            'light': '#ffffff',    # Superficie blanca
            'dark': '#2d333b'      # Superficie gris oscuro
        },
        'surface_secondary': {
            'light': '#f8f9fa',    # Superficie secundaria
            'dark': '#343a40'      # Superficie secundaria oscura
        },
        
        # Colores de bordes
        'border': {
            'light': '#dee2e6',    # Borde gris claro
            'dark': '#444c56'      # Borde gris oscuro
        },
        'border_light': {
            'light': '#e9ecef',    # Borde muy claro
            'dark': '#495057'      # Borde claro oscuro
        },
        
        # Colores de texto
        'text': {
            'light': '#212529',    # Texto negro
            'dark': '#e9ecef'      # Texto blanco
        },
        'text_secondary': {
            'light': '#6c757d',    # Texto gris
            'dark': '#adb5bd'      # Texto gris claro
        },
        'text_muted': {
            'light': '#adb5bd',    # Texto atenuado
            'dark': '#6c757d'      # Texto atenuado oscuro
        },
        'text_inverse': {
            'light': '#ffffff',    # Texto blanco (para fondos oscuros)
            'dark': '#212529'      # Texto negro (para fondos claros)
        },
        
        # Colores para estados de UI
        'hover': {
            'light': '#e9ecef',    # Hover gris claro
            'dark': '#343a40'      # Hover gris oscuro
        },
        'selected': {
            'light': '#e7f3ff',    # Seleccionado azul claro
            'dark': '#2c5282'      # Seleccionado azul oscuro
        },
        'disabled': {
            'light': '#e9ecef',    # Deshabilitado gris claro
            'dark': '#343a40'      # Deshabilitado gris oscuro
        },
        'focus': {
            'light': '#2c5aa0',    # Borde focus azul
            'dark': '#4dabf7'      # Borde focus azul claro
        }
    }
    
    # ===== MÉTODOS DE ACCESO =====
    
    @classmethod
    def get_color(cls, color_name: str, theme: str = 'light') -> str:
        """
        Obtener color por nombre y tema
        
        Args:
            color_name: Nombre del color (ej: 'primary', 'background')
            theme: 'light' o 'dark'
        
        Returns:
            Color hexadecimal como string
        """
        theme = theme.lower().strip()
        if theme not in ['light', 'dark']:
            theme = 'light'
            print(f"⚠️  Tema '{theme}' no válido. Usando 'light'")
        
        if color_name in cls._COLORS:
            return cls._COLORS[color_name][theme]
        
        # Si el color no existe, usar un color por defecto
        print(f"⚠️  Color '{color_name}' no encontrado. Usando 'primary'")
        return cls._COLORS['primary'][theme]
    
    @classmethod
    def get_palette(cls, theme: str = 'light') -> Dict[str, str]:
        """
        Obtener paleta completa para un tema
        
        Returns:
            Dict con todos los colores del tema
        """
        palette = {}
        for color_name in cls._COLORS:
            palette[color_name] = cls.get_color(color_name, theme)
        return palette
    
    @classmethod
    def get_css_variables(cls, theme: str = 'light') -> str:
        """
        Obtener variables CSS para un tema
        
        Returns:
            String con variables CSS :root
        """
        palette = cls.get_palette(theme)
        
        css_vars = ":root {\n"
        for name, value in palette.items():
            # Convertir snake_case a kebab-case para CSS
            css_name = f"--bvc-{name.replace('_', '-')}"
            css_vars += f"    {css_name}: {value};\n"
        css_vars += "}\n"
        
        return css_vars
    
    @classmethod
    def list_colors(cls, theme: str = 'light') -> List[str]:
        """
        Listar todos los colores disponibles
        
        Returns:
            Lista de nombres de colores
        """
        return sorted(cls._COLORS.keys())
    
    @classmethod
    def validate_palette(cls) -> bool:
        """
        Validar que todos los colores tengan valores para ambos temas
        
        Returns:
            True si la paleta es válida
        """
        errors = []
        for color_name, themes in cls._COLORS.items():
            if 'light' not in themes:
                errors.append(f"Color '{color_name}' no tiene valor para tema 'light'")
            if 'dark' not in themes:
                errors.append(f"Color '{color_name}' no tiene valor para tema 'dark'")
        
        if errors:
            print("❌ Errores en la paleta de colores:")
            for error in errors:
                print(f"   • {error}")
            return False
        
        print("✅ Paleta de colores válida")
        return True


class DynamicColorPalette(ColorPalette):
    """Paleta de colores dinámica que cambia con el tema"""
    
    def __init__(self, initial_theme: str = 'light'):
        self.current_theme = initial_theme
    
    def set_theme(self, theme: str):
        """Cambiar tema actual"""
        if theme not in ['light', 'dark']:
            raise ValueError(f"Tema '{theme}' no válido. Use 'light' o 'dark'")
        self.current_theme = theme
    
    def __getattr__(self, name: str) -> str:
        """Acceder a colores como atributos (ej: palette.primary)"""
        if name in self._COLORS:
            return self.get_color(name, self.current_theme)
        raise AttributeError(f"'DynamicColorPalette' object has no attribute '{name}'")
    
    @property
    def vars(self) -> str:
        """Obtener variables CSS para el tema actual"""
        return self.get_css_variables(self.current_theme)
    
    @property
    def all(self) -> Dict[str, str]:
        """Obtener todos los colores del tema actual"""
        return self.get_palette(self.current_theme)


# Prueba rápida de la paleta
if __name__ == "__main__":
    print("🧪 Probando paleta de colores...")
    
    # Validar paleta
    ColorPalette.validate_palette()
    
    # Mostrar algunos colores
    print(f"\n🎨 Colores para tema 'light':")
    print(f"  • primary: {ColorPalette.get_color('primary', 'light')}")
    print(f"  • background: {ColorPalette.get_color('background', 'light')}")
    print(f"  • text: {ColorPalette.get_color('text', 'light')}")
    
    print(f"\n🎨 Colores para tema 'dark':")
    print(f"  • primary: {ColorPalette.get_color('primary', 'dark')}")
    print(f"  • background: {ColorPalette.get_color('background', 'dark')}")
    print(f"  • text: {ColorPalette.get_color('text', 'dark')}")
    
    # Probar paleta dinámica
    print(f"\n🔄 Probando paleta dinámica:")
    dynamic = DynamicColorPalette('light')
    print(f"  • dynamic.primary: {dynamic.primary}")
    
    dynamic.set_theme('dark')
    print(f"  • dynamic.primary (dark): {dynamic.primary}")
    
    print("\n✅ Paleta de colores funcionando correctamente")