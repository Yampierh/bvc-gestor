# src/bvc_gestor/ui/styles/components/topbar.py
"""
Estilos específicos para la barra superior
"""
from ..utils.color_palette import ColorPalette


class TopbarStyles:
    """Estilos para la barra superior"""
    
    @staticmethod
    def get_styles(theme: str = 'light') -> str:
        """Obtener estilos CSS para la topbar"""
        colors = ColorPalette.get_palette(theme)
        
        return f"""
        /* ===== TOPBAR PRINCIPAL ===== */
        
        /* Widget topbar principal */
        QWidget#topbar-main {{
            background-color: {colors['surface']};
            border-bottom: 1px solid {colors['border']};
            min-height: 60px;
            max-height: 60px;
            padding: 0 20px;
        }}
        
        /* Título de la aplicación en topbar */
        QLabel#topbar-title {{
            font-size: 20px;
            font-weight: bold;
            color: {colors['primary']};
            padding: 0;
            margin: 0;
        }}
        
        QLabel#topbar-subtitle {{
            font-size: 14px;
            color: {colors['text_secondary']};
            margin-left: 10px;
            font-style: italic;
        }}
        
        /* Fecha y hora */
        QLabel#header-datetime {{
            color: {colors['text_secondary']};
            font-size: 14px;
            padding: 0;
            border-right: 1px solid {colors['border_light']};
        }}
        
        /* Botones de acción de la topbar */
        QPushButton.topbar-action-btn {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 8px;
            min-width: 40px;
            min-height: 40px;
            max-width: 40px;
            max-height: 40px;
            font-size: 16px;
            margin-left: 8px;
        }}
        
        QPushButton.topbar-action-btn:hover {{
            background-color: {colors['hover']};
            border-color: {colors['border']};
        }}
        
        QPushButton.topbar-action-btn:pressed {{
            background-color: {colors['border']};
            padding: 9px 7px 7px 9px;
        }}
        
        QPushButton.topbar-action-btn:checked {{
            background-color: {colors['selected']};
            color: {colors['text_inverse']};
            border-color: {colors['primary']};
        }}
        
        /* Botón de tema específico */
        QPushButton#theme-toggle-btn {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 8px;
            min-width: 40px;
            min-height: 40px;
            font-size: 18px;
        }}
        
        QPushButton#theme-toggle-btn:hover {{
            background-color: {colors['warning']};
            color: {colors['text_inverse']};
        }}
        
        /* Botón de notificaciones con badge */
        QPushButton#notifications-btn {{
            position: relative;
        }}
        
        /* Badge de notificaciones */
        QLabel.notification-badge {{
            background-color: {colors['danger']};
            color: white;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
            min-width: 18px;
            min-height: 18px;
            max-width: 18px;
            max-height: 18px;
            padding: 0;
            text-align: center;
            position: absolute;
            top: -5px;
            right: -5px;
            z-index: 100;
        }}
        
        /* Botón de perfil de usuario */
        QPushButton#profile-btn {{
            border-radius: 20px;
            padding: 6px 12px;
            min-height: 40px;
        }}
        
        QPushButton#profile-btn:hover {{
            background-color: {colors['hover']};
        }}
        
        /* Indicador de estado del sistema */
        QLabel#system-status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-right: 15px;
        }}
        
        QLabel#system-status[data-status="online"] {{
            background-color: {colors['success']}20;
            color: {colors['success']};
            border: 1px solid {colors['success']}40;
        }}
        
        QLabel#system-status[data-status="offline"] {{
            background-color: {colors['danger']}20;
            color: {colors['danger']};
            border: 1px solid {colors['danger']}40;
        }}
        
        QLabel#system-status[data-status="warning"] {{
            background-color: {colors['warning']}20;
            color: {colors['warning']};
            border: 1px solid {colors['warning']}40;
        }}
        
        /* Barra de búsqueda */
        QLineEdit#topbar-search {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 20px;
            padding: 8px 15px;
            padding-left: 35px;
            font-size: 14px;
            min-width: 250px;
            min-height: 36px;
        }}
        
        QLineEdit#topbar-search:focus {{
            border: 2px solid {colors['primary']};
            padding-left: 34px;
        }}
        
        QLineEdit#topbar-search::placeholder {{
            color: {colors['text_muted']};
        }}
        
        /* Icono de búsqueda */
        QLineEdit#topbar-search QToolButton {{
            background-color: transparent;
            border: none;
            color: {colors['text_muted']};
            padding: 0 8px;
        }}
        
        /* Menú desplegable en topbar */
        QPushButton.topbar-menu-btn {{
            background-color: transparent;
            border: none;
            padding: 10px 15px;
            color: {colors['text_secondary']};
            font-size: 14px;
        }}
        
        QPushButton.topbar-menu-btn:hover {{
            background-color: {colors['hover']};
            border-radius: 6px;
        }}
        
        QPushButton.topbar-menu-btn::menu-indicator {{
            image: none;
            width: 0;
        }}
        """