from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class BalanceCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("BalanceCard")
        self.setStyleSheet("""
            #BalanceCard {
                background-color: #1e1e1e;
                border-radius: 10px;
                border: 1px solid #333;
            }
            QLabel { color: #ecf0f1; font-family: 'Segoe UI'; }
            .monto { font-size: 18px; font-weight: bold; color: #2ecc71; }
            .titulo { font-size: 12px; color: #bdc3c7; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Secciones de información: Extraemos el layout y guardamos la referencia al label
        lay_disp, self.ref_disp = self._crear_seccion("DISPONIBLE", "0.00 Bs")
        lay_tit, self.ref_tit = self._crear_seccion("EN TÍTULOS", "0.00 Bs")
        lay_tot, self.ref_tot = self._crear_seccion("PATRIMONIO TOTAL", "0.00 Bs")
        
        layout.addLayout(lay_disp)
        layout.addLayout(lay_tit)
        layout.addLayout(lay_tot)

    def _crear_seccion(self, titulo, valor_inicial):
        v_layout = QVBoxLayout()
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setProperty("class", "titulo")
        
        lbl_valor = QLabel(valor_inicial)
        lbl_valor.setProperty("class", "monto")
        
        v_layout.addWidget(lbl_titulo)
        v_layout.addWidget(lbl_valor)
        
        # Devolvemos el layout para colocarlo, y el label para actualizarlo luego
        return v_layout, lbl_valor

    def update_values(self, disponible, titulos, total):
        self.ref_disp.setText(f"{disponible:,.2f} Bs")
        self.ref_tit.setText(f"{titulos:,.2f} Bs")
        self.ref_tot.setText(f"{total:,.2f} Bs")