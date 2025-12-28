# src/bvc_gestor/ui/styles/themes/light_theme.py
"""
Tema claro completo para BVC-GESTOR
"""
from ..components.buttons import ButtonStyles
from ..components.tables import TableStyles
from ..components.cards import CardStyles
from ..components.forms import FormStyles
from ..components.dialogs import DialogStyles
from ..components.sidebar import SidebarStyles
from ..components.topbar import TopbarStyles
from ..components.statusbar import StatusbarStyles
from ..utils.color_palette import ColorPalette


class LightTheme:
    """Tema claro completo para BVC-GESTOR"""
    
    @staticmethod
    def get_stylesheet() -> str:
        """Obtener hoja de estilos completa para tema claro"""
        colors = ColorPalette.get_palette('light')
        
        # Variables CSS
        css_vars = ColorPalette.get_css_variables('light')
        
        # Estilos base (siempre incluidos)
        base_styles = f"""
        /* ===== TEMA CLARO BVC-GESTOR ===== */
        /* Generado automáticamente - No modificar manualmente */
        
        /* Aplicación principal */
        QMainWindow {{
            background-color: {colors['background']};
        }}
        
        /* Widgets generales */
        QWidget {{
            font-family: "Segoe UI", "Arial", "Helvetica", sans-serif;
            font-size: 14px;
            color: {colors['text']};
            background-color: {colors['background']};
        }}
        
        /* Labels */
        QLabel {{
            color: {colors['text']};
            font-size: 14px;
            background-color: transparent;
        }}
        
        QLabel.title {{
            font-size: 20px;
            font-weight: bold;
            color: {colors['primary']};
            margin-bottom: 12px;
        }}
        
        QLabel.subtitle {{
            font-size: 16px;
            font-weight: 600;
            color: {colors['text_secondary']};
            margin-bottom: 10px;
        }}
        
        QLabel.section-title {{
            font-size: 18px;
            font-weight: bold;
            color: {colors['primary_dark']};
            padding-bottom: 8px;
            border-bottom: 2px solid {colors['border_light']};
            margin-bottom: 16px;
        }}
        
        QLabel.caption {{
            font-size: 12px;
            color: {colors['text_muted']};
            font-style: italic;
        }}
        
        QLabel.value-large {{
            font-size: 24px;
            font-weight: bold;
            color: {colors['primary']};
        }}
        
        QLabel.value-positive {{
            color: {colors['profit']};
            font-weight: 600;
        }}
        
        QLabel.value-negative {{
            color: {colors['loss']};
            font-weight: 600;
        }}
        
        /* Frames y contenedores */
        QFrame {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
        }}
        
        QFrame.card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 16px;
        }}
        
        QFrame.card:hover {{
            border-color: {colors['primary']};
            box-shadow: 0 2px 8px rgba(44, 90, 160, 0.1);
        }}
        
        QFrame.card-highlight {{
            border: 2px solid {colors['primary']};
            background-color: {colors['primary_light']};
        }}
        
        QGroupBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 16px;
            margin-top: 12px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 8px 0 8px;
            color: {colors['primary']};
            font-weight: bold;
            font-size: 14px;
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
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_muted']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
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
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['text_muted']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        /* Separadores */
        QFrame.separator-h {{
            background-color: {colors['border_light']};
            max-height: 1px;
            min-height: 1px;
            border: none;
        }}
        
        QFrame.separator-v {{
            background-color: {colors['border_light']};
            max-width: 1px;
            min-width: 1px;
            border: none;
        }}
        
        /* Progress bars */
        QProgressBar {{
            border: 1px solid {colors['border']};
            border-radius: 6px;
            background-color: {colors['surface']};
            text-align: center;
            color: {colors['text_secondary']};
            font-size: 12px;
            padding: 1px;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 5px;
        }}
        
        QProgressBar.success::chunk {{
            background-color: {colors['success']};
        }}
        
        QProgressBar.warning::chunk {{
            background-color: {colors['warning']};
        }}
        
        QProgressBar.danger::chunk {{
            background-color: {colors['danger']};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 8px;
            background-color: {colors['surface']};
            padding: 4px;
            margin-top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {colors['surface_secondary']};
            padding: 10px 20px;
            margin-right: 4px;
            border: 1px solid {colors['border']};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            color: {colors['text_secondary']};
            font-weight: 500;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['surface']};
            color: {colors['primary']};
            font-weight: 600;
            border-bottom: 2px solid {colors['primary']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {colors['hover']};
            color: {colors['text']};
        }}
        
        /* Line edits */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            selection-background-color: {colors['primary']};
            selection-color: {colors['text_inverse']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {colors['primary']};
            padding: 7px 11px;
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {colors['disabled']};
            color: {colors['text_muted']};
            border-color: {colors['border_light']};
        }}
        
        QLineEdit.search {{
            padding-left: 36px;
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="%236c757d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>');
            background-repeat: no-repeat;
            background-position: 12px center;
        }}
        
        /* Combo boxes */
        QComboBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            min-height: 36px;
        }}
        
        QComboBox:hover {{
            border-color: {colors['text_muted']};
        }}
        
        QComboBox:focus {{
            border: 2px solid {colors['primary']};
            padding: 7px 11px;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 36px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors['text_secondary']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 4px;
            selection-background-color: {colors['primary']};
            selection-color: {colors['text_inverse']};
        }}
        
        /* Spin boxes */
        QSpinBox, QDoubleSpinBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            min-height: 36px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {colors['primary']};
            padding: 7px 11px;
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            background-color: {colors['surface_secondary']};
            border: 1px solid {colors['border']};
            border-top-right-radius: 5px;
            width: 24px;
            height: 16px;
        }}
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: {colors['surface_secondary']};
            border: 1px solid {colors['border']};
            border-bottom-right-radius: 5px;
            width: 24px;
            height: 16px;
        }}
        
        /* Checkboxes y radio buttons */
        QCheckBox, QRadioButton {{
            color: {colors['text']};
            font-size: 14px;
            spacing: 8px;
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 20px;
            height: 20px;
        }}
        
        QCheckBox::indicator:unchecked {{
            border: 2px solid {colors['border']};
            border-radius: 4px;
            background-color: {colors['surface']};
        }}
        
        QCheckBox::indicator:checked {{
            border: 2px solid {colors['primary']};
            border-radius: 4px;
            background-color: {colors['primary']};
            image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>');
        }}
        
        QRadioButton::indicator:unchecked {{
            border: 2px solid {colors['border']};
            border-radius: 10px;
            background-color: {colors['surface']};
        }}
        
        QRadioButton::indicator:checked {{
            border: 2px solid {colors['primary']};
            border-radius: 10px;
            background-color: {colors['primary']};
        }}
        
        /* Mensajes y alertas */
        QMessageBox {{
            background-color: {colors['surface']};
        }}
        
        QMessageBox QLabel {{
            color: {colors['text']};
            font-size: 14px;
        }}
        
        /* Área de scroll */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        
        /* Splitter */
        QSplitter::handle {{
            background-color: {colors['border_light']};
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors['border']};
        }}
        
        /* Toolbar */
        QToolBar {{
            background-color: {colors['surface']};
            border-bottom: 1px solid {colors['border']};
            padding: 4px;
            spacing: 4px;
        }}
        
        QToolBar::separator {{
            background-color: {colors['border_light']};
            width: 1px;
            margin: 0 8px;
        }}
        
        /* Status bar */
        QStatusBar {{
            background-color: {colors['surface']};
            border-top: 1px solid {colors['border']};
            color: {colors['text_secondary']};
            font-size: 12px;
        }}
        """
        
        # Combinar todos los estilos
        full_stylesheet = (
            css_vars + "\n" +
            base_styles + "\n" +
            SidebarStyles.get_styles('light') + "\n" +
            TopbarStyles.get_styles('light') + "\n" +
            StatusbarStyles.get_styles('light') + "\n" +
            ButtonStyles.get_styles('light') + "\n" +
            TableStyles.get_styles('light') + "\n" +
            CardStyles.get_styles('light') + "\n" +
            FormStyles.get_styles('light') + "\n" +
            DialogStyles.get_styles('light')
        )
        
        return full_stylesheet
    
    @staticmethod
    def get_minimal_stylesheet() -> str:
        """Obtener versión mínima para pruebas"""
        colors = ColorPalette.get_palette('light')
        
        return f"""
        QMainWindow {{
            background-color: {colors['background']};
        }}
        
        QWidget {{
            font-family: "Segoe UI";
            font-size: 14px;
            color: {colors['text']};
        }}
        
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['primary_dark']};
        }}
        
        QLabel {{
            color: {colors['text']};
        }}
        """