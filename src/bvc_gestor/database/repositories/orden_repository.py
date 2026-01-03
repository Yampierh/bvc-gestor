# src/bvc_gestor/database/repositories/orden_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from ..models_sql import OrdenDB
from ...utils.constants import EstadoOrden

class OrdenRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, orden_id: int) -> Optional[OrdenDB]:
        return self.session.get(OrdenDB, orden_id)

    def get_por_cliente(self, cliente_id: int, limite: int = 50) -> List[OrdenDB]:
        """Obtiene las órdenes más recientes de un cliente"""
        stmt = (
            select(OrdenDB)
            .where(OrdenDB.cliente_id == cliente_id)
            .order_by(desc(OrdenDB.fecha_registro))
            .limit(limite)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_pendientes_por_activo(self, activo_id: str) -> List[OrdenDB]:
        """Útil para ver la profundidad de mercado de un ticker (ej. BNC)"""
        stmt = (
            select(OrdenDB)
            .where(OrdenDB.activo_id == activo_id)
            .where(OrdenDB.estado == EstadoOrden.PENDIENTE)
        )
        return list(self.session.execute(stmt).scalars().all())