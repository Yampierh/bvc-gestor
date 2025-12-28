# src/bvc_gestor/ui/styles/components/cards.py
"""
Estilos para tarjetas y métricas
"""
from ..utils.color_palette import ColorPalette


class CardStyles:
    """Estilos para tarjetas de métricas y contenido"""
    
    @staticmethod
    def get_styles(theme: str = 'light') -> str:
        """Obtener estilos CSS para tarjetas"""
        colors = ColorPalette.get_palette(theme)
        
        return f"""
        /* ===== TARJETAS Y MÉTRICAS ===== */
        
        /* Tarjeta básica */
        QFrame.card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 16px;
        }}
        
        QFrame.card:hover {{
            border-color: {colors['primary']};
            box-shadow: 0 2px 8px {colors['border']}40;
        }}
        
        /* Tarjeta con sombra */
        QFrame.card-shadow {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 12px {colors['border']}30;
        }}
        
        /* Tarjeta sin borde */
        QFrame.card-borderless {{
            background-color: {colors['surface']};
            border: none;
            border-radius: 8px;
            padding: 16px;
        }}
        
        /* Tarjeta con color de acento */
        QFrame.card-accent {{
            background-color: {colors['surface']};
            border-left: 4px solid {colors['primary']};
            border-right: 1px solid {colors['border']};
            border-top: 1px solid {colors['border']};
            border-bottom: 1px solid {colors['border']};
            border-radius: 0 8px 8px 0;
            padding: 16px;
        }}
        
        /* Tarjeta de métrica (KPI) */
        QFrame.metric-card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 20px;
            min-height: 120px;
        }}
        
        QFrame.metric-card:hover {{
            border: 2px solid {colors['primary']};
            padding: 19px;
        }}
        
        /* Título de tarjeta */
        QLabel.card-title {{
            font-size: 14px;
            font-weight: 600;
            color: {colors['text_secondary']};
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* Valor de métrica */
        QLabel.metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: {colors['text']};
            margin-bottom: 4px;
        }}
        
        QLabel.metric-value[data-trend="up"] {{
            color: {colors['profit']};
        }}
        
        QLabel.metric-value[data-trend="down"] {{
            color: {colors['loss']};
        }}
        
        /* Variación de métrica */
        QLabel.metric-change {{
            font-size: 13px;
            font-weight: 500;
            padding: 2px 8px;
            border-radius: 10px;
        }}
        
        QLabel.metric-change[data-trend="up"] {{
            background-color: {colors['profit']}20;
            color: {colors['profit']};
        }}
        
        QLabel.metric-change[data-trend="down"] {{
            background-color: {colors['loss']}20;
            color: {colors['loss']};
        }}
        
        QLabel.metric-change[data-trend="neutral"] {{
            background-color: {colors['text_muted']}20;
            color: {colors['text_muted']};
        }}
        
        /* Icono en tarjeta */
        QLabel.metric-icon {{
            font-size: 24px;
            padding: 8px;
            border-radius: 8px;
            min-width: 40px;
            min-height: 40px;
            max-width: 40px;
            max-height: 40px;
            text-align: center;
        }}
        
        QLabel.metric-icon[data-type="clientes"] {{
            background-color: {colors['primary']}20;
            color: {colors['primary']};
        }}
        
        QLabel.metric-icon[data-type="capital"] {{
            background-color: {colors['success']}20;
            color: {colors['success']};
        }}
        
        QLabel.metric-icon[data-type="ordenes"] {{
            background-color: {colors['warning']}20;
            color: {colors['warning']};
        }}
        
        QLabel.metric-icon[data-type="rendimiento"] {{
            background-color: {colors['info']}20;
            color: {colors['info']};
        }}
        
        /* Tarjeta de gráfico */
        QFrame.chart-card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 0;
        }}
        
        QLabel.chart-title {{
            font-size: 16px;
            font-weight: 600;
            color: {colors['text']};
            padding: 16px 16px 8px 16px;
            border-bottom: 1px solid {colors['border_light']};
        }}
        
        /* Tarjeta de lista */
        QFrame.list-card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 0;
        }}
        
        QLabel.list-card-title {{
            font-size: 16px;
            font-weight: 600;
            color: {colors['text']};
            padding: 16px;
            border-bottom: 1px solid {colors['border_light']};
        }}
        
        /* Tarjeta de actividad reciente */
        QFrame.activity-card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 16px;
        }}
        
        QLabel.activity-item {{
            font-size: 13px;
            color: {colors['text']};
            padding: 8px 0;
            border-bottom: 1px solid {colors['border_light']};
        }}
        
        QLabel.activity-item:last-child {{
            border-bottom: none;
        }}
        
        QLabel.activity-time {{
            color: {colors['text_muted']};
            font-size: 11px;
            font-weight: 500;
        }}
        
        QLabel.activity-icon {{
            color: {colors['primary']};
            font-size: 14px;
            min-width: 24px;
        }}
        
        /* Tarjeta de estado (status) */
        QFrame.status-card {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 12px;
        }}
        
        QLabel.status-indicator {{
            min-width: 12px;
            min-height: 12px;
            max-width: 12px;
            max-height: 12px;
            border-radius: 6px;
            margin-right: 8px;
        }}
        
        QLabel.status-indicator[data-status="success"] {{
            background-color: {colors['success']};
        }}
        
        QLabel.status-indicator[data-status="warning"] {{
            background-color: {colors['warning']};
        }}
        
        QLabel.status-indicator[data-status="error"] {{
            background-color: {colors['danger']};
        }}
        
        QLabel.status-indicator[data-status="info"] {{
            background-color: {colors['info']};
        }}
        """