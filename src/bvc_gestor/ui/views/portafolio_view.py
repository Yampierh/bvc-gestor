"""
Vista de Portafolio - Posiciones actuales del inversor.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import logging

logger = logging.getLogger(__name__)


class PortafolioView(QWidget):
    """
    Vista del portafolio de inversiones.
    
    Signals:
        vender_posicion_clicked: Emitido cuando se clickea vender (portafolio_item_id)
        volver_clicked: Emitido cuando se clickea volver
    """
    
    vender_posicion_clicked = pyqtSignal(int)
    volver_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.posiciones = []
        self.resumen = {}
        self.setup_ui()
        self.aplicar_estilos()
    
    def setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.btn_volver = QPushButton("← Volver")
        self.btn_volver.setObjectName("backButton")
        self.btn_volver.clicked.connect(self.volver_clicked.emit)
        
        title_label = QLabel("💼 Mi Portafolio")
        title_label.setObjectName("pageTitle")
        
        header_layout.addWidget(self.btn_volver)
        header_layout.addWidget(title_label, 1)
        
        layout.addLayout(header_layout)
        
        # --- Cards de Resumen ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Valor Total del Portafolio
        self.card_valor_total = self._crear_metric_card(
            "💰 Valor Total",
            "Bs. 0.00",
            "",
            "#2196F3"
        )
        cards_layout.addWidget(self.card_valor_total)
        
        # Inversión Inicial
        self.card_inversion = self._crear_metric_card(
            "📊 Inversión Inicial",
            "Bs. 0.00",
            "",
            "#9C27B0"
        )
        cards_layout.addWidget(self.card_inversion)
        
        # Ganancia/Pérdida
        self.card_ganancia = self._crear_metric_card(
            "📈 Ganancia/Pérdida",
            "Bs. 0.00",
            "",
            "#4CAF50"
        )
        cards_layout.addWidget(self.card_ganancia)
        
        # Rendimiento %
        self.card_rendimiento = self._crear_metric_card(
            "% Rendimiento",
            "0.00%",
            "",
            "#FF9800"
        )
        cards_layout.addWidget(self.card_rendimiento)
        
        layout.addLayout(cards_layout)
        
        # --- Tabla de Posiciones ---
        tabla_header = QLabel("📋 Posiciones Actuales")
        tabla_header.setObjectName("sectionTitle")
        layout.addWidget(tabla_header)
        
        self.tabla_portafolio = QTableWidget()
        self.tabla_portafolio.setObjectName("tablaPortafolio")
        self.tabla_portafolio.setColumnCount(10)
        self.tabla_portafolio.setHorizontalHeaderLabels([
            "Ticker", "Nombre", "Cantidad", "Disponible", "Costo Prom.",
            "Precio Actual", "Valor Mercado", "G/P", "Rendimiento %", "Acciones"
        ])
        
        # Configurar columnas
        header = self.tabla_portafolio.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in range(2, 9):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        self.tabla_portafolio.setColumnWidth(9, 80)
        
        self.tabla_portafolio.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_portafolio.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        
        layout.addWidget(self.tabla_portafolio, 1)
        
        # Footer
        footer_layout = QHBoxLayout()
        
        self.lbl_total_posiciones = QLabel("Total: 0 posiciones")
        self.lbl_total_posiciones.setObjectName("footerLabel")
        
        footer_layout.addWidget(self.lbl_total_posiciones)
        footer_layout.addStretch()
        
        layout.addLayout(footer_layout)
    
    def _crear_metric_card(self, titulo: str, valor: str, 
                          subtitulo: str, color: str) -> QFrame:
        """Crea una tarjeta de métrica"""
        card = QFrame()
        card.setObjectName("metricCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(20, 15, 20, 15)
        
        # Título
        title_label = QLabel(titulo)
        title_label.setObjectName("metricCardTitle")
        card_layout.addWidget(title_label)
        
        # Valor
        value_label = QLabel(valor)
        value_label.setObjectName("metricCardValue")
        value_label.setStyleSheet(f"color: {color};")
        card_layout.addWidget(value_label)
        
        # Subtítulo (si existe)
        if subtitulo:
            subtitle_label = QLabel(subtitulo)
            subtitle_label.setObjectName("metricCardSubtitle")
            card_layout.addWidget(subtitle_label)
        
        return card
    
    def actualizar_resumen(self, resumen: dict):
        """Actualiza las tarjetas de resumen"""
        self.resumen = resumen
        
        # Valor total
        valor_total = resumen.get('valor_mercado_total', 0)
        self.card_valor_total.findChild(QLabel, "metricCardValue").setText(
            f"Bs. {valor_total:,.2f}"
        )
        
        # Inversión inicial
        inversion = resumen.get('inversion_total', 0)
        self.card_inversion.findChild(QLabel, "metricCardValue").setText(
            f"Bs. {inversion:,.2f}"
        )
        
        # Ganancia/Pérdida
        gp = resumen.get('ganancia_perdida_total', 0)
        gp_label = self.card_ganancia.findChild(QLabel, "metricCardValue")
        
        if gp >= 0:
            gp_label.setText(f"+Bs. {gp:,.2f}")
            gp_label.setStyleSheet("color: #4CAF50;")
        else:
            gp_label.setText(f"Bs. {gp:,.2f}")
            gp_label.setStyleSheet("color: #F44336;")
        
        # Rendimiento %
        rendimiento = resumen.get('rendimiento_total_pct', 0)
        rend_label = self.card_rendimiento.findChild(QLabel, "metricCardValue")
        
        if rendimiento >= 0:
            rend_label.setText(f"+{rendimiento:.2f}%")
            rend_label.setStyleSheet("color: #4CAF50;")
        else:
            rend_label.setText(f"{rendimiento:.2f}%")
            rend_label.setStyleSheet("color: #F44336;")
    
    def poblar_tabla(self, posiciones: list):
        """Puebla la tabla con las posiciones"""
        self.posiciones = posiciones
        self.tabla_portafolio.setRowCount(len(posiciones))
        
        for row, pos in enumerate(posiciones):
            # Ticker
            ticker_item = QTableWidgetItem(pos['ticker'])
            ticker_item.setFont(ticker_item.font())
            ticker_item.font().setBold(True)
            self.tabla_portafolio.setItem(row, 0, ticker_item)
            
            # Nombre
            self.tabla_portafolio.setItem(row, 1, QTableWidgetItem(pos['nombre']))
            
            # Cantidad Total
            cant_item = QTableWidgetItem(f"{pos['cantidad_total']:,}")
            cant_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_portafolio.setItem(row, 2, cant_item)
            
            # Cantidad Disponible
            disp_item = QTableWidgetItem(f"{pos['cantidad_disponible']:,}")
            disp_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            if pos['cantidad_disponible'] < pos['cantidad_total']:
                disp_item.setForeground(QColor("#FF9800"))
            else:
                disp_item.setForeground(QColor("#4CAF50"))
            
            self.tabla_portafolio.setItem(row, 3, disp_item)
            
            # Costo Promedio
            costo_item = QTableWidgetItem(f"Bs. {pos['costo_promedio']:,.2f}")
            costo_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_portafolio.setItem(row, 4, costo_item)
            
            # Precio Actual
            precio_actual = pos.get('precio_actual', 0)
            precio_item = QTableWidgetItem(f"Bs. {precio_actual:,.2f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Color según si subió o bajó vs costo
            if precio_actual > pos['costo_promedio']:
                precio_item.setForeground(QColor("#4CAF50"))
            elif precio_actual < pos['costo_promedio']:
                precio_item.setForeground(QColor("#F44336"))
            
            self.tabla_portafolio.setItem(row, 5, precio_item)
            
            # Valor de Mercado
            valor_mercado = pos.get('valor_mercado', 0)
            valor_item = QTableWidgetItem(f"Bs. {valor_mercado:,.2f}")
            valor_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_portafolio.setItem(row, 6, valor_item)
            
            # Ganancia/Pérdida
            gp = pos.get('ganancia_perdida', 0)
            gp_texto = f"Bs. {abs(gp):,.2f}"
            if gp >= 0:
                gp_texto = f"+{gp_texto}"
            else:
                gp_texto = f"-{gp_texto}"
            
            gp_item = QTableWidgetItem(gp_texto)
            gp_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            if gp >= 0:
                gp_item.setForeground(QColor("#4CAF50"))
            else:
                gp_item.setForeground(QColor("#F44336"))
            
            self.tabla_portafolio.setItem(row, 7, gp_item)
            
            # Rendimiento %
            rendimiento = pos.get('rendimiento_pct', 0)
            rend_texto = f"{abs(rendimiento):.2f}%"
            if rendimiento >= 0:
                rend_texto = f"+{rend_texto}"
            else:
                rend_texto = f"-{rend_texto}"
            
            rend_item = QTableWidgetItem(rend_texto)
            rend_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            if rendimiento >= 0:
                rend_item.setForeground(QColor("#4CAF50"))
            else:
                rend_item.setForeground(QColor("#F44336"))
            
            self.tabla_portafolio.setItem(row, 8, rend_item)
            
            # Acciones
            if pos['cantidad_disponible'] > 0:
                acciones_widget = self._crear_boton_vender(pos)
                self.tabla_portafolio.setCellWidget(row, 9, acciones_widget)
        
        # Actualizar footer
        self.lbl_total_posiciones.setText(f"Total: {len(posiciones)} posiciones")
    
    def _crear_boton_vender(self, posicion: dict) -> QWidget:
        """Crea el botón de vender para una posición"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        btn_vender = QPushButton("Vender")
        btn_vender.setObjectName("venderButton")
        btn_vender.clicked.connect(
            lambda: self.vender_posicion_clicked.emit(posicion['id'])
        )
        
        layout.addWidget(btn_vender)
        
        return widget
    
    def aplicar_estilos(self):
        """Aplica estilos CSS"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            
            #pageTitle {
                font-size: 24px;
                font-weight: bold;
                color: #FF6B00;
            }
            
            #backButton {
                background-color: transparent;
                color: #AAAAAA;
                border: 2px solid #3D3D3D;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
            }
            
            #backButton:hover {
                border-color: #FF6B00;
                color: #FF6B00;
            }
            
            #metricCard {
                background-color: #2D2D2D;
                border-radius: 12px;
                border: 2px solid #3D3D3D;
            }
            
            #metricCardTitle {
                font-size: 13px;
                color: #AAAAAA;
                font-weight: bold;
            }
            
            #metricCardValue {
                font-size: 24px;
                font-weight: bold;
            }
            
            #metricCardSubtitle {
                font-size: 12px;
                color: #888888;
            }
            
            #sectionTitle {
                font-size: 18px;
                font-weight: bold;
                color: #FF6B00;
                padding: 10px 0;
            }
            
            #tablaPortafolio {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 8px;
                gridline-color: #3D3D3D;
            }
            
            #tablaPortafolio::item {
                padding: 10px;
                border-bottom: 1px solid #3D3D3D;
            }
            
            #tablaPortafolio::item:selected {
                background-color: #FF6B00;
            }
            
            #tablaPortafolio QHeaderView::section {
                background-color: #1E1E1E;
                color: #AAAAAA;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #FF6B00;
                font-weight: bold;
                font-size: 13px;
            }
            
            #venderButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            
            #venderButton:hover {
                background-color: #E57373;
            }
            
            #footerLabel {
                font-size: 13px;
                color: #AAAAAA;
                font-weight: bold;
            }
        """)