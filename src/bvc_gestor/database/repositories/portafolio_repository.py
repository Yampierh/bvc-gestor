from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models_sql import PortafolioItemDB


class PortafolioRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_item(self, cliente_id: int, activo_id: str) -> Optional[PortafolioItemDB]:
        """Busca si el cliente ya posee este activo."""
        stmt = select(PortafolioItemDB).where(
            PortafolioItemDB.cliente_id == cliente_id,
            PortafolioItemDB.activo_id == activo_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def actualizar_o_crear_posicion(self, cliente_id: int, activo_id: str, cantidad: int, precio_compra: float):
        """Suma acciones al portafolio y promedia el costo."""
        item = self.get_item(cliente_id, activo_id)
        if item:
            # Calcular nuevo costo promedio (Lógica básica)
            total_anterior = float(item.cantidad) * float(item.costo_promedio)
            total_nuevo = cantidad * precio_compra
            item.cantidad += cantidad
            item.costo_promedio = (total_anterior + total_nuevo) / item.cantidad
        else:
            item = PortafolioItemDB(
                cliente_id=cliente_id,
                activo_id=activo_id,
                cantidad=cantidad,
                precio_compra_promedio=precio_compra
            )
            self.session.add(item)
        return item
    
    def get_by_cliente(self, cliente_id: int) -> List[PortafolioItemDB]:
        """Obtiene todos los activos que posee un cliente específico."""
        stmt = select(PortafolioItemDB).where(PortafolioItemDB.cliente_id == cliente_id)
        return list(self.session.execute(stmt).scalars().all())