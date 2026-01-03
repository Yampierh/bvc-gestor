from decimal import Decimal
from ..models_sql import ActivoDB, ConfiguracionDB
from ..engine import get_database

def cargar_datos_iniciales():
    db_engine = get_database()
    session = db_engine.get_session()
    
    try:
        # 1. Cargar Tickers (Activos)
        tickers = [
            {"id": "MVZ.B", "nombre": "Mercantil Servicios Financieros (B)", "tipo": "Acción", "sector": "Banca"},
            {"id": "RST", "nombre": "Ron Santa Teresa", "tipo": "Acción", "sector": "Consumo"},
            {"id": "BNC", "nombre": "Banco Nacional de Crédito", "tipo": "Acción", "sector": "Banca"},
            # Agrega aquí la lista completa que te pasé antes
        ]
        
        for t in tickers:
            # Solo agregamos si no existe para evitar errores de duplicado
            if not session.query(ActivoDB).filter_by(id=t['id']).first():
                nuevo_activo = ActivoDB(
                    id=t['id'],
                    nombre=t['nombre'],
                    tipo=t['tipo'],
                    sector=t['sector'],
                    moneda="VES",
                    precio_actual=Decimal("0.00")
                )
                session.add(nuevo_activo)

        # 2. Cargar Configuraciones Globales
        configs = [
            {"clave": "comision_casa_bolsa", "valor": "0.009", "tipo": "number", "categoria": "Bolsa"},
            {"clave": "iva_porcentaje", "valor": "0.16", "tipo": "number", "categoria": "Impuestos"},
            {"clave": "tasa_bcv_usd", "valor": "55.50", "tipo": "number", "categoria": "Mercado"}
        ]

        for c in configs:
            if not session.query(ConfiguracionDB).filter_by(clave=c['clave']).first():
                session.add(ConfiguracionDB(**c))

        session.commit()
        print("✓ Datos iniciales cargados con éxito.")
        
    except Exception as e:
        session.rollback()
        print(f"Error cargando seeds: {e}")
    finally:
        session.close()