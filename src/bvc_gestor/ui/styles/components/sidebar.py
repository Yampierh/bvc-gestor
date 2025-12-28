# src/bvc_gestor/ui/styles/components/sidebar.py
"""
Estilos específicos para la barra lateral
"""
from ..utils.color_palette import ColorPalette


class SidebarStyles:
    """Estilos para la sidebar de navegación"""
    
    @staticmethod
    def get_styles(theme: str = 'light') -> str:
        """Obtener estilos CSS para la sidebar"""
        colors = ColorPalette.get_palette(theme)
        
        return f"""
        /* ===== SIDEBAR PRINCIPAL ===== */
        
        /* Widget sidebar principal */
        QWidget#sidebar-main {{
            background-color: {colors['surface']};
            border-right: 1px solid {colors['border']};
            min-width: 220px;
            max-width: 220px;
        }}
        
        /* Logo/título de la aplicación */
        QLabel#sidebar-logo {{
            font-size: 18px;
            font-weight: bold;
            color: {colors['primary']};
            padding: 15px;
            margin-bottom: 10px;
            text-align: center;
            border-bottom: 1px solid {colors['border_light']};
        }}
        
        /* Botones de navegación principales */
        QPushButton.sidebar-nav-btn {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 4px 8px;
            text-align: left;
            font-weight: 500;
            font-size: 14px;
            color: {colors['text']};
            min-height: 44px;
        }}
        
        QPushButton.sidebar-nav-btn:hover {{
            background-color: {colors['hover']};
        }}
        
        QPushButton.sidebar-nav-btn:checked {{
            background-color: {colors['selected']};
            color: {colors['text_inverse']};
            font-weight: 600;
        }}
        
        QPushButton.sidebar-nav-btn:checked:hover {{
            background-color: {colors['selected']};
        }}
        
        QPushButton.sidebar-nav-btn:disabled {{
            color: {colors['text_muted']};
            background-color: transparent;
        }}
        
        /* Iconos en botones de sidebar */
        QPushButton.sidebar-nav-btn::icon {{
            margin-right: 10px;
            width: 20px;
            height: 20px;
        }}
        
        /* Separador de secciones */
        QFrame#sidebar-separator {{
            background-color: {colors['border_light']};
            min-height: 1px;
            max-height: 1px;
            margin: 15px 10px;
        }}
        
        /* Área inferior de la sidebar */
        QWidget#sidebar-footer {{
            background-color: {colors['surface_secondary']};
            border-top: 1px solid {colors['border']};
            padding: 10px;
            margin-top: 20px;
        }}
        
        /* Versión de la aplicación en footer */
        QLabel#sidebar-version {{
            color: {colors['text_muted']};
            font-size: 11px;
            text-align: center;
            padding: 5px;
        }}
        
        /* Indicador de estado (punto) en botones */
        QPushButton.sidebar-nav-btn[data-status="active"]::before {{
            content: "●";
            color: {colors['success']};
            font-size: 12px;
            margin-right: 8px;
        }}
        
        QPushButton.sidebar-nav-btn[data-status="inactive"]::before {{
            content: "○";
            color: {colors['text_muted']};
            font-size: 12px;
            margin-right: 8px;
        }}
        
        /* Sidebar compacta (para pantallas pequeñas) */
        QWidget#sidebar-main.compact {{
            min-width: 60px;
            max-width: 60px;
        }}
        
        QWidget#sidebar-main.compact QPushButton.sidebar-nav-btn {{
            padding: 12px 0;
            text-align: center;
        }}
        
        QWidget#sidebar-main.compact QPushButton.sidebar-nav-btn::icon {{
            margin-right: 0;
        }}
        
        /* Badge de notificaciones en sidebar */
        QPushButton.sidebar-nav-btn[data-notifications]::after {{
            content: attr(data-notifications);
            background-color: {colors['danger']};
            color: white;
            font-size: 10px;
            font-weight: bold;
            border-radius: 8px;
            min-width: 16px;
            min-height: 16px;
            padding: 0 4px;
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
        }}
        """