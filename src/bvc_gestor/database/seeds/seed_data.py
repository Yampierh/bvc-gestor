import pandas as pd
import logging
import os
from pathlib import Path

# Usamos importaciones absolutas para evitar el error de "parent package"
from src.bvc_gestor.database.engine import get_database
from src.bvc_gestor.database.models_sql import BancoDB, ActivoDB, CasaBolsaDB

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SeedData")

def seed_database():
    # 1. LOCALIZAR ARCHIVOS (Detecta la carpeta donde está el script)
    current_dir = Path(__file__).parent.absolute()
    
    db_engine = get_database()
    session = db_engine.get_session()
    
    try:
        # --- A. CARGAR BANCOS ---
        file_bancos = current_dir / "bancos_venezuela.csv"
        if file_bancos.exists():
            logger.info(f"Procesando: {file_bancos.name}")
            df = pd.read_csv(file_bancos)
            for _, row in df.iterrows():
                cod = str(row['codigo']).zfill(4)
                if not session.query(BancoDB).filter_by(codigo=cod).first():
                    session.add(BancoDB(
                        codigo=cod,
                        nombre=row['nombre'],
                        rif=row['rif']
                    ))
        
        # --- B. CARGAR ACTIVOS (TICKERS) ---
        file_tickers = current_dir / "lista_tickers_bvc.csv"
        if file_tickers.exists():
            logger.info(f"Procesando: {file_tickers.name}")
            df = pd.read_csv(file_tickers)
            for _, row in df.iterrows():
                if not session.query(ActivoDB).filter_by(rif=row['rif']).first():
                    session.add(ActivoDB(
                        ticker=row['ticker'],
                        nombre=row['nombre_emisor'],
                        rif=row['rif'],
                        sector=row['sector'],
                    ))

        # --- C. CARGAR CASAS DE BOLSA ---
        file_casas = current_dir / "entidades_bursatiles_ven.csv"
        if file_casas.exists():
            logger.info(f"Procesando: {file_casas.name}")
            df = pd.read_csv(file_casas)
            for _, row in df.iterrows():
                if not session.query(CasaBolsaDB).filter_by(rif=row['rif']).first():
                    session.add(CasaBolsaDB(
                        nombre=row['nombre'],
                        rif=row['rif'],
                        sector=row['sector'],
                        tipo_entidad=row['tipo_entidad'],
                    ))

        session.commit()
        logger.info("¡✓ Base de datos semillada con éxito!")

    except Exception as e:
        session.rollback()
        logger.error(f"¡X Error durante el semillado: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()