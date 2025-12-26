# src/bvc_gestor/ui/widgets/dashboard_widget.py
"""
Widget del Dashboard principal
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter, QBrush
import logging
from datetime import datetime

from ...core.app_state import AppState
from ...utils.logger import logger
from ...database.repositories import RepositoryFactory
from ...database.engine import get_database

class MetricCard(QFrame):
    """Tarjeta para métricas del dashboard"""
    
    def __init__(self, title: str, value: str, icon: str = "", color: str = "#2c5aa0"):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz"""
        self.setFixedHeight(100)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        self.setLayout(layout)
        
        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #6c757d;
                font-size: 14px;
                font-weight: 500;
            }}
        """)
        layout.addWidget(title_label)
        
        # Valor
        value_label = QLabel(self.value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 24px;
                font-weight: bold;
                margin-top: 5px;
            }}
        """)
        layout.addWidget(value_label)
        
        # Estilo del frame
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }}
            QFrame:hover {{
                border: 2px solid {self.color};
            }}
        """)

class DashboardWidget(QWidget):
    """Widget principal del dashboard"""
    
    refresh_requested = pyqtSignal()
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.db_session = None
        self.metric_cards = []
        self.setup_ui()
        self.setup_connections()
        logger.info("DashboardWidget inicializado")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # Título
        title_label = QLabel("📊 Dashboard")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c5aa0;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Área desplazable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        scroll_widget.setLayout(scroll_layout)
        
        # Grid de métricas
        self.metrics_grid = QGridLayout()
        self.metrics_grid.setSpacing(15)
        scroll_layout.addLayout(self.metrics_grid)
        
        # Sección de actividad reciente
        self.setup_recent_activity_section(scroll_layout)
        
        # Espaciador
        scroll_layout.addStretch(1)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def setup_recent_activity_section(self, layout: QVBoxLayout):
        """Configurar sección de actividad reciente"""
        # Título de sección
        activity_title = QLabel("⚡ Actividad Reciente")
        activity_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #495057;
                margin-top: 20px;
            }
        """)
        layout.addWidget(activity_title)
        
        # Frame para actividad
        self.activity_frame = QFrame()
        self.activity_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.activity_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
                padding: 15px;
            }
        """)
        
        self.activity_layout = QVBoxLayout()
        self.activity_layout.setSpacing(10)
        self.activity_frame.setLayout(self.activity_layout)
        
        # Mensaje de carga inicial
        loading_label = QLabel("Cargando actividad...")
        loading_label.setStyleSheet("color: #6c757d;")
        self.activity_layout.addWidget(loading_label)
        
        layout.addWidget(self.activity_frame)
    
    def setup_connections(self):
        """Configurar conexiones"""
        # Timer para actualizar datos periódicamente
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(30000)  # Actualizar cada 30 segundos
    
    def refresh_data(self):
        """Refrescar datos del dashboard"""
        logger.info("Refrescando datos del dashboard")
        
        try:
            # Obtener sesión de base de datos
            if self.db_session is None:
                self.db_session = get_database().get_session()
            
            # Obtener repositorios
            cliente_repo = RepositoryFactory.get_repository(self.db_session, 'cliente')
            cuenta_repo = RepositoryFactory.get_repository(self.db_session, 'cuenta')
            orden_repo = RepositoryFactory.get_repository(self.db_session, 'orden')
            
            # Calcular métricas
            total_clientes = cliente_repo.count()
            clientes_activos = len(cliente_repo.get_active_clients())
            total_cuentas = cuenta_repo.count()
            cuentas_activas = len(cuenta_repo.get_active_accounts())
            ordenes_pendientes = len(orden_repo.get_pending_orders())
            ordenes_hoy = len(orden_repo.get_today_orders())
            
            # Métricas de ejemplo (serían calculadas de datos reales)
            capital_total = 1500000.00  # $1.5M
            rendimiento_mensual = 2.4   # 2.4%
            
            # Definir métricas
            metrics = [
                ("👥 Clientes Activos", f"{clientes_activos}/{total_clientes}", "#2c5aa0"),
                ("💼 Cuentas Activas", f"{cuentas_activas}/{total_cuentas}", "#28a745"),
                ("📋 Órdenes Pendientes", str(ordenes_pendientes), "#ffc107"),
                ("📈 Capital Total", f"${capital_total:,.2f}", "#17a2b8"),
                ("📊 Rendimiento Mensual", f"{rendimiento_mensual}%", rendimiento_mensual >= 0 and "#198754" or "#dc3545"),
                ("🔄 Órdenes Hoy", str(ordenes_hoy), "#6f42c1"),
            ]
            
            # Actualizar tarjetas de métricas
            self.update_metric_cards(metrics)
            
            # Actualizar actividad reciente
            self.update_recent_activity()
            
            logger.info("Datos del dashboard actualizados")
            
        except Exception as e:
            logger.error(f"Error refrescando dashboard: {e}")
            # Mostrar métricas de placeholder en caso de error
            self.show_placeholder_metrics()
    
    def update_metric_cards(self, metrics: list):
        """Actualizar tarjetas de métricas"""
        # Limpiar layout existente
        while self.metrics_grid.count():
            item = self.metrics_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.metric_cards.clear()
        
        # Crear nuevas tarjetas
        for i, (title, value, color) in enumerate(metrics):
            row = i // 3
            col = i % 3
            
            card = MetricCard(title, value, color=color)
            self.metrics_grid.addWidget(card, row, col)
            self.metric_cards.append(card)
    
    def update_recent_activity(self):
        """Actualizar actividad reciente"""
        # Limpiar actividad anterior
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Actividad de ejemplo
        activities = [
            "15:30 Compra BNC @1.25 (Cliente: María González)",
            "14:45 Venta EMPV @3.40 (Cliente: Carlos Pérez)",
            "13:20 Depósito $10,000 (Cliente: Ana Rodríguez)",
            "11:15 Nueva orden pendiente BNV @2.10",
            "10:30 Actualización de precios completada",
            "09:45 Backup automático ejecutado"
        ]
        
        for activity in activities[:5]:  # Mostrar solo las 5 más recientes
            activity_label = QLabel(f"• {activity}")
            activity_label.setStyleSheet("""
                QLabel {
                    color: #495057;
                    font-size: 14px;
                    padding: 5px 0;
                }
            """)
            self.activity_layout.addWidget(activity_label)
        
        # Si no hay actividad
        if not activities:
            no_activity = QLabel("No hay actividad reciente")
            no_activity.setStyleSheet("color: #6c757d; font-style: italic;")
            self.activity_layout.addWidget(no_activity)
    
    def show_placeholder_metrics(self):
        """Mostrar métricas de placeholder en caso de error"""
        metrics = [
            ("👥 Clientes", "Cargando...", "#2c5aa0"),
            ("💼 Cuentas", "Cargando...", "#28a745"),
            ("📋 Órdenes", "Cargando...", "#ffc107"),
            ("📈 Capital", "Cargando...", "#17a2b8"),
            ("📊 Rendimiento", "Cargando...", "#198754"),
            ("🔄 Actividad", "Cargando...", "#6f42c1"),
        ]
        self.update_metric_cards(metrics)
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.update_timer:
            self.update_timer.stop()
        
        if self.db_session:
            self.db_session.close()