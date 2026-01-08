from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QHeaderView, QLineEdit, QPushButton, QLabel, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt

class ClientesListView(QWidget):
    # Señal que emite el ID del cliente seleccionado
    cliente_seleccionado = pyqtSignal(int)
    nuevo_cliente_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Barra Superior
        toolbar = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Buscar por RIF o Razón Social...")
        self.search_bar.setObjectName("searchBar")
        
        self.btn_nuevo = QPushButton("+ Nuevo Cliente")
        self.btn_nuevo.setObjectName("primaryButton")
        self.btn_nuevo.clicked.connect(self.nuevo_cliente_clicked.emit)

        toolbar.addWidget(self.search_bar, stretch=3)
        toolbar.addStretch(1)
        toolbar.addWidget(self.btn_nuevo)
        layout.addLayout(toolbar)

        # Tabla de Clientes
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["RIF", "Nombre / Razón Social", "Tipo", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        
        # Conectar doble clic para abrir detalle
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        layout.addWidget(self.table)

    def _on_row_double_clicked(self, row, column):
        # Asumiendo que guardamos el ID en un dato oculto o primera columna
        cliente_id = int(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole))
        self.cliente_seleccionado.emit(cliente_id)