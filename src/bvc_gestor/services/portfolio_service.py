from decimal import Decimal
import logging
from ..database.repositories import RepositoryFactory
from typing import List

logger = logging.getLogger(__name__)

class PortfolioService:
    def __init__(self, db_session):
        self.db = db_session

    def obtener_resumen_cliente(self, cliente_id: int):
        """
        Devuelve un resumen detallado para la pantalla principal:
        Saldos + Activos + Ganancia/Pérdida (P&L).
        """
        cuenta_repo = RepositoryFactory.get_repository(self.db, 'cuenta')
        portafolio_repo = RepositoryFactory.get_repository(self.db, 'portafolio')
        
        # 1. Obtener saldos
        cuentas = cuenta_repo.get_by_cliente(cliente_id)
        if not cuentas:
            return None
        
        cuenta = cuentas[0] # Usamos la principal por ahora
        
        # 2. Obtener items del portafolio
        items = portafolio_repo.get_by_cliente(cliente_id) # Debes añadir este método al repo
        
        resumen_activos = []
        valor_total_titulos = Decimal("0.0")

        for item in items:
            # Aquí asumimos que tienes una forma de obtener el precio actual
            # Podrías usar un ActivoRepository para obtener el precio de mercado
            precio_actual = Decimal("0.0055") # Simulado: Precio actual en BVC
            
            valor_mercado = item.cantidad * precio_actual
            valor_total_titulos += valor_mercado
            
            ganancia_unitaria = precio_actual - Decimal(str(item.costo_promedio))
            rendimiento_pct = (ganancia_unitaria / Decimal(str(item.costo_promedio))) * 100

            resumen_activos.append({
                "activo": item.activo_id,
                "cantidad": item.cantidad,
                "costo_promedio": item.costo_promedio,
                "precio_actual": precio_actual,
                "valor_mercado": valor_mercado,
                "pnl_pct": rendimiento_pct
            })

        return {
            "saldo_disponible": cuenta.saldo_disponible_bs,
            "saldo_bloqueado": cuenta.saldo_bloqueado_bs,
            "valor_en_titulos": valor_total_titulos,
            "patrimonio_total": cuenta.saldo_disponible_bs + cuenta.saldo_bloqueado_bs + valor_total_titulos,
            "activos": resumen_activos
        }