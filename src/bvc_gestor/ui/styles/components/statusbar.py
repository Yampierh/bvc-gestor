# src/bvc_gestor/ui/styles/components/statusbar.py
"""
Estilos para la barra de estado
"""
from ..utils.color_palette import ColorPalette


class StatusbarStyles:
    """Estilos para la barra de estado de la aplicación"""
    
    @staticmethod
    def get_styles(theme: str = 'light') -> str:
        """Obtener estilos CSS para la statusbar"""
        colors = ColorPalette.get_palette(theme)
        
        return f"""
        /* ===== BARRA DE ESTADO ===== */
        
        /* Statusbar principal */
        QStatusBar {{
            background-color: {colors['surface_secondary']};
            border-top: 1px solid {colors['border']};
            font-size: 12px;
            color: {colors['text_secondary']};
            min-height: 24px;
            max-height: 24px;
        }}
        
        /* Labels dentro de la statusbar */
        QStatusBar QLabel {{
            color: {colors['text_secondary']};
            font-size: 12px;
            padding: 0 5px;
        }}
        
        /* Separadores en statusbar */
        QStatusBar QFrame[frameShape="5"] {{ /* VLine */
            background-color: {colors['border']};
            max-width: 1px;
            min-width: 1px;
            margin: 0 8px;
        }}
        
        /* Indicadores de estado */
        QLabel.status-indicator {{
            font-weight: 500;
            padding: 0 8px;
        }}
        
        /* Indicador de base de datos */
        QLabel#db-status {{
            font-weight: 600;
        }}
        
        QLabel#db-status[status="connected"] {{
            color: {colors['success']};
        }}
        
        QLabel#db-status[status="disconnected"] {{
            color: {colors['danger']};
        }}
        
        QLabel#db-status[status="error"] {{
            color: {colors['danger']};
            font-weight: bold;
        }}
        
        /* Indicador de usuario */
        QLabel#user-status {{
            color: {colors['primary']};
        }}
        
        /* Indicador de cambios */
        QLabel#changes-status {{
            font-style: italic;
        }}
        
        QLabel#changes-status[status="saved"] {{
            color: {colors['success']};
        }}
        
        QLabel#changes-status[status="pending"] {{
            color: {colors['warning']};
            font-weight: 500;
            animation: blink 2s infinite;
        }}
        
        /* Animación para cambios pendientes */
        @keyframes blink {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        
        /* Versión de la aplicación */
        QLabel#app-version {{
            color: {colors['text_muted']};
            font-size: 11px;
        }}
        
        /* Mensajes temporales */
        QStatusBar::item {{
            border: none;
        }}
        
        /* Botones en statusbar (si los hay) */
        QStatusBar QPushButton {{
            background-color: transparent;
            border: 1px solid {colors['border']};
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 11px;
            min-height: 18px;
            max-height: 18px;
        }}
        
        QStatusBar QPushButton:hover {{
            background-color: {colors['hover']};
        }}
        
        /* Progress bar en statusbar */
        QStatusBar QProgressBar {{
            border: 1px solid {colors['border']};
            border-radius: 3px;
            background-color: {colors['surface']};
            height: 14px;
            min-width: 100px;
            max-width: 200px;
        }}
        
        QStatusBar QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 2px;
        }}
        
        /* Área de mensajes */
        QStatusBar QLabel#message-area {{
            color: {colors['text']};
            font-weight: 500;
            padding: 0 10px;
            border-left: 1px solid {colors['border_light']};
            border-right: 1px solid {colors['border_light']};
        }}
        
        /* Mensajes de error */
        QStatusBar QLabel.error-message {{
            color: {colors['danger']};
            font-weight: bold;
        }}
        
        /* Mensajes de éxito */
        QStatusBar QLabel.success-message {{
            color: {colors['success']};
            font-weight: 500;
        }}
        
        /* Mensajes de advertencia */
        QStatusBar QLabel.warning-message {{
            color: {colors['warning']};
            font-weight: 500;
        }}
        
        /* Mensajes de información */
        QStatusBar QLabel.info-message {{
            color: {colors['info']};
        }}
        
        /* Indicador de conexión */
        QLabel.connection-indicator {{
            min-width: 12px;
            min-height: 12px;
            max-width: 12px;
            max-height: 12px;
            border-radius: 6px;
        }}
        
        QLabel.connection-indicator[status="online"] {{
            background-color: {colors['success']};
            border: 2px solid {colors['success']};
        }}
        
        QLabel.connection-indicator[status="offline"] {{
            background-color: {colors['danger']};
            border: 2px solid {colors['danger']};
        }}
        
        QLabel.connection-indicator[status="connecting"] {{
            background-color: {colors['warning']};
            border: 2px solid {colors['warning']};
            animation: pulse 1.5s infinite;
        }}
        
        /* Animación de pulso para conexión */
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.3; }}
            100% {{ opacity: 1; }}
        }}
        
        /* Grupo de indicadores */
        QFrame.status-group {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border_light']};
            border-radius: 4px;
            padding: 2px 6px;
            margin: 0 3px;
        }}
        
        /* Contador de notificaciones */
        QLabel.notification-count {{
            background-color: {colors['danger']};
            color: {colors['text_inverse']};
            border-radius: 8px;
            font-size: 9px;
            font-weight: bold;
            min-width: 16px;
            min-height: 16px;
            max-width: 16px;
            max-height: 16px;
            padding: 0;
        }}
        
        /* Reloj/tiempo */
        QLabel#clock {{
            font-family: "Consolas", "Monaco", monospace;
            font-size: 11px;
            color: {colors['text_secondary']};
            padding: 0 8px;
            border-left: 1px solid {colors['border_light']};
        }}
        
        /* Memoria/CPU (para debug) */
        QLabel.system-info {{
            font-size: 10px;
            color: {colors['text_muted']};
            font-family: "Consolas", "Monaco", monospace;
        }}
        
        /* Modo de desarrollo */
        QLabel.dev-mode {{
            background-color: {colors['danger']};
            color: {colors['text_inverse']};
            border-radius: 3px;
            padding: 1px 4px;
            font-size: 9px;
            font-weight: bold;
            margin: 0 5px;
        }}
        """