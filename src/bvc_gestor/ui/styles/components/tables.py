# src/bvc_gestor/ui/styles/components/tables.py
"""
Estilos para tablas
"""
from ..utils.color_palette import ColorPalette


class TableStyles:
    """Estilos para tablas de la aplicación"""
    
    @staticmethod
    def get_styles(theme: str = 'light') -> str:
        """Obtener estilos CSS para tablas"""
        colors = ColorPalette.get_palette(theme)
        
        return f"""
        /* ===== TABLAS ===== */
        
        /* Tabla principal */
        QTableView, QTableWidget {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            gridline-color: {colors['border_light']};
            font-size: 13px;
            outline: none; /* Remover outline por defecto */
        }}
        
        /* Items de la tabla */
        QTableView::item, QTableWidget::item {{
            padding: 8px;
            color: {colors['text']};
            border-bottom: 1px solid {colors['border_light']};
        }}
        
        QTableView::item:selected, QTableWidget::item:selected {{
            background-color: {colors['selected']};
            color: {colors['text_inverse']};
            border: none;
        }}
        
        QTableView::item:focus, QTableWidget::item:focus {{
            outline: none;
            border: 1px solid {colors['focus']};
        }}
        
        /* Filas alternas */
        QTableView::item:alternate, QTableWidget::item:alternate {{
            background-color: {colors['surface_secondary']};
        }}
        
        /* Header de la tabla */
        QHeaderView::section {{
            background-color: {colors['surface_secondary']};
            padding: 10px 8px;
            border: none;
            border-right: 1px solid {colors['border']};
            border-bottom: 2px solid {colors['border']};
            font-weight: 600;
            color: {colors['text_secondary']};
            font-size: 12px;
            text-transform: uppercase;
        }}
        
        QHeaderView::section:checked {{
            background-color: {colors['selected']};
            color: {colors['text_inverse']};
        }}
        
        QHeaderView::section:hover {{
            background-color: {colors['hover']};
        }}
        
        /* Scrollbar de tabla */
        QTableView QScrollBar:vertical, QTableWidget QScrollBar:vertical {{
            background-color: {colors['surface_secondary']};
            width: 10px;
            border-radius: 5px;
        }}
        
        QTableView QScrollBar::handle:vertical, QTableWidget QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 5px;
            min-height: 20px;
        }}
        
        /* Tabla de órdenes - colores especiales */
        QTableWidget#ordenes-table QTableWidget::item[data-type="compra"] {{
            color: {colors['profit']};
            font-weight: 500;
        }}
        
        QTableWidget#ordenes-table QTableWidget::item[data-type="venta"] {{
            color: {colors['loss']};
            font-weight: 500;
        }}
        
        /* Tabla de clientes */
        QTableWidget#clientes-table QTableWidget::item[data-estado="activo"] {{
            color: {colors['success']};
        }}
        
        QTableWidget#clientes-table QTableWidget::item[data-estado="inactivo"] {{
            color: {colors['text_muted']};
        }}
        
        /* Tabla compacta (para dashboards) */
        QTableView.compact, QTableWidget.compact {{
            font-size: 12px;
        }}
        
        QTableView.compact::item, QTableWidget.compact::item {{
            padding: 4px 6px;
        }}
        
        /* Tabla sin bordes */
        QTableView.no-border, QTableWidget.no-border {{
            border: none;
            gridline-color: transparent;
        }}
        """