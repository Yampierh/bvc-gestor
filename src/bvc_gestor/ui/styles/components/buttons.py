# src/bvc_gestor/ui/styles/components/buttons.py
"""
Estilos para botones
"""
from ..utils.color_palette import ColorPalette


class ButtonStyles:
    """Estilos para botones de la aplicación"""
    
    @staticmethod
    def get_styles(theme: str = 'light') -> str:
        """Obtener estilos CSS para botones"""
        colors = ColorPalette.get_palette(theme)
        
        return f"""
        /* ===== BOTONES PRINCIPALES ===== */
        
        /* Botón primario (azul BVC) */
        QPushButton.primary {{
            background-color: {colors['primary']};
            color: {colors['text_inverse']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 14px;
            min-height: 36px;
        }}
        
        QPushButton.primary:hover {{
            background-color: {colors['primary_dark']};
        }}
        
        QPushButton.primary:pressed {{
            background-color: {colors['primary_dark']};
            padding: 9px 15px 7px 17px; /* Efecto de presión */
        }}
        
        QPushButton.primary:disabled {{
            background-color: {colors['disabled']};
            color: {colors['text_muted']};
        }}
        
        /* Botón secundario */
        QPushButton.secondary {{
            background-color: {colors['secondary']};
            color: {colors['text_inverse']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 14px;
            min-height: 36px;
        }}
        
        QPushButton.secondary:hover {{
            background-color: {colors['border']};
        }}
        
        QPushButton.secondary:disabled {{
            background-color: {colors['disabled']};
            color: {colors['text_muted']};
        }}
        
        /* Botón éxito (verde) */
        QPushButton.success {{
            background-color: {colors['success']};
            color: {colors['text_inverse']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 14px;
            min-height: 36px;
        }}
        
        QPushButton.success:hover {{
            background-color: {colors['profit']};
        }}
        
        /* Botón peligro (rojo) */
        QPushButton.danger {{
            background-color: {colors['danger']};
            color: {colors['text_inverse']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 14px;
            min-height: 36px;
        }}
        
        QPushButton.danger:hover {{
            background-color: {colors['loss']};
        }}
        
        /* Botón outline (borde solamente) */
        QPushButton.outline {{
            background-color: transparent;
            color: {colors['primary']};
            border: 2px solid {colors['primary']};
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 500;
            font-size: 14px;
            min-height: 36px;
        }}
        
        QPushButton.outline:hover {{
            background-color: {colors['primary_light']};
        }}
        
        /* Botón de texto (sin fondo) */
        QPushButton.text {{
            background-color: transparent;
            color: {colors['primary']};
            border: none;
            padding: 6px 12px;
            font-weight: 500;
            font-size: 14px;
            min-height: 36px;
        }}
        
        QPushButton.text:hover {{
            background-color: {colors['hover']};
            border-radius: 4px;
        }}
        
        /* Botón pequeño */
        QPushButton.small {{
            padding: 4px 8px;
            font-size: 12px;
            min-height: 28px;
        }}
        
        /* Botón grande */
        QPushButton.large {{
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
            min-height: 48px;
        }}
        
        /* Botón con icono */
        QPushButton.icon-button {{
            background-color: transparent;
            border: none;
            padding: 8px;
            min-width: 40px;
            min-height: 40px;
            border-radius: 6px;
        }}
        
        QPushButton.icon-button:hover {{
            background-color: {colors['hover']};
        }}
        
        /* Botón toolbar */
        QPushButton.toolbar-button {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 13px;
            min-height: 32px;
        }}
        
        QPushButton.toolbar-button:hover {{
            background-color: {colors['hover']};
        }}
        
        /* Botón sidebar */
        QPushButton.sidebar-button {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            font-weight: 500;
            font-size: 14px;
            color: {colors['text']};
            margin: 2px 8px;
        }}
        
        QPushButton.sidebar-button:hover {{
            background-color: {colors['hover']};
        }}
        
        QPushButton.sidebar-button:checked {{
            background-color: {colors['selected']};
            color: {colors['text_inverse']};
            font-weight: 600;
        }}
        
        QPushButton.sidebar-button:checked:hover {{
            background-color: {colors['selected']};
        }}
        """