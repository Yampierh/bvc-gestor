# src/bvc_gestor/ui/components/combo_items.py
"""
Widgets dinámicos reutilizables para formularios
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox,
    QLineEdit, QRadioButton, QPushButton
)
from PyQt6.QtCore import pyqtSignal, Qt


class DynamicItem(QWidget):
    """Clase base para items dinámicos"""
    removed = pyqtSignal(QWidget)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("RowItem")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(10)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configurar UI - Implementar en subclases"""
        raise NotImplementedError
    
    def _add_combo(self, items, placeholder):
        """Agregar combobox con items"""
        combo = QComboBox()
        combo.setObjectName("item_combo")
        combo.setMinimumWidth(200)
        combo.addItem(f"-- {placeholder} --", None)
        
        if items:
            for item in items:
                nombre = item.get("nombre", "")
                item_id = item.get("id")
                if nombre and item_id:
                    combo.addItem(nombre, item_id)
        
        return combo
    
    def _add_input(self, placeholder):
        """Agregar campo de texto"""
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setObjectName("item_input")
        edit.setMinimumWidth(150)
        return edit
    
    def _add_radio(self, text):
        """Agregar radio button"""
        radio = QRadioButton(text)
        radio.setObjectName("principal_radio")
        return radio
    
    def _add_tipo_combo(self):
        """Agregar combo de tipos"""
        combo = QComboBox()
        combo.setObjectName("tipo_combo")
        combo.setMinimumWidth(120)
        return combo
    
    def _add_delete_btn(self):
        """Agregar botón eliminar"""
        btn = QPushButton("🗑")
        btn.setFlat(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setObjectName("delete_btn")
        btn.setFixedSize(30, 30)
        btn.clicked.connect(lambda: self.removed.emit(self))
        return btn
    
    def get_data(self):
        """Obtener datos - Implementar en subclases"""
        raise NotImplementedError


class BancoItem(DynamicItem):
    """Widget para cuenta bancaria"""
    
    def __init__(self, bancos=None):
        self.bancos = bancos or []
        super().__init__()
    
    def _setup_ui(self):
        self.cmb_banco = self._add_combo(self.bancos, "Banco")
        self.txt_cuenta = self._add_input("Número de cuenta")
        self.cmb_tipo = self._add_tipo_combo()
        self.cmb_tipo.addItems(["Corriente", "Ahorros", "Nómina"])
        self.rbtn_principal = self._add_radio("Principal")
        
        self.layout.addWidget(self.cmb_banco, 35)
        self.layout.addWidget(self.txt_cuenta, 30)
        self.layout.addWidget(self.cmb_tipo, 20)
        self.layout.addWidget(self.rbtn_principal, 15)
        self.layout.addWidget(self._add_delete_btn())
    
    def set_banco(self, banco_id):
        """Seleccionar banco por ID"""
        for i in range(self.cmb_banco.count()):
            if self.cmb_banco.itemData(i) == banco_id:
                self.cmb_banco.setCurrentIndex(i)
                break
    
    def set_numero(self, numero):
        """Establecer número de cuenta"""
        self.txt_cuenta.setText(numero)
    
    def set_tipo(self, tipo_cuenta):
        """Establecer tipo de cuenta"""
        index = self.cmb_tipo.findText(tipo_cuenta)
        if index >= 0:
            self.cmb_tipo.setCurrentIndex(index)
    
    def set_principal(self, es_principal):
        """Marcar como principal"""
        self.rbtn_principal.setChecked(es_principal)
    
    def get_data(self):
        return {
            "banco_id": self.cmb_banco.currentData(),
            "numero_cuenta": self.txt_cuenta.text().strip(),
            "tipo_cuenta": self.cmb_tipo.currentText(),
            "default": self.rbtn_principal.isChecked()
        }


class CuentaBursatilItem(DynamicItem):
    """Widget para cuenta bursátil"""
    
    def __init__(self, corredores=None):
        self.corredores = corredores or []
        super().__init__()
    
    def _setup_ui(self):
        self.cmb_corredor = self._add_combo(self.corredores, "Casa Bolsa")
        self.txt_cuenta = self._add_input("Cuenta bursátil")
        self.cmb_tipo = self._add_tipo_combo()
        self.cmb_tipo.addItems(["Individual", "Conjunta", "Jurídica"])
        self.rbtn_principal = self._add_radio("Principal")
        
        self.layout.addWidget(self.cmb_corredor, 35)
        self.layout.addWidget(self.txt_cuenta, 35)
        self.layout.addWidget(self.cmb_tipo, 20)
        self.layout.addWidget(self.rbtn_principal, 10)
        self.layout.addWidget(self._add_delete_btn())
    
    def set_casa(self, casa_id):
        """Seleccionar casa de bolsa por ID"""
        for i in range(self.cmb_corredor.count()):
            if self.cmb_corredor.itemData(i) == casa_id:
                self.cmb_corredor.setCurrentIndex(i)
                break
    
    def set_cuenta(self, cuenta):
        """Establecer número de cuenta"""
        self.txt_cuenta.setText(cuenta)
    
    def set_tipo(self, tipo_cuenta):
        """Establecer tipo de cuenta"""
        index = self.cmb_tipo.findText(tipo_cuenta)
        if index >= 0:
            self.cmb_tipo.setCurrentIndex(index)
    
    def set_default(self, es_default):
        """Marcar como principal"""
        self.rbtn_principal.setChecked(es_default)
    
    def get_data(self):
        return {
            "casa_bolsa_id": self.cmb_corredor.currentData(),
            "cuenta": self.txt_cuenta.text().strip(),
            "tipo_cuenta": self.cmb_tipo.currentText(),
            "default": self.rbtn_principal.isChecked()
        }