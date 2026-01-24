# src\bvc_gestor\ui\views\dashboard.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGridLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class MetricCard(QFrame):
    """Componente reutilizable para las tarjetas de KPI superiores"""
    def __init__(self, icon_path, title, value, color="#FF6B00"):
        super().__init__()
        self.setObjectName("MetricCard")
        
        # 1. Layout Principal (Horizontal: Icono | Textos)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # 2. Configuración del Icono
        self.icon_lbl = QLabel()
        # Cargamos la imagen y la escalamos con suavizado
        pixmap = QPixmap(icon_path)
        self.icon_lbl.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        # 3. Layout para los Textos (Vertical: Título / Valor)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1) # Espacio estrecho entre título y valor
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("MetricTitle")
        
        self.value_lbl = QLabel(value)
        self.value_lbl.setObjectName("MetricValue")
        
        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.value_lbl)

        # 4. Ensamblar la estructura
        main_layout.addWidget(self.icon_lbl)
        main_layout.addLayout(text_layout) 
        main_layout.addStretch() # Empuja todo a la izquierda para que no se separe al crecer

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        self.setup_ui()

    def setup_ui(self):

        # 2. Fila de KPIs (Métricas)
        kpi_layout = QHBoxLayout()
        kpi_layout.addWidget(MetricCard("src/bvc_gestor/assets/icons/bar_chart.svg", "Inversion", "$1,050.47"))
        kpi_layout.addWidget(MetricCard("src/bvc_gestor/assets/icons/attach_money.svg", "Ganancias", "$342.39"))
        kpi_layout.addWidget(MetricCard("src/bvc_gestor/assets/icons/info.svg", "Ordenes Pendientes", "2"))
        kpi_layout.addWidget(MetricCard("src/bvc_gestor/assets/icons/check_circle.svg", "Ordenes Activas", "12"))
        self.main_layout.addLayout(kpi_layout)

        # 3. Sección Central: Gráfico y Progreso (Placeholder visual)
        middle_section = QHBoxLayout()
        
        chart_frame = QFrame()
        chart_frame.setObjectName("Card")
        chart_frame.setMinimumHeight(300)
        chart_vbox = QVBoxLayout(chart_frame)
        chart_vbox.addWidget(QLabel("Activity Overview (Line Chart Placeholder)"))
        
        progress_frame = QFrame()
        progress_frame.setObjectName("Card")
        progress_frame.setFixedWidth(350)
        prog_vbox = QVBoxLayout(progress_frame)
        prog_vbox.addWidget(QLabel("Project Completion"))
        
        middle_section.addWidget(chart_frame, stretch=2)
        middle_section.addWidget(progress_frame, stretch=1)
        self.main_layout.addLayout(middle_section)

        # 4. Sección Inferior: Tabla de Reportes
        self.create_reports_table()

    def create_reports_table(self):
        container = QFrame()
        container.setObjectName("Card")
        layout = QVBoxLayout(container)
        
        title = QLabel("Weekly Reports")
        title.setObjectName("TableTitle")
        layout.addWidget(title)
        
        table = QTableWidget(5, 5)
        table.setHorizontalHeaderLabels(["Name", "Status", "Size", "Date", "Time"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        
        # Datos de ejemplo
        sample_data = [
            ("Jonathan Sandoval", "In Progress", "56 MB", "10 Jun 2024", "04:41 PM"),
            ("Matt Doherty", "Completed", "45 MB", "10 Jun 2024", "04:40 PM"),
            ("Adela Parkson", "Submitted", "98 MB", "10 Jun 2024", "04:37 PM"),
        ]
        
        for row_idx, row_data in enumerate(sample_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                table.setItem(row_idx, col_idx, item)
        
        layout.addWidget(table)
        self.main_layout.addWidget(container)