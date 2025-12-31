# src/bvc_gestor/ui/main_window.py
"""
Ventana principal de la aplicación BVC-GESTOR
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QStatusBar, QMessageBox, QApplication, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QCloseEvent, QFont, QIcon
import logging
import sys

from ..utils.logger import logger
from .sidebar import Sidebar
from .topbar import Topbar
from .statusbar import StatusBar
from .widgets.dashboard_widget import DashboardWidget
from .widgets.clientes_widget import ClientesWidget
from .widgets.ordenes_widget import OrdenesWidget
# from .widgets.portafolio_widget import PortafolioWidget
# from .widgets.reportes_widget import ReportesWidget
# from .widgets.config_widget import ConfigWidget
from ..core.app_state import AppState

# Importar el StyleManager
from .styles import get_style_manager


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    # Señales
    app_closing = pyqtSignal()
    theme_changed = pyqtSignal(bool)  # True = oscuro, False = claro
    
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self.widgets = {}  # Diccionario de widgets cargados
        
        # Obtener StyleManager
        self.style_manager = get_style_manager()
        
        # Sincronizar StyleManager con el estado inicial
        self.style_manager.update_theme(self.app_state.modo_oscuro)
        
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
        
        logger.info("Ventana principal inicializada")
        logger.info(f"Tema inicial: {'oscuro' if self.app_state.modo_oscuro else 'claro'}")
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Configurar ventana principal
        self.setWindowTitle("BVC-GESTOR")
        
        # Configurar icono de la ventana (si existe)
        try:
            icon_path = sys.path[0] + "/src/bvc_gestor/assets/icons/app-icon.png"
            self.setWindowIcon(QIcon(icon_path))
        except:
            pass  # Si no hay icono, continuar sin él
        
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
        self.sidebar = Sidebar(self.app_state)
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
        
        # Centrar ventana
        self.center_window()
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def load_initial_widgets(self):
        """Cargar widgets iniciales"""
        # Dashboard
        self.dashboard_widget = DashboardWidget(self.app_state)
        self.stacked_widget.addWidget(self.dashboard_widget)
        self.widgets['dashboard'] = self.dashboard_widget
        
        # Clientes
        self.clientes_widget = ClientesWidget(self.app_state)
        self.stacked_widget.addWidget(self.clientes_widget)
        self.widgets['clientes'] = self.clientes_widget
        
        # Órdenes
        self.ordenes_widget = OrdenesWidget(self.app_state)
        self.stacked_widget.addWidget(self.ordenes_widget)
        self.widgets['ordenes'] = self.ordenes_widget
        
        # Crear placeholders para otros módulos
        module_configs = [
            ('portafolio', '📈 Portafolio'),
            ('reportes', '📋 Reportes'),
            ('config', '⚙️ Configuración'),
        ]
        
        for module_name, display_name in module_configs:
            placeholder = self.create_placeholder_widget(display_name)
            self.stacked_widget.addWidget(placeholder)
            self.widgets[module_name] = placeholder
        
        # Mostrar dashboard por defecto
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        self.sidebar.set_active_button('dashboard')

    def create_placeholder_widget(self, module_name: str) -> QWidget:
        """Crear widget placeholder para módulos no cargados"""
        from PyQt6.QtWidgets import QVBoxLayout, QLabel
        from PyQt6.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel(f"{module_name} - Cargando...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #6c757d;
                margin-top: 100px;
            }
        """)
        
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget
    
    def create_error_widget(self, module_name: str, error: Exception):
        """Crear widget de error"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        error_label = QLabel(f"❌ Error cargando {module_name}:\n\n{str(error)}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setProperty("class", "error-label")  # Clase CSS
        error_label.setWordWrap(True)
        
        retry_button = QPushButton("🔄 Reintentar")
        retry_button.setProperty("class", "danger")  # Clase CSS
        retry_button.clicked.connect(lambda: self.retry_load_module(module_name))
        
        layout.addStretch()
        layout.addWidget(error_label)
        layout.addWidget(retry_button, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        return widget
    
    def retry_load_module(self, module_name: str):
        """Reintentar cargar un módulo"""
        logger.info(f"Reintentando cargar módulo: {module_name}")
        self.show_widget(module_name)
    
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
        
        # Statusbar signals
        # Note: theme_toggle_requested signal not available in StatusBar
        # Theme toggling is handled via Topbar instead
        
        # Timer para actualizar statusbar
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.statusbar.update_status)
        self.status_timer.start(5000)  # Actualizar cada 5 segundos
        
        # Conectar señal de cambio de tema
        self.theme_changed.connect(self.on_theme_changed)
    
    def apply_styles(self):
        """Aplicar estilos a la ventana"""
        # Configurar fuente
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)
        
        # Aplicar estilos usando StyleManager
        self.apply_stylesheet()
    
    def apply_stylesheet(self):
        """Aplicar hoja de estilos actual"""
        try:
            # Obtener estilos del tema actual
            stylesheet = self.style_manager.get_stylesheet()
            
            # Aplicar a toda la ventana
            self.setStyleSheet(stylesheet)
            
            # Aplicar también a widgets hijos importantes
            if hasattr(self, 'sidebar'):
                self.sidebar.setStyleSheet(stylesheet)
            if hasattr(self, 'topbar'):
                self.topbar.setStyleSheet(stylesheet)
            
            logger.debug(f"Estilos aplicados (tema: {self.style_manager.current_theme})")
            
        except Exception as e:
            logger.error(f"Error aplicando estilos: {e}")
            # Fallback mínimo
            self.setStyleSheet("")
    
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
            widget = self.load_widget_dynamic(widget_name)
            if widget:
                # Reemplazar placeholder con widget real
                index = self.get_widget_index(widget_name)
                if index >= 0:
                    # Remover placeholder
                    old_widget = self.stacked_widget.widget(index)
                    self.stacked_widget.removeWidget(old_widget)
                    old_widget.deleteLater()
                    
                    # Insertar widget real
                    self.stacked_widget.insertWidget(index, widget)
                    self.widgets[widget_name] = widget
                    
                    # Mostrar y configurar
                    self.stacked_widget.setCurrentWidget(widget)
                    self.sidebar.set_active_button(widget_name)
                    
                    # Aplicar estilos al nuevo widget
                    self.apply_stylesheet_to_widget(widget)
                    
                    logger.info(f"✅ Widget '{widget_name}' cargado dinámicamente")
        except Exception as e:
            logger.error(f"❌ Error cargando widget {widget_name}: {e}")
            
            # Mostrar widget de error
            error_widget = self.create_error_widget(widget_name, e)
            index = self.get_widget_index(widget_name)
            if index >= 0:
                old_widget = self.stacked_widget.widget(index)
                self.stacked_widget.removeWidget(old_widget)
                self.stacked_widget.insertWidget(index, error_widget)
                self.stacked_widget.setCurrentWidget(error_widget)
                self.sidebar.set_active_button(widget_name)
            
            QMessageBox.warning(
                self, 
                "Error", 
                f"No se pudo cargar el módulo {widget_name}:\n\n{str(e)}"
            )
    
    def load_widget_dynamic(self, widget_name: str):
        """Cargar widget específico dinámicamente"""
        if widget_name == 'dashboard':
            from .widgets.dashboard_widget import DashboardWidget
            return DashboardWidget(self.app_state)
        elif widget_name == 'clientes':
            from .widgets.clientes_widget import ClientesWidget
            return ClientesWidget(self.app_state)
        elif widget_name == 'ordenes':
            from .widgets.ordenes_widget import OrdenesWidget
            return OrdenesWidget(self.app_state)
        elif widget_name == 'portafolio':
            from .widgets.portafolio_widget import PortafolioWidget
            return PortafolioWidget(self.app_state)
        elif widget_name == 'reportes':
            from .widgets.reportes_widget import ReportesWidget
            return ReportesWidget(self.app_state)
        elif widget_name == 'config':
            from .widgets.config_widget import ConfigWidget
            return ConfigWidget(self.app_state)
        return None
    
    def apply_stylesheet_to_widget(self, widget):
        """Aplicar hoja de estilos a un widget específico"""
        try:
            stylesheet = self.style_manager.get_stylesheet()
            widget.setStyleSheet(stylesheet)
            
            # Aplicar recursivamente a hijos
            for child in widget.findChildren(QWidget):
                child.setStyleSheet(stylesheet)
        except Exception as e:
            logger.error(f"Error aplicando estilos a widget: {e}")
    
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
        try:
            # Calcular nuevo tema
            nuevo_modo_oscuro = not self.app_state.modo_oscuro
            
            # Actualizar estado de la aplicación
            self.app_state.modo_oscuro = nuevo_modo_oscuro
            self.app_state.set_config('general', 'modo_oscuro', nuevo_modo_oscuro)
            
            # Actualizar StyleManager
            self.style_manager.update_theme(nuevo_modo_oscuro)
            
            # Actualizar Topbar (para cambiar icono)
            if hasattr(self, 'topbar'):
                self.topbar.update_theme_icon()
            
            # Actualizar Statusbar
            # if hasattr(self, 'statusbar'):
            #     self.statusbar.update_theme_indicator()
            
            # Recargar estilos
            self.apply_stylesheet()
            
            # Notificar a widgets cargados
            self.theme_changed.emit(nuevo_modo_oscuro)
            
            # Actualizar widgets individualmente
            for widget_name, widget in self.widgets.items():
                if hasattr(widget, 'on_theme_changed'):
                    try:
                        widget.on_theme_changed(nuevo_modo_oscuro)
                    except Exception as e:
                        logger.error(f"Error actualizando tema en {widget_name}: {e}")
            
            logger.info(f"🎨 Tema cambiado a: {'oscuro' if nuevo_modo_oscuro else 'claro'}")
            
            # Mostrar mensaje en statusbar
            tema_str = "oscuro" if nuevo_modo_oscuro else "claro"
            self.statusbar.show_message(f"Tema cambiado a {tema_str}", 2000)
            
        except Exception as e:
            logger.error(f"❌ Error cambiando tema: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo cambiar el tema:\n\n{str(e)}")
    
    def on_theme_changed(self, dark_mode: bool):
        """Manejar cambio de tema (señal)"""
        # Este método puede ser extendido para lógica adicional
        pass
    
    def refresh_data(self):
        """Refrescar datos de la aplicación"""
        logger.info("Refrescando datos...")
        
        try:
            # Refrescar widget actual
            current_widget = self.stacked_widget.currentWidget()
            if hasattr(current_widget, 'refresh_data'):
                current_widget.refresh_data()
            
            # Refrescar dashboard si está cargado
            if 'dashboard' in self.widgets and hasattr(self.widgets['dashboard'], 'refresh_data'):
                self.widgets['dashboard'].refresh_data()
            
            self.statusbar.show_message("✅ Datos actualizados", 3000)
            
        except Exception as e:
            logger.error(f"Error refrescando datos: {e}")
            self.statusbar.show_message(f"❌ Error actualizando datos", 3000)
    
    def show_notifications(self):
        """Mostrar notificaciones"""
        # TODO: Implementar sistema de notificaciones
        QMessageBox.information(
            self, 
            "Notificaciones", 
            "Sistema de notificaciones en desarrollo.\n\n"
            "Próximamente: Alertas de órdenes ejecutadas, precios límite, etc."
        )
    
    def show_profile(self):
        """Mostrar perfil de usuario"""
        # TODO: Implementar perfil de usuario
        QMessageBox.information(
            self,
            "Perfil de Usuario",
            "Perfil de usuario en desarrollo.\n\n"
            "Próximamente: Información del usuario, preferencias, etc."
        )
    
    def closeEvent(self, event: QCloseEvent):
        """Manejar cierre de la aplicación"""
        # Verificar cambios pendientes
        if self.app_state.cambios_pendientes:
            reply = QMessageBox.question(
                self, 
                "Cambios pendientes",
                "Hay cambios sin guardar. ¿Está seguro de que desea salir?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                # Guardar cambios pendientes
                if self.save_pending_changes():
                    event.accept()
                else:
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Discard:
                # Descartar cambios
                event.accept()
            else:
                # Cancelar cierre
                event.ignore()
                return
        
        # Confirmar cierre si no hay cambios pendientes
        reply = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Está seguro de que desea salir de BVC-GESTOR?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            event.ignore()
            return
        
        # Emitir señal de cierre
        self.app_closing.emit()
        
        # Limpiar recursos
        self.cleanup()
        
        # Aceptar evento de cierre
        event.accept()
        logger.info("Aplicación cerrada")
    
    def save_pending_changes(self) -> bool:
        """Guardar cambios pendientes"""
        try:
            logger.info("Guardando cambios pendientes...")
            
            # Guardar configuración
            success = self.app_state.guardar_configuracion()
            
            # Guardar datos de widgets si tienen cambios
            for widget_name, widget in self.widgets.items():
                if hasattr(widget, 'save_changes'):
                    try:
                        widget_success = widget.save_changes()
                        if widget_success:
                            logger.debug(f"Cambios guardados en {widget_name}")
                    except Exception as e:
                        logger.error(f"Error guardando cambios en {widget_name}: {e}")
            
            if success:
                self.statusbar.show_message("✅ Cambios guardados", 3000)
                self.app_state.cambios_pendientes = False
            else:
                self.statusbar.show_message("❌ Error guardando cambios", 3000)
            
            return success
            
        except Exception as e:
            logger.error(f"Error guardando cambios: {e}")
            self.statusbar.show_message(f"❌ Error: {str(e)[:50]}...", 3000)
            return False
    
    def cleanup(self):
        """Limpiar recursos antes de cerrar"""
        # Detener timers
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        
        # Limpiar widgets
        for widget_name, widget in self.widgets.items():
            if hasattr(widget, 'cleanup'):
                try:
                    widget.cleanup()
                    logger.debug(f"Recursos liberados en {widget_name}")
                except Exception as e:
                    logger.error(f"Error limpiando {widget_name}: {e}")
        
        # Limpiar estado
        self.app_state.limpiar_estado()
        
        # Cerrar conexiones de base de datos si es necesario
        try:
            from ..database.engine import get_database
            db = get_database()
            if hasattr(db, 'close_all'):
                db.close_all()
        except:
            pass
        
        logger.info("Recursos limpiados")
    
    def showEvent(self, event):
        """Manejar evento de mostrar ventana"""
        super().showEvent(event)
        
        # Actualizar estado
        self.app_state.aplicacion_iniciada = True
        
        # Actualizar UI
        if hasattr(self, 'statusbar'):
            self.statusbar.update_status()
        
        logger.info("Ventana principal mostrada")
    
    def keyPressEvent(self, event):
        """Manejar eventos de teclado"""
        # Atajos globales
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_N:
                self.show_widget('clientes')  # Nuevo cliente
                event.accept()
                return
            elif event.key() == Qt.Key.Key_O:
                self.show_widget('ordenes')  # Nueva orden
                event.accept()
                return
            elif event.key() == Qt.Key.Key_R:
                self.refresh_data()  # Refrescar
                event.accept()
                return
            elif event.key() == Qt.Key.Key_T:
                self.toggle_theme()  # Cambiar tema
                event.accept()
                return
        
        # F5 para refrescar
        elif event.key() == Qt.Key.Key_F5:
            self.refresh_data()
            event.accept()
            return
        
        # Escape para salir
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return
        
        super().keyPressEvent(event)