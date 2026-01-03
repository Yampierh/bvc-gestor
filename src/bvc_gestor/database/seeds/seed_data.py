"""
Script para poblar la base de datos basándose estrictamente en models_sql.py
"""
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import date

from ...database.engine import get_database
from ...database.models_sql import (
    BancoDB, CasaBolsaDB, ClienteDB, CuentaDB, 
    ActivoDB, PortafolioItemDB, ConfiguracionDB
)
from ...utils.constants import (
    TipoPersona, TipoDocumento, PerfilRiesgo, Moneda
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_seeds():
    db = get_database()
    db.create_tables() # Crea las tablas si no existen
    session = db.get_session()
    
    try:
        logger.info("🌱 Iniciando carga de datos según modelos SQL...")

        # 1. Bancos (Basado en BancoDB)
        banco = session.query(BancoDB).filter_by(rif="J-00002961-0").first()
        if not banco:
            banco = BancoDB(
                nombre="Banco Mercantil",
                rif="J-00002961-0",
                codigo_banco="0105",
                pais="Venezuela"
            )
            session.add(banco)
            logger.info("✓ Banco creado")

        # 2. Casas de Bolsa (Basado en CasaBolsaDB)
        casa = session.query(CasaBolsaDB).filter_by(rif="J-30694531-8").first()
        if not casa:
            casa = CasaBolsaDB(
                nombre="Merinvest Casa de Bolsa",
                rif="J-30694531-8",
                codigo_casa="001"
            )
            session.add(casa)
            logger.info("✓ Casa de Bolsa creada")
        
        session.flush()

        # 3. Cliente (Basado en ClienteDB y sus validadores)
        cliente = session.query(ClienteDB).filter_by(documento_id="V-12345678").first()
        if not cliente:
            cliente = ClienteDB(
                documento_id="V-12345678", # Pasa validar_cedula
                tipo_persona=TipoPersona.NATURAL,
                tipo_documento=TipoDocumento.CEDULA,
                nombre_completo="Juan Pérez Inversionista",
                email="juan.perez@email.com",
                telefono="+58-414-1234567", # Pasa validar_telefono_venezolano
                direccion="Av. Francisco de Miranda, Chacao",
                ciudad="Caracas",
                estado="Miranda",
                perfil_riesgo=PerfilRiesgo.MODERADO,
                id_banco=banco.id,
                id_casa_bolsa=casa.id
            )
            session.add(cliente)
            session.flush()
            logger.info(f"✓ Cliente '{cliente.nombre_completo}' creado")

            # 4. Cuenta Bursátil (Basado en CuentaDB)
            cuenta = CuentaDB(
                cliente_id=cliente.id,
                numero_cuenta="BVC-2023-0001",
                tipo_cuenta="Individual",
                moneda_base=Moneda.BOLIVAR.value,
                saldo_disponible_bs=Decimal("10000.00000000"),
                saldo_disponible_usd=Decimal("250.00000000"),
                estado="Activa"
            )
            session.add(cuenta)
            session.flush()
            logger.info("✓ Cuenta bursátil con saldo inicial creada")

        # 5. Activos (Basado en ActivoDB)
        activos = [
            {"id": "MVZ.B", "nombre": "Mercantil Serv. Fin B", "rif": "J-00002961-0", "precio": "135.00"},
            {"id": "BNC", "nombre": "Banco Nacional de Crédito", "rif": "J-30984132-7", "precio": "0.0050"},
            {"id": "CANTV", "nombre": "CANTV Clase D", "rif": "J-00124134-5", "precio": "3.80"}
        ]

        for act in activos:
            if not session.get(ActivoDB, act["id"]):
                nuevo_activo = ActivoDB(
                    id=act["id"],
                    nombre=act["nombre"],
                    rif=act["rif"],
                    tipo="Acción",
                    moneda=Moneda.BOLIVAR.value,
                    precio_actual=Decimal(act["precio"]),
                    lote_standard=100
                )
                session.add(nuevo_activo)
        
        session.flush()
        logger.info(f"✓ {len(activos)} Activos cargados")

        # 6. Portafolio inicial (Basado en PortafolioItemDB)
        # Verificamos si Juan ya tiene BNC (usando cuenta.id y cliente.id que son Integer)
        item = session.query(PortafolioItemDB).filter_by(activo_id="BNC", cliente_id=cliente.id).first()
        if not item:
            posicion = PortafolioItemDB(
                cliente_id=cliente.id,
                cuenta_id=cuenta.id,
                activo_id="BNC",
                cantidad=5000,
                costo_promedio=Decimal("0.0045"),
                precio_actual=Decimal("0.0050"),
                moneda=Moneda.BOLIVAR.value
            )
            session.add(posicion)
            logger.info("✓ Posición inicial de BNC añadida al portafolio")

        session.commit()
        logger.info("✨ Base de datos poblada exitosamente según modelos SQL.")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error en la seed: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    run_seeds()