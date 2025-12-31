# src/bvc_gestor/ui/widgets/dashboard_widget.py
"""
Widget del Dashboard principal - MIGRADO
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
from ..styles import get_style_manager  # Importar StyleManager

class MetricCard(QFrame):
    """Tarjeta para métricas del dashboard"""
    
    def __init__(self, title: str, value: str, icon: str = "", color: str = "primary"):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color  # Ahora es nombre de color, no valor hex
        self.style_manager = get_style_manager()  # StyleManager
        self.setObjectName("metric-card")  # ID para CSS
        self.setProperty("data-color", color)  # Atributo data
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
        title_label.setObjectName("metric-title")  # ID para CSS
        layout.addWidget(title_label)
        
        # Valor
        value_label = QLabel(self.value)
        value_label.setObjectName("metric-value")  # ID para CSS
        value_label.setProperty("data-color", self.color)  # Atributo data
        layout.addWidget(value_label)
    
    def apply_styles(self):
        """Aplicar estilos usando StyleManager"""
        self.style_manager.apply_stylesheet(self)
    
    def on_theme_changed(self):
        """Manejar cambio de tema"""
        self.apply_styles()

class DashboardWidget(QWidget):
    """Widget principal del dashboard - MIGRADO"""
    
    refresh_requested = pyqtSignal()
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.style_manager = get_style_manager()  # StyleManager
        self.db_session = None
        self.metric_cards = []
        self.setObjectName("dashboard-widget")  # ID para CSS
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()  # Aplicar estilos
        logger.info("DashboardWidget inicializado")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # Título
        title_label = QLabel("📊 Dashboard")
        title_label.setObjectName("dashboard-title")  # ID para CSS
        layout.addWidget(title_label)
        
        # Área desplazable
        scroll_area = QScrollArea()
        scroll_area.setObjectName("dashboard-scroll")  # ID para CSS
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        scroll_widget.setObjectName("dashboard-content")  # ID para CSS
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
        activity_title.setObjectName("activity-title")  # ID para CSS
        layout.addWidget(activity_title)
        
        # Frame para actividad
        self.activity_frame = QFrame()
        self.activity_frame.setObjectName("activity-frame")  # ID para CSS
        self.activity_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        
        self.activity_layout = QVBoxLayout()
        self.activity_layout.setSpacing(10)
        self.activity_frame.setLayout(self.activity_layout)
        
        # Mensaje de carga inicial
        loading_label = QLabel("Cargando actividad...")
        loading_label.setObjectName("activity-loading")  # ID para CSS
        self.activity_layout.addWidget(loading_label)
        
        layout.addWidget(self.activity_frame)
    
    def apply_styles(self):
        """Aplicar estilos usando StyleManager"""
        self.style_manager.apply_stylesheet(self)
        # Aplicar estilos a todas las tarjetas de métricas
        for card in self.metric_cards:
            if hasattr(card, 'apply_styles'):
                card.apply_styles()
    
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
            
            # Métricas de ejemplo
            capital_total = 1500000.00  # $1.5M
            rendimiento_mensual = 2.4   # 2.4%
            
            # Definir métricas (ahora con nombres de color)
            metrics = [
                ("👥 Clientes Activos", f"{clientes_activos}/{total_clientes}", "primary"),
                ("💼 Cuentas Activas", f"{cuentas_activas}/{total_cuentas}", "success"),
                ("📋 Órdenes Pendientes", str(ordenes_pendientes), "warning"),
                ("📈 Capital Total", f"${capital_total:,.2f}", "info"),
                ("📊 Rendimiento Mensual", f"{rendimiento_mensual}%", 
                "profit" if rendimiento_mensual >= 0 else "loss"),
                ("🔄 Órdenes Hoy", str(ordenes_hoy), "secondary"),
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
        
        # Aplicar estilos a las nuevas tarjetas
        self.apply_styles()
    
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
            activity_label.setObjectName("activity-item")  # ID para CSS
            self.activity_layout.addWidget(activity_label)
        
        # Si no hay actividad
        if not activities:
            no_activity = QLabel("No hay actividad reciente")
            no_activity.setObjectName("activity-empty")  # ID para CSS
            self.activity_layout.addWidget(no_activity)
    
    def show_placeholder_metrics(self):
        """Mostrar métricas de placeholder en caso de error"""
        metrics = [
            ("👥 Clientes", "Cargando...", "primary"),
            ("💼 Cuentas", "Cargando...", "success"),
            ("📋 Órdenes", "Cargando...", "warning"),
            ("📈 Capital", "Cargando...", "info"),
            ("📊 Rendimiento", "Cargando...", "secondary"),
            ("🔄 Actividad", "Cargando...", "secondary"),
        ]
        self.update_metric_cards(metrics)
    
    def on_theme_changed(self, dark_mode: bool):
        """Manejar cambio de tema"""
        self.apply_styles()
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.update_timer:
            self.update_timer.stop()
        
        if self.db_session:
            self.db_session.close()