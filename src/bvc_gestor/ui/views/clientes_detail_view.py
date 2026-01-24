# src/bvc_gestor/ui/views/clientes_detail_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QGridLayout, QLineEdit, 
    QComboBox, QPushButton, QDateEdit, QRadioButton,
    QTextEdit, QCheckBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QDate
from ..components import BancoItem, CuentaBursatilItem


class ClienteDetalleView(QWidget):
    """Vista de detalle para formulario de cliente"""
    back_clicked = pyqtSignal()
    documento_agregado = pyqtSignal(dict)  # Señal para documentos

    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Barra de herramientas
        self._setup_toolbar()

        # 2. Área de contenido con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scroll_area")
        
        container = QWidget()
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(20, 0, 0, 0)
        self.content_layout.setSpacing(20)

        # 3. Secciones del formulario
        self._setup_sections()
        scroll.setWidget(container)
        self.main_layout.addWidget(scroll)

    def _setup_toolbar(self):
        """Configurar barra de herramientas"""
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(70)
        layout = QHBoxLayout(toolbar)
        
        btn_back = QPushButton("← Volver")
        btn_back.setFlat(True)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.back_clicked.emit)
        
        self.lbl_title = QLabel("Inversor")        
        self.lbl_title.setObjectName("header_title")
        
        self.btn_save = QPushButton("Guardar")
        self.btn_save.setObjectName("primaryButton")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setFixedWidth(100)
        
        self.btn_delete = QPushButton("Borrar")
        self.btn_delete.setObjectName("secondaryButton")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setFixedWidth(100)
        
        layout.addWidget(btn_back)
        layout.addSpacing(20)
        layout.addWidget(self.lbl_title)
        layout.addStretch()
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_save)
        self.main_layout.addWidget(toolbar)

    def _create_card(self, title):
        """Crear card con título"""
        card = QFrame()
        card.setObjectName("Card")
        layout = QGridLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        title_lbl = QLabel(title.upper())
        title_lbl.setObjectName("card_title")
        layout.addWidget(title_lbl, 0, 0, 1, 4)
        
        return card, layout

    def _setup_sections(self):
        """Configurar secciones del formulario"""
        # Sección 1: Identificación
        self._setup_identificacion()
        
        # Sección 2: Bancaria
        self._setup_bancaria()
        
        # Sección 3: Bursátil
        self._setup_bursatil()
        
        # Sección 4: Documentos (NUEVA)
        self._setup_documentos()

    def _setup_identificacion(self):
        """Configurar sección de identificación"""
        card, layout = self._create_card("Identificación")
        
        # Campos básicos
        self.txt_nombre = self._add_input(layout, "Nombre/Razón Social", "Ingrese nombre completo", 1, 0)
        self.txt_rif = self._add_input(layout, "RIF/Cédula", "J-12312345-1", 2, 0)
        self.cmb_tipo = self._add_combo(layout, "Tipo de Inversor", 2, 1)
        #self.date_rif = self._add_date(layout, "Vencimiento RIF", 2, 2)
        self.txt_email = self._add_input(layout, "Correo", "correo@dominio.com", 3, 0)
        self.txt_telefono = self._add_input(layout, "Teléfono", "0414-1234567", 3, 1)
        self.txt_direccion = self._add_text_area(layout, "Dirección Fiscal", "Calle, municipio, ciudad", 4, 0, 2)
        self.txt_ciudad = self._add_input(layout, "Ciudad/Estado", "Ciudad, Estado", 5, 0)
        
        # Perfil de riesgo (del modelo pero comentado)
        # self.cmb_perfil = self._add_combo(layout, "Perfil de Riesgo", 5, 1)
        
        self.content_layout.addWidget(card)

    def _setup_bancaria(self):
        """Configurar sección bancaria dinámica"""
        card = self._create_dynamic_section(
            title="Información Bancaria",
            widget_class=BancoItem,
            data_attr='bancos',
            add_method='add_cuenta_banco',
            layout_attr='bancos_layout',
            btn_text="+ Agregar cuenta bancaria"
        )
        self.content_layout.addWidget(card)

    def _setup_bursatil(self):
        """Configurar sección bursátil dinámica"""
        card = self._create_dynamic_section(
            title="Cuenta Bursátil",
            widget_class=CuentaBursatilItem,
            data_attr='corredores',
            add_method='add_cuenta_bursatil',
            layout_attr='bursatil_layout',
            btn_text="+ Agregar cuenta bursátil"
        )
        self.content_layout.addWidget(card)

    def _setup_documentos(self):
        """Configurar sección de documentos (NUEVA)"""
        card, layout = self._create_card("Documentos")
        
        # Contenedor para documentos
        docs_widget = QWidget()
        docs_widget.setObjectName("FormQWidget")
        self.docs_layout = QVBoxLayout(docs_widget)
        self.docs_layout.setContentsMargins(0, 0, 0, 0)
        self.docs_layout.setSpacing(10)
        
        # Botón para subir documentos
        btn_add_doc = QPushButton("📎 Subir Documento")
        btn_add_doc.setObjectName("addRowButton")
        btn_add_doc.clicked.connect(self._agregar_documento)
        
        layout.addWidget(docs_widget, 1, 0, 1, 4)
        layout.addWidget(btn_add_doc, 2, 0, 1, 4)
        
        self.content_layout.addWidget(card)

    def _create_dynamic_section(self, title, widget_class, data_attr, add_method, layout_attr, btn_text):
        """Crear sección dinámica genérica"""
        card, layout = self._create_card(title)
        
        # Contenedor para widgets
        container = QWidget()
        container.setObjectName("FormQWidget")
        dynamic_layout = QVBoxLayout(container)
        dynamic_layout.setContentsMargins(0, 0, 0, 0)
        dynamic_layout.setSpacing(10)
        
        # Guardar referencia
        setattr(self, layout_attr, dynamic_layout)
        
        # Widget inicial
        getattr(self, add_method)()
        
        # Botón para agregar
        btn_add = QPushButton(btn_text)
        btn_add.setObjectName("addRowButton")
        btn_add.clicked.connect(getattr(self, add_method))
        
        layout.addWidget(container, 1, 0, 1, 4)
        layout.addWidget(btn_add, 2, 0, 1, 4)
        
        return card

    # ============= MÉTODOS PÚBLICOS =============

    def add_cuenta_banco(self, banco_id=None, numero="", principal=False, tipo="Corriente"):
        """Agregar widget de cuenta bancaria"""
        item = BancoItem(getattr(self, 'bancos', []))
        
        if banco_id and hasattr(self, 'bancos'):
            item.set_banco(banco_id)
        
        if numero:
            item.set_numero(numero)
        
        if tipo:
            item.set_tipo(tipo)
        
        if principal:
            item.set_principal(True)
            
        item.removed.connect(lambda: self._remove_item(item))
        self.bancos_layout.addWidget(item)
        return item
    
    def add_cuenta_bursatil(self, casa_id=None, cuenta="", tipo="Individual", default=False):
        """Agregar widget de cuenta bursátil"""
        item = CuentaBursatilItem(getattr(self, 'corredores', []))
        
        if casa_id and hasattr(self, 'corredores'):
            item.set_casa(casa_id)
        
        if cuenta:
            item.set_cuenta(cuenta)
        
        if tipo:
            item.set_tipo(tipo)
        
        item.set_default(default)
            
        item.removed.connect(lambda: self._remove_item(item))
        self.bursatil_layout.addWidget(item)
        return item
    
    def add_documento(self, tipo_doc="", nombre="", ruta=""):
        """Agregar documento a la lista"""
        widget = QWidget()
        widget.setObjectName("RowItem")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        lbl_tipo = QLabel(tipo_doc if tipo_doc else "Documento")
        lbl_tipo.setObjectName("document_label")
        
        lbl_nombre = QLabel(nombre if nombre else "Sin nombre")
        lbl_nombre.setObjectName("document_name")
        
        chk_verificado = QCheckBox("Verificado")
        chk_verificado.setChecked(False)
        chk_verificado.setObjectName("document_check")
        
        btn_ver = QPushButton("👁️")
        btn_ver.setObjectName("iconButton")
        btn_ver.setToolTip("Ver documento")
        
        btn_elim = QPushButton("🗑")
        btn_elim.setObjectName("delete_btn")
        btn_elim.setToolTip("Eliminar documento")
        
        layout.addWidget(lbl_tipo, 30)
        layout.addWidget(lbl_nombre, 50)
        layout.addWidget(chk_verificado, 20)
        layout.addWidget(btn_ver)
        layout.addWidget(btn_elim)
        
        self.docs_layout.addWidget(widget)
        
        # Conectar señales
        def verificar():
            self.documento_agregado.emit({
                "tipo": tipo_doc,
                "nombre": nombre,
                "ruta": ruta,
                "verificado": chk_verificado.isChecked()
            })
        
        chk_verificado.stateChanged.connect(verificar)
        
        return widget
    
    def get_bancos_data(self):
        """Obtener datos de cuentas bancarias"""
        return self._get_widgets_data(self.bancos_layout, BancoItem)
    
    def get_bursatiles_data(self):
        """Obtener datos de cuentas bursátiles"""
        return self._get_widgets_data(self.bursatil_layout, CuentaBursatilItem)
    
    def get_documentos_data(self):
        """Obtener datos de documentos (simplificado)"""
        # Esta implementación es básica, en producción sería más completa
        return []
    
    def clear_dynamic(self):
        """Limpiar widgets dinámicos"""
        self._clear_layout(self.bancos_layout)
        self._clear_layout(self.bursatil_layout)
        self._clear_layout(self.docs_layout)
    
    def load_combos(self, tipo_data=None, perfiles=None):
        """Precargar combos básicos"""
        if tipo_data:
            self.cmb_tipo.clear()
            self.cmb_tipo.addItem("-- Seleccione --", None)
            for tipo in tipo_data:
                self.cmb_tipo.addItem(tipo.value, tipo)
        
        # Perfiles de riesgo (si se habilita)
        # if perfiles and hasattr(self, 'cmb_perfil'):
        #     self.cmb_perfil.clear()
        #     self.cmb_perfil.addItem("-- Seleccione --", "")
        #     for perfil in perfiles:
        #         self.cmb_perfil.addItem(perfil, perfil)

    # ============= HELPERS =============

    def _add_input(self, layout, label, placeholder, row, col, colspan=1):
        """Agregar campo de texto"""
        widget = QWidget()
        widget.setObjectName("FormQWidget")
        vbox = QVBoxLayout(widget)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(QLabel(label))
        
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setObjectName("form_input")
        vbox.addWidget(edit)
        
        layout.addWidget(widget, row, col, 1, colspan)
        return edit

    def _add_text_area(self, layout, label, placeholder, row, col, colspan=1):
        """Agregar área de texto grande"""
        widget = QWidget()
        widget.setObjectName("FormQWidget")
        vbox = QVBoxLayout(widget)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(QLabel(label))
        
        edit = QTextEdit()
        edit.setPlaceholderText(placeholder)
        edit.setMaximumHeight(80)
        edit.setObjectName("form_textarea")
        vbox.addWidget(edit)
        
        layout.addWidget(widget, row, col, 1, colspan)
        return edit

    def _add_combo(self, layout, label, row, col, colspan=1):
        """Agregar combobox"""
        widget = QWidget()
        widget.setObjectName("FormQWidget")
        vbox = QVBoxLayout(widget)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(QLabel(label))
        
        combo = QComboBox()
        combo.setObjectName("form_combo")
        vbox.addWidget(combo)
        
        layout.addWidget(widget, row, col, 1, colspan)
        return combo
    
    def _agregar_documento(self):
        """Método para manejar subida de documentos"""
        # Este método debería abrir un diálogo de selección de archivos
        # Por ahora solo emite señal
        self.documento_agregado.emit({"accion": "agregar"})
    
    def _remove_item(self, widget):
        """Eliminar widget dinámico"""
        widget.setParent(None)
        widget.deleteLater()
    
    def _get_widgets_data(self, layout, widget_type):
        """Obtener datos de widgets específicos"""
        datos = []
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, widget_type):
                datos.append(widget.get_data())
        return datos
    
    def _clear_layout(self, layout):
        """Limpiar layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()