# src/bvc_gestor/ui/styles/__init__.py
"""
Sistema centralizado de estilos para BVC-GESTOR
"""
import logging
from typing import Dict, Optional, List, Any
import os

from .utils.color_palette import DynamicColorPalette

# Importar todos los componentes de estilo
from .components.buttons import ButtonStyles
from .components.tables import TableStyles
from .components.cards import CardStyles
from .components.forms import FormStyles
from .components.dialogs import DialogStyles
from .components.sidebar import SidebarStyles
from .components.topbar import TopbarStyles
from .components.statusbar import StatusbarStyles
#from .components.metrics import MetricsStyles

# Importar temas completos
from .themes.light_theme import LightTheme
from .themes.dark_theme import DarkTheme

from ...utils.logger import logger


class StyleManager:
    """
    Manager central de estilos de la aplicación
    
    Patrón Singleton para acceso global
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Evitar múltiples inicializaciones
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.current_theme = 'light'
            self.color_palette = DynamicColorPalette(self.current_theme)
            self.stylesheet_cache = {}
            self._component_styles = {}
            self._themes = {}
            
            # Registrar todos los componentes de estilo
            self._register_all_components()
            
            # Registrar todos los temas
            self._register_all_themes()
            
            logger.info(f"✅ StyleManager inicializado (tema: {self.current_theme})")
    
    def _register_all_components(self):
        """Registrar todos los componentes de estilos disponibles"""
        components = {
            'buttons': ButtonStyles,
            'tables': TableStyles,
            'cards': CardStyles,
            'forms': FormStyles,
            'dialogs': DialogStyles,
            'sidebar': SidebarStyles,
            'topbar': TopbarStyles,
            'statusbar': StatusbarStyles,
            #'metrics': MetricsStyles
        }
        
        for name, component in components.items():
            self.register_component(name, component)
        
        logger.info(f"📦 Componentes registrados: {', '.join(components.keys())}")
    
    def _register_all_themes(self):
        """Registrar todos los temas disponibles"""
        self._themes = {
            'light': LightTheme,
            'dark': DarkTheme
        }
        logger.info(f"🎨 Temas registrados: {', '.join(self._themes.keys())}")
    
    def register_component(self, name: str, component_class):
        """Registrar un componente de estilos"""
        self._component_styles[name] = component_class
        logger.debug(f"Componente de estilo registrado: {name}")
    
    def register_theme(self, name: str, theme_class):
        """Registrar un nuevo tema"""
        self._themes[name] = theme_class
        logger.info(f"Nuevo tema registrado: {name}")
    
    def set_theme(self, theme: str):
        """
        Cambiar tema de la aplicación
        
        Args:
            theme: 'light' o 'dark' (u otros si están registrados)
        """
        theme = theme.lower().strip()
        
        if theme not in self._themes:
            logger.warning(f"Tema '{theme}' no registrado. Temas disponibles: {', '.join(self._themes.keys())}")
            return
        
        if theme == self.current_theme:
            return  # No hacer nada si ya está en ese tema
        
        old_theme = self.current_theme
        self.current_theme = theme
        self.color_palette.set_theme(theme)
        
        # Limpiar caché de estilos
        self.stylesheet_cache.clear()
        
        logger.info(f"🎨 Tema cambiado: {old_theme} → {theme}")
    
    def get_stylesheet(self, theme: Optional[str] = None, 
                    components: Optional[List[str]] = None,
                    use_theme_file: bool = True) -> str:
        """
        Obtener hoja de estilos completa o parcial
        
        Args:
            theme: Tema a usar (None = tema actual)
            components: Lista de componentes a incluir (None = todos)
            use_theme_file: Usar archivo de tema completo (True) o construir dinámicamente (False)
        
        Returns:
            String CSS con los estilos
        """
        if theme is None:
            theme = self.current_theme
        
        # Usar caché si está disponible
        cache_key = f"{theme}:{','.join(components) if components else 'all'}:{use_theme_file}"
        if cache_key in self.stylesheet_cache:
            return self.stylesheet_cache[cache_key]
        
        if use_theme_file and theme in self._themes:
            # Usar archivo de tema completo
            css = self._themes[theme].get_stylesheet()
        else:
            # Construir dinámicamente
            css = self._build_stylesheet(theme, components)
        
        # Cachear resultado
        self.stylesheet_cache[cache_key] = css
        
        return css
    
    def _build_stylesheet(self, theme: str, components: Optional[List[str]] = None) -> str:
        """Construir hoja de estilos dinámicamente"""
        # Variables CSS del tema
        css = self.color_palette.vars + "\n"
        
        # Estilos base (siempre incluidos)
        css += self._get_base_styles(theme) + "\n"
        
        # Estilos de componentes
        if components:
            # Solo componentes específicos
            for comp_name in components:
                if comp_name in self._component_styles:
                    css += self._component_styles[comp_name].get_styles(theme) + "\n"
        else:
            # Todos los componentes
            for comp_name, comp_class in self._component_styles.items():
                css += comp_class.get_styles(theme) + "\n"
        
        return css
    
    def _get_base_styles(self, theme: str) -> str:
        """Obtener estilos base comunes a toda la aplicación"""
        colors = self.color_palette.all
        
        return f"""
        /* ===== ESTILOS BASE BVC-GESTOR ===== */
        
        /* Aplicación principal */
        QMainWindow {{
            background-color: {colors['background']};
        }}
        
        /* Widgets generales */
        QWidget {{
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 14px;
            color: {colors['text']};
        }}
        
        /* Scroll Area */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        
        /* Labels */
        QLabel {{
            color: {colors['text']};
            font-size: 14px;
        }}
        
        QLabel.title {{
            font-size: 18px;
            font-weight: bold;
            color: {colors['primary']};
            margin-bottom: 10px;
        }}
        
        QLabel.subtitle {{
            font-size: 16px;
            font-weight: 600;
            color: {colors['text_secondary']};
            margin-bottom: 8px;
        }}
        
        QLabel.caption {{
            font-size: 12px;
            color: {colors['text_muted']};
        }}
        
        QLabel.error {{
            color: {colors['danger']};
            font-weight: 500;
        }}
        
        QLabel.success {{
            color: {colors['success']};
            font-weight: 500;
        }}
        
        QLabel.warning {{
            color: {colors['warning']};
            font-weight: 500;
        }}
        
        /* Frames y grupos */
        QFrame, QGroupBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 12px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {colors['primary']};
            font-weight: bold;
        }}
        
        /* Line Edits */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            selection-background-color: {colors['primary']};
            selection-color: {colors['text_inverse']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {colors['focus']};
            padding: 7px 11px;
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {colors['disabled']};
            color: {colors['text_muted']};
        }}
        
        /* Combo Box */
        QComboBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            min-height: 36px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {colors['border_light']};
        }}
        
        QComboBox:focus {{
            border: 2px solid {colors['focus']};
            padding: 7px 11px;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors['text_secondary']};
            margin-right: 10px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            selection-background-color: {colors['selected']};
            selection-color: {colors['text_inverse']};
        }}
        
        /* Spin Box */
        QSpinBox, QDoubleSpinBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            min-height: 36px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {colors['focus']};
            padding: 7px 11px;
        }}
        
        /* Check Box y Radio Button */
        QCheckBox, QRadioButton {{
            color: {colors['text']};
            font-size: 14px;
            spacing: 8px;
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border: 2px solid {colors['primary']};
            border-radius: 3px;
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors['primary']};
            border: 2px solid {colors['primary']};
            border-radius: 9px;
        }}
        
        /* Progress bars */
        QProgressBar {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            background-color: {colors['surface']};
            text-align: center;
            color: {colors['text_secondary']};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 3px;
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            background-color: {colors['surface']};
        }}
        
        QTabBar::tab {{
            background-color: {colors['surface_secondary']};
            padding: 8px 16px;
            margin-right: 2px;
            border: 1px solid {colors['border']};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            color: {colors['text_secondary']};
        }}
        
        QTabBar::tab:selected, QTabBar::tab:hover {{
            background-color: {colors['surface']};
            color: {colors['primary']};
            font-weight: bold;
        }}
        
        QTabBar::tab:selected {{
            border-bottom: 2px solid {colors['primary']};
        }}
        
        /* Toolbar */
        QToolBar {{
            background-color: {colors['surface']};
            border-bottom: 1px solid {colors['border']};
            spacing: 5px;
            padding: 5px;
        }}
        
        QToolBar::separator {{
            background-color: {colors['border']};
            width: 1px;
            margin: 0 10px;
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {colors['surface']};
            border-top: 1px solid {colors['border']};
            color: {colors['text_secondary']};
            font-size: 12px;
        }}
        
        /* Menu */
        QMenu {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            padding: 5px;
        }}
        
        QMenu::item {{
            padding: 5px 20px 5px 20px;
            color: {colors['text']};
        }}
        
        QMenu::item:selected {{
            background-color: {colors['selected']};
            color: {colors['text_inverse']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {colors['border']};
            margin: 5px 0;
        }}
        
        /* Message Box */
        QMessageBox {{
            background-color: {colors['surface']};
        }}
        
        QMessageBox QLabel {{
            color: {colors['text']};
            font-size: 14px;
        }}
        
        /* Dialog */
        QDialog {{
            background-color: {colors['surface']};
        }}
        
        /* Splitter */
        QSplitter::handle {{
            background-color: {colors['border']};
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors['border_light']};
        }}
        
        /* Scrollbars generales */
        QScrollBar:vertical {{
            background-color: {colors['surface_secondary']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_muted']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['surface_secondary']};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['text_muted']};
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 12px;
        }}
        
        /* Separadores */
        QFrame[frameShape="4"] {{ /* HLine */
            background-color: {colors['border']};
            max-height: 1px;
            min-height: 1px;
        }}
        
        QFrame[frameShape="5"] {{ /* VLine */
            background-color: {colors['border']};
            max-width: 1px;
            min-width: 1px;
        }}
        """
    
    def get_color(self, color_name: str, theme: Optional[str] = None) -> str:
        """Obtener color por nombre"""
        if theme is None:
            theme = self.current_theme
        return self.color_palette.get_color(color_name, theme)
    
    def apply_stylesheet(self, widget, theme: Optional[str] = None,
                        components: Optional[List[str]] = None,
                        use_theme_file: bool = True):
        """Aplicar estilos a un widget"""
        stylesheet = self.get_stylesheet(theme, components, use_theme_file)
        widget.setStyleSheet(stylesheet)
    
    def update_theme(self, dark_mode: bool):
        """Actualizar tema basado en modo oscuro/claro"""
        theme = 'dark' if dark_mode else 'light'
        self.set_theme(theme)
    
    def apply_widget_styles(self, widget, widget_type: str = None):
        """
        Aplicar estilos específicos a un widget basado en su tipo
        
        Args:
            widget: Widget a estilizar
            widget_type: Tipo de widget (sidebar, topbar, etc.)
        """
        if widget_type:
            # Aplicar solo estilos de ese componente
            self.apply_stylesheet(widget, components=[widget_type])
        else:
            # Aplicar todos los estilos
            self.apply_stylesheet(widget)
    
    def refresh_all_widgets(self, parent_widget):
        """
        Refrescar estilos de todos los widgets hijos recursivamente
        
        Args:
            parent_widget: Widget padre desde donde comenzar
        """
        self.apply_stylesheet(parent_widget)
        
        # Refrescar hijos recursivamente
        for child in parent_widget.findChildren(QWidget):
            if child != parent_widget:
                self.apply_stylesheet(child)
    
    @property
    def is_dark(self) -> bool:
        """¿Está en modo oscuro?"""
        return self.current_theme == 'dark'
    
    @property
    def palette(self) -> Dict[str, str]:
        """Obtener paleta de colores actual"""
        return self.color_palette.all
    
    @property
    def available_themes(self) -> List[str]:
        """Obtener lista de temas disponibles"""
        return list(self._themes.keys())
    
    @property
    def available_components(self) -> List[str]:
        """Obtener lista de componentes disponibles"""
        return list(self._component_styles.keys())
    
    def debug_info(self) -> str:
        """Información de debug del StyleManager"""
        info = [
            f"StyleManager Debug Info",
            f"=======================",
            f"• Tema actual: {self.current_theme}",
            f"• Temas disponibles: {', '.join(self.available_themes)}",
            f"• Componentes registrados: {', '.join(self.available_components)}",
            f"• Estilos en caché: {len(self.stylesheet_cache)}",
            f"• Modo oscuro: {self.is_dark}",
            f"",
            f"Colores principales:",
            f"  • primary: {self.get_color('primary')}",
            f"  • background: {self.get_color('background')}",
            f"  • surface: {self.get_color('surface')}",
            f"  • text: {self.get_color('text')}",
            f"  • border: {self.get_color('border')}",
            f"",
            f"Estadísticas:",
            f"  • Tamaño caché: {sum(len(css) for css in self.stylesheet_cache.values())} chars",
        ]
        return "\n".join(info)


# Singleton para acceso global
_style_manager_instance = None

def get_style_manager() -> StyleManager:
    """Obtener instancia global del StyleManager"""
    global _style_manager_instance
    if _style_manager_instance is None:
        _style_manager_instance = StyleManager()
    return _style_manager_instance


# Función de conveniencia para aplicar estilos rápidamente
def apply_global_styles(app):
    """Aplicar estilos globales a toda la aplicación"""
    sm = get_style_manager()
    sm.apply_stylesheet(app)