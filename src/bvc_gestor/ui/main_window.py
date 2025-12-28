# src/bvc_gestor/ui/main_window.py
"""
Ventana principal de la aplicación BVC-GESTOR
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QStatusBar, QMessageBox, QApplication, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QCloseEvent, QFont
import logging

from ..utils.logger import logger
from .sidebar import Sidebar
from .topbar import Topbar
from .statusbar import StatusBar
from .widgets.dashboard_widget import DashboardWidget
from ..core.app_state import AppState

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    # Señales
    app_closing = pyqtSignal()
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.widgets = {}  # Diccionario de widgets cargados
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
        logger.info("Ventana principal inicializada")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Configurar ventana principal
        self.setWindowTitle("BVC-GESTOR")
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Topbar (barra superior)
        self.topbar = Topbar(self.app_state)
        main_layout.addWidget(self.topbar)
        
        # Contenedor principal (sidebar + contenido)
        content_container = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_container.setLayout(content_layout)
        
        # Sidebar (barra lateral)
        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)
        
        # Área de contenido principal
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)
        self.content_area.setLayout(self.content_layout)
        content_layout.addWidget(self.content_area, 1)  # Factor de expansión 1
        
        # Stacked widget para cambiar entre vistas
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        
        # Agregar contenedor al layout principal
        main_layout.addWidget(content_container, 1)  # Factor de expansión 1
        
        # Statusbar (barra de estado)
        self.statusbar = StatusBar(self.app_state)
        self.setStatusBar(self.statusbar)
        
        # Cargar widgets iniciales
        self.load_initial_widgets()
        
        # Configurar tamaño inicial
        self.resize(1400, 800)
    
    def load_initial_widgets(self):
        """Cargar widgets iniciales"""
        # Dashboard
        self.dashboard_widget = DashboardWidget(self.app_state)
        self.stacked_widget.addWidget(self.dashboard_widget)
        self.widgets['dashboard'] = self.dashboard_widget
        
        # Placeholders para otros widgets (se cargarán dinámicamente)
        placeholder_widgets = ['clientes', 'ordenes', 'portafolio', 'reportes', 'config']
        
        for widget_name in placeholder_widgets:
            placeholder = QWidget()
            layout = QVBoxLayout()
            label = QLabel(f"Módulo {widget_name.capitalize()} - Cargando...")
            label.setStyleSheet("font-size: 18px; color: #6c757d;")
            layout.addWidget(label)
            placeholder.setLayout(layout)
            self.stacked_widget.addWidget(placeholder)
        
        # Mostrar dashboard por defecto
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        self.sidebar.set_active_button('dashboard')
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Sidebar signals
        self.sidebar.dashboard_clicked.connect(lambda: self.show_widget('dashboard'))
        self.sidebar.clientes_clicked.connect(lambda: self.show_widget('clientes'))
        self.sidebar.ordenes_clicked.connect(lambda: self.show_widget('ordenes'))
        self.sidebar.portafolio_clicked.connect(lambda: self.show_widget('portafolio'))
        self.sidebar.reportes_clicked.connect(lambda: self.show_widget('reportes'))
        self.sidebar.config_clicked.connect(lambda: self.show_widget('config'))
        
        # Topbar signals
        self.topbar.theme_toggled.connect(self.toggle_theme)
        self.topbar.refresh_clicked.connect(self.refresh_data)
        self.topbar.notifications_clicked.connect(self.show_notifications)
        self.topbar.settings_clicked.connect(lambda: self.show_widget('config'))
        self.topbar.profile_clicked.connect(self.show_profile)
        
        # Timer para actualizar statusbar
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.statusbar.update_status)
        self.status_timer.start(5000)  # Actualizar cada 5 segundos
    
    def apply_styles(self):
        """Aplicar estilos a la ventana"""
        # Configurar fuente
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)
        
        # Cargar hoja de estilos
        self.load_stylesheet()
    
    def load_stylesheet(self):
        """Cargar hoja de estilos QSS"""
        try:
            from .styles.dark import DARK_STYLESHEET
            from .styles.light import LIGHT_STYLESHEET
            
            if self.app_state.modo_oscuro:
                self.setStyleSheet(DARK_STYLESHEET)
            else:
                self.setStyleSheet(LIGHT_STYLESHEET)
                
            logger.info("Estilos cargados correctamente")
        except ImportError as e:
            logger.warning(f"No se pudieron cargar estilos: {e}")
            # Estilos básicos como fallback
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                }
            """)
    
    def show_widget(self, widget_name: str):
        """Mostrar widget específico"""
        logger.info(f"Cambiando a widget: {widget_name}")
        
        # Verificar si el widget ya está cargado
        if widget_name in self.widgets:
            self.stacked_widget.setCurrentWidget(self.widgets[widget_name])
            self.sidebar.set_active_button(widget_name)
            return
        
        # Cargar widget dinámicamente si no está cargado
        try:
            widget = self.load_widget(widget_name)
            if widget:
                # Reemplazar placeholder con widget real
                index = self.get_widget_index(widget_name)
                if index >= 0:
                    old_widget = self.stacked_widget.widget(index)
                    self.stacked_widget.removeWidget(old_widget)
                    self.stacked_widget.insertWidget(index, widget)
                    self.widgets[widget_name] = widget
                    self.stacked_widget.setCurrentWidget(widget)
                    self.sidebar.set_active_button(widget_name)
                    logger.info(f"Widget '{widget_name}' cargado dinámicamente")
        except Exception as e:
            logger.error(f"Error cargando widget {widget_name}: {e}")
            QMessageBox.warning(self, "Error", f"No se pudo cargar el módulo {widget_name}")
    
    def load_widget(self, widget_name: str):
        """Cargar widget específico"""
        from .widgets import (
            ClientesWidget, OrdenesWidget, PortafolioWidget,
            ReportesWidget, ConfigWidget
        )
        
        widgets_map = {
            'clientes': ClientesWidget,
            'ordenes': OrdenesWidget,
            'portafolio': PortafolioWidget,
            'reportes': ReportesWidget,
            'config': ConfigWidget,
        }
        
        widget_class = widgets_map.get(widget_name)
        if widget_class:
            return widget_class(self.app_state)
        
        return None
    
    def get_widget_index(self, widget_name: str) -> int:
        """Obtener índice del widget en stacked widget"""
        mapping = {
            'dashboard': 0,
            'clientes': 1,
            'ordenes': 2,
            'portafolio': 3,
            'reportes': 4,
            'config': 5
        }
        return mapping.get(widget_name, -1)
    
    def toggle_theme(self):
        """Cambiar entre tema oscuro y claro"""
        self.app_state.modo_oscuro = not self.app_state.modo_oscuro
        self.app_state.set_config('general', 'modo_oscuro', self.app_state.modo_oscuro)
        self.load_stylesheet()
        logger.info(f"Tema cambiado a: {'oscuro' if self.app_state.modo_oscuro else 'claro'}")
    
    def refresh_data(self):
        """Refrescar datos de la aplicación"""
        logger.info("Refrescando datos...")
        
        # Aquí iría la lógica para refrescar datos
        # Por ahora, solo actualizamos el dashboard si está visible
        current_widget = self.stacked_widget.currentWidget()
        if current_widget == self.dashboard_widget:
            self.dashboard_widget.refresh_data()
        
        self.statusbar.show_message("Datos actualizados", 3000)
    
    def show_notifications(self):
        """Mostrar notificaciones"""
        # Placeholder - implementaremos más tarde
        QMessageBox.information(self, "Notificaciones", "Sistema de notificaciones en desarrollo")
    
    def show_profile(self):
        """Mostrar perfil de usuario"""
        # Placeholder - implementaremos más tarde
        QMessageBox.information(self, "Perfil", "Perfil de usuario en desarrollo")
    
    def closeEvent(self, event: QCloseEvent):
        """Manejar cierre de la aplicación"""
        if self.app_state.cambios_pendientes:
            reply = QMessageBox.question(
                self, "Cambios pendientes",
                "Hay cambios sin guardar. ¿Está seguro de que desea salir?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                # Guardar cambios pendientes
                self.save_pending_changes()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                # Descartar cambios
                event.accept()
            else:
                # Cancelar cierre
                event.ignore()
                return
        
        # Emitir señal de cierre
        self.app_closing.emit()
        
        # Limpiar recursos
        self.cleanup()
        
        # Aceptar evento de cierre
        event.accept()
        logger.info("Aplicación cerrada")
    
    def save_pending_changes(self):
        """Guardar cambios pendientes"""
        logger.info("Guardando cambios pendientes...")
        # Aquí iría la lógica para guardar cambios
        self.app_state.guardar_configuracion()
        self.statusbar.show_message("Cambios guardados", 3000)
    
    def cleanup(self):
        """Limpiar recursos antes de cerrar"""
        self.status_timer.stop()
        
        # Limpiar widgets
        for widget_name, widget in self.widgets.items():
            if hasattr(widget, 'cleanup'):
                widget.cleanup()
        
        # Limpiar estado
        self.app_state.limpiar_estado()
    
    def showEvent(self, event):
        """Manejar evento de mostrar ventana"""
        super().showEvent(event)
        logger.info("Ventana principal mostrada")