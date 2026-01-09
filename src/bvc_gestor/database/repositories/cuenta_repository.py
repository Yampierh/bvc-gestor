# src/bvc_gestor/database/repositories/cuenta_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models_sql import CuentaBursatilDB

class CuentaRepository:
    """
    Repositorio especializado en la gestión de cuentas bancarias/bursátiles.
    Se encarga de las consultas directas a la tabla cuentas.
    """
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, cuenta_id: int) -> Optional[CuentaBursatilDB]:
        """Busca una cuenta por su ID primario."""
        return self.session.get(CuentaBursatilDB, cuenta_id)

    def get_by_numero(self, numero_cuenta: str) -> Optional[CuentaBursatilDB]:
        """Busca una cuenta por su número de cuenta (ej. 0105-...)"""
        stmt = select(CuentaBursatilDB).where(CuentaBursatilDB.numero_cuenta == numero_cuenta)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_cliente(self, cliente_id: int) -> List[CuentaBursatilDB]:
        """Obtiene todas las cuentas asociadas a un cliente."""
        stmt = select(CuentaBursatilDB).where(CuentaBursatilDB.cliente_id == cliente_id)
        return list(self.session.execute(stmt).scalars().all())

    def obtener_saldo_disponible(self, cuenta_id: int) -> float:
        """Devuelve el saldo disponible listo para operar."""
        cuenta = self.get_by_id(cuenta_id)
        return float(cuenta.saldo_disponible_bs) if cuenta else 0.0