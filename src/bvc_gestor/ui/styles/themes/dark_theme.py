# src/bvc_gestor/ui/styles/themes/dark_theme.py
"""
Tema oscuro completo para BVC-GESTOR
"""
from typing import Dict, Any
import logging

from ..components.buttons import ButtonStyles
from ..components.tables import TableStyles
from ..components.cards import CardStyles
from ..components.forms import FormStyles
from ..components.dialogs import DialogStyles
from ..components.sidebar import SidebarStyles
from ..components.topbar import TopbarStyles
from ..components.statusbar import StatusbarStyles
from ..utils.color_palette import ColorPalette


class DarkTheme:
    """Tema oscuro completo para BVC-GESTOR"""
    
    @staticmethod
    def get_stylesheet() -> str:
        """Obtener hoja de estilos completa para tema oscuro"""
        # Variables CSS del tema oscuro
        css_vars = ColorPalette.get_css_variables('dark')
        
        # Estilos base para tema oscuro
        base_styles = DarkTheme._get_base_styles()
        
        # Combinar todos los estilos de componentes
        full_stylesheet = (
            css_vars + "\n" +
            base_styles + "\n" +
            SidebarStyles.get_styles('dark') + "\n" +
            TopbarStyles.get_styles('dark') + "\n" +
            ButtonStyles.get_styles('dark') + "\n" +
            TableStyles.get_styles('dark') + "\n" +
            CardStyles.get_styles('dark') + "\n" +
            FormStyles.get_styles('dark') + "\n" +
            DialogStyles.get_styles('dark') + "\n" +
            StatusbarStyles.get_styles('dark')
        )
        
        return full_stylesheet
    
    @staticmethod
    def _get_base_styles() -> str:
        """Obtener estilos base específicos para tema oscuro"""
        colors = ColorPalette.get_palette('dark')
        
        return f"""
        /* ===== TEMA OSCURO - ESTILOS BASE ===== */
        
        /* Aplicación principal */
        QMainWindow {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}
        
        /* Widgets generales */
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text']};
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 14px;
            selection-background-color: {colors['primary']};
            selection-color: {colors['text_inverse']};
        }}
        
        /* Labels */
        QLabel {{
            color: {colors['text']};
            background-color: transparent;
        }}
        
        QLabel.title {{
            color: {colors['primary']};
            font-size: 18px;
            font-weight: bold;
        }}
        
        QLabel.subtitle {{
            color: {colors['text_secondary']};
            font-size: 16px;
            font-weight: 600;
        }}
        
        QLabel.caption {{
            color: {colors['text_muted']};
            font-size: 12px;
        }}
        
        /* Frames y grupos */
        QFrame, QGroupBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            color: {colors['text']};
        }}
        
        QGroupBox {{
            padding-top: 10px;
            margin-top: 20px;
        }}
        
        QGroupBox::title {{
            color: {colors['primary']};
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            font-weight: bold;
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {colors['surface_secondary']};
            width: 12px;
            border-radius: 6px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_muted']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['surface_secondary']};
            height: 12px;
            border-radius: 6px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['text_muted']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
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
        
        /* Progress bars */
        QProgressBar {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            background-color: {colors['surface_secondary']};
            text-align: center;
            color: {colors['text_secondary']};
            padding: 1px;
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
            margin-top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {colors['surface_secondary']};
            color: {colors['text_secondary']};
            padding: 8px 16px;
            margin-right: 2px;
            border: 1px solid {colors['border']};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 80px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['surface']};
            color: {colors['primary']};
            font-weight: bold;
            border-bottom: 2px solid {colors['primary']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {colors['hover']};
            color: {colors['text']};
        }}
        
        QTabBar::tab:disabled {{
            color: {colors['text_muted']};
            background-color: {colors['surface_secondary']};
        }}
        
        /* Checkboxes y RadioButtons */
        QCheckBox, QRadioButton {{
            color: {colors['text']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
        }}
        
        QCheckBox::indicator:unchecked {{
            border: 2px solid {colors['border']};
            background-color: {colors['surface']};
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:checked {{
            border: 2px solid {colors['primary']};
            background-color: {colors['primary']};
            border-radius: 3px;
            image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><path d='M2,5 L4,7 L8,2' stroke='white' stroke-width='2' fill='none'/></svg>");
        }}
        
        QRadioButton::indicator:unchecked {{
            border: 2px solid {colors['border']};
            background-color: {colors['surface']};
            border-radius: 9px;
        }}
        
        QRadioButton::indicator:checked {{
            border: 2px solid {colors['primary']};
            background-color: {colors['primary']};
            border-radius: 9px;
        }}
        
        /* LineEdits y TextEdits */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px 12px;
            selection-background-color: {colors['primary']};
            selection-color: {colors['text_inverse']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {colors['primary']};
            padding: 5px 11px;
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {colors['surface_secondary']};
            color: {colors['text_muted']};
            border: 1px solid {colors['border']};
        }}
        
        QLineEdit[readOnly="true"], QTextEdit[readOnly="true"], QPlainTextEdit[readOnly="true"] {{
            background-color: {colors['surface_secondary']};
            color: {colors['text_secondary']};
        }}
        
        /* ComboBox */
        QComboBox {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px 12px;
            min-height: 30px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {colors['text_muted']};
        }}
        
        QComboBox:focus {{
            border: 2px solid {colors['primary']};
            padding: 5px 11px;
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
            color: {colors['text']};
            border: 1px solid {colors['border']};
            selection-background-color: {colors['primary']};
            selection-color: {colors['text_inverse']};
        }}
        
        /* SpinBox */
        QSpinBox, QDoubleSpinBox {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px 12px;
            min-height: 30px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {colors['primary']};
            padding: 5px 11px;
        }}
        
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            background-color: {colors['surface_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 2px;
            width: 20px;
        }}
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {colors['hover']};
        }}
        
        QSpinBox::up-arrow, QSpinBox::down-arrow,
        QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {{
            width: 6px;
            height: 6px;
            border-left: 2px solid {colors['text']};
            border-bottom: 2px solid {colors['text']};
        }}
        
        /* Slider */
        QSlider::groove:horizontal {{
            border: 1px solid {colors['border']};
            height: 6px;
            background: {colors['surface_secondary']};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {colors['primary']};
            border: 1px solid {colors['primary_dark']};
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {colors['primary_light']};
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
        
        /* Mensajes y alertas */
        QMessageBox {{
            background-color: {colors['surface']};
            color: {colors['text']};
        }}
        
        QMessageBox QLabel {{
            color: {colors['text']};
        }}
        
        /* Menús */
        QMenu {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 6px 24px 6px 12px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['selected']};
            color: {colors['text_inverse']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {colors['border']};
            margin: 4px 8px;
        }}
        
        /* Toolbars */
        QToolBar {{
            background-color: {colors['surface']};
            border-bottom: 1px solid {colors['border']};
            spacing: 4px;
            padding: 4px;
        }}
        
        QToolBar::separator {{
            background-color: {colors['border']};
            width: 1px;
            margin: 4px 8px;
        }}
        
        /* Splitter */
        QSplitter::handle {{
            background-color: {colors['border']};
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors['primary']};
        }}
        
        /* Estado de validación */
        .valid {{
            border: 2px solid {colors['success']} !important;
        }}
        
        .invalid {{
            border: 2px solid {colors['danger']} !important;
        }}
        
        .warning {{
            border: 2px solid {colors['warning']} !important;
        }}
        
        /* Estados financieros */
        .profit {{
            color: {colors['profit']} !important;
            font-weight: 500;
        }}
        
        .loss {{
            color: {colors['loss']} !important;
            font-weight: 500;
        }}
        
        .neutral {{
            color: {colors['text_secondary']} !important;
        }}
        
        /* Estados de cliente */
        .active {{
            color: {colors['success']} !important;
        }}
        
        .inactive {{
            color: {colors['text_muted']} !important;
        }}
        
        /* Estados de orden */
        .pending {{
            color: {colors['warning']} !important;
        }}
        
        .executed {{
            color: {colors['success']} !important;
        }}
        
        .cancelled {{
            color: {colors['text_muted']} !important;
        }}
        
        .rejected {{
            color: {colors['danger']} !important;
        }}
        """
    
    @staticmethod
    def get_color_overrides() -> Dict[str, str]:
        """
        Obtener sobreescrituras de color específicas para tema oscuro
        
        Returns:
            Dict con colores específicos para widgets particulares
        """
        colors = ColorPalette.get_palette('dark')
        
        return {
            # Sobreescrituras específicas para tema oscuro
            'QTableView::item:alternate': f'background-color: {colors["surface_secondary"]}',
            'QTableWidget::item:alternate': f'background-color: {colors["surface_secondary"]}',
            
            # Headers de tabla más oscuros
            'QHeaderView::section': f'''
                background-color: {colors['surface_secondary']};
                color: {colors['text_secondary']};
                border: none;
                border-right: 1px solid {colors['border']};
                border-bottom: 2px solid {colors['border']};
            ''',
            
            # Botones de formulario
            'QDialogButtonBox QPushButton': f'''
                min-width: 80px;
                min-height: 36px;
            ''',
            
            # Placeholder text más visible
            'QLineEdit::placeholder, QTextEdit::placeholder-text': f'''
                color: {colors['text_muted']};
            ''',
        }


# También crear el tema claro actualizado
class LightTheme:
    """Tema claro completo para BVC-GESTOR"""
    
    @staticmethod
    def get_stylesheet() -> str:
        """Obtener hoja de estilos completa para tema claro"""
        css_vars = ColorPalette.get_css_variables('light')
        
        # Reutilizar la misma estructura pero con colores claros
        base_styles = DarkTheme._get_base_styles().replace(
            "TEMA OSCURO - ESTILOS BASE", 
            "TEMA CLARO - ESTILOS BASE"
        )
        
        # Combinar todos los estilos de componentes
        full_stylesheet = (
            css_vars + "\n" +
            base_styles + "\n" +
            SidebarStyles.get_styles('light') + "\n" +
            TopbarStyles.get_styles('light') + "\n" +
            ButtonStyles.get_styles('light') + "\n" +
            TableStyles.get_styles('light') + "\n" +
            CardStyles.get_styles('light') + "\n" +
            FormStyles.get_styles('light') + "\n" +
            DialogStyles.get_styles('light') + "\n" +
            StatusbarStyles.get_styles('light')
        )
        
        return full_stylesheet


if __name__ == "__main__":
    """Prueba del tema oscuro"""
    print("🧪 Probando tema oscuro...\n")
    
    # Generar estilos
    stylesheet = DarkTheme.get_stylesheet()
    
    # Mostrar información
    print(f"📄 Longitud del stylesheet: {len(stylesheet)} caracteres")
    print(f"📊 Líneas de código: {stylesheet.count(chr(10))}")
    
    # Mostrar primeras 10 líneas
    print(f"\n📝 Primeras 10 líneas:")
    for i, line in enumerate(stylesheet.split('\n')[:10], 1):
        print(f"{i:3}: {line}")
    
    # Mostrar algunas variables CSS
    print(f"\n🎨 Algunas variables CSS:")
    css_lines = [line for line in stylesheet.split('\n') if '--bvc-' in line]
    for var in css_lines[:5]:
        print(f"  {var.strip()}")
    
    print(f"\n✅ Tema oscuro generado exitosamente")