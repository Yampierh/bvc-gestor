from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QColor

class PortfolioTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Activo", "Cantidad", "Costo Prom.", "Precio Act.", "P&L %"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("QTableWidget { background-color: #252526; color: white; border: none; }")

    def load_data(self, activos):
        self.setRowCount(len(activos))
        for i, data in enumerate(activos):
            self.setItem(i, 0, QTableWidgetItem(data['activo']))
            self.setItem(i, 1, QTableWidgetItem(f"{data['cantidad']:,}"))
            self.setItem(i, 2, QTableWidgetItem(f"{data['costo_promedio']:.4f}"))
            self.setItem(i, 3, QTableWidgetItem(f"{data['precio_actual']:.4f}"))
            
            # Formatear P&L con color (Verde para ganancia, Rojo para pérdida)
            pnl = data['pnl_pct']
            pnl_item = QTableWidgetItem(f"{pnl:+.2f}%")
            pnl_item.setForeground(QColor("#2ecc71") if pnl >= 0 else QColor("#e74c3c"))
            self.setItem(i, 4, pnl_item)