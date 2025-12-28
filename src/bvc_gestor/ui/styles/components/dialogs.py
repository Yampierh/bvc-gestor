# src/bvc_gestor/ui/styles/components/dialogs.py
"""
Estilos para diálogos y ventanas modales
"""
from ..utils.color_palette import ColorPalette


class DialogStyles:
    """Estilos para diálogos de la aplicación"""
    
    @staticmethod
    def get_styles(theme: str = 'light') -> str:
        """Obtener estilos CSS para diálogos"""
        colors = ColorPalette.get_palette(theme)
        
        return f"""
        /* ===== DIÁLOGOS Y MODALES ===== */
        
        /* Diálogo principal */
        QDialog {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 10px;
        }}
        
        /* Título del diálogo */
        QLabel.dialog-title {{
            font-size: 18px;
            font-weight: bold;
            color: {colors['primary']};
            padding: 15px 20px;
            border-bottom: 1px solid {colors['border']};
            background-color: {colors['surface_secondary']};
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }}
        
        /* Contenido del diálogo */
        QWidget.dialog-content {{
            padding: 20px;
        }}
        
        /* Botones del diálogo */
        QDialogButtonBox {{
            padding: 15px 20px;
            border-top: 1px solid {colors['border']};
            background-color: {colors['surface_secondary']};
            border-bottom-left-radius: 10px;
            border-bottom-right-radius: 10px;
        }}
        
        QDialogButtonBox QPushButton {{
            min-width: 80px;
            min-height: 36px;
        }}
        
        /* Diálogo de confirmación */
        QDialog.confirmation-dialog {{
            min-width: 400px;
            min-height: 200px;
        }}
        
        /* Diálogo de error */
        QDialog.error-dialog {{
            border: 2px solid {colors['danger']};
        }}
        
        QDialog.error-dialog QLabel.dialog-title {{
            color: {colors['danger']};
            background-color: rgba(220, 53, 69, 0.1);
        }}
        
        /* Diálogo de éxito */
        QDialog.success-dialog {{
            border: 2px solid {colors['success']};
        }}
        
        QDialog.success-dialog QLabel.dialog-title {{
            color: {colors['success']};
            background-color: rgba(40, 167, 69, 0.1);
        }}
        
        /* Diálogo de advertencia */
        QDialog.warning-dialog {{
            border: 2px solid {colors['warning']};
        }}
        
        QDialog.warning-dialog QLabel.dialog-title {{
            color: {colors['warning']};
            background-color: rgba(255, 193, 7, 0.1);
        }}
        
        /* Diálogo de información */
        QDialog.info-dialog {{
            border: 2px solid {colors['info']};
        }}
        
        QDialog.info-dialog QLabel.dialog-title {{
            color: {colors['info']};
            background-color: rgba(23, 162, 184, 0.1);
        }}
        
        /* Diálogo con pestañas */
        QDialog.tabbed-dialog QTabWidget::pane {{
            border: none;
            background-color: transparent;
        }}
        
        QDialog.tabbed-dialog QTabBar::tab {{
            padding: 10px 20px;
            margin-right: 5px;
        }}
        
        /* Diálogo de carga/progreso */
        QDialog.progress-dialog QProgressBar {{
            min-height: 30px;
            border-radius: 15px;
        }}
        
        QDialog.progress-dialog QLabel {{
            text-align: center;
            margin-bottom: 15px;
        }}
        
        /* Diálogo de selección */
        QDialog.selection-dialog QListView, QDialog.selection-dialog QTreeView {{
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 5px;
        }}
        
        /* Diálogo con formulario */
        QDialog.form-dialog QFrame {{
            border: none;
            background-color: transparent;
        }}
        
        /* Diálogo de ayuda */
        QDialog.help-dialog {{
            max-width: 600px;
        }}
        
        QDialog.help-dialog QTextBrowser {{
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 10px;
            background-color: {colors['surface']};
        }}
        
        /* Overlay de diálogo (fondo) */
        QWidget.dialog-overlay {{
            background-color: rgba(0, 0, 0, 0.5);
        }}
        """