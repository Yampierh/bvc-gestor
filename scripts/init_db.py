# scripts/init_db.py - VERSIÓN CORREGIDA
"""
Script para inicializar la base de datos
"""
import sys
from pathlib import Path

# Añadir src al path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

def main():
    from bvc_gestor.database.engine import get_database
    from bvc_gestor.utils.logger import logger
    
    print("Inicializando base de datos BVC-GESTOR...")
    
    try:
        # Obtener motor de base de datos
        db_engine = get_database()
        
        # Probar conexión
        if db_engine.test_connection():
            print("✓ Conexión a base de datos exitosa")
        else:
            print("✗ Error en conexión a base de datos")
            return 1
        
        # Crear tablas
        print("Creando tablas...")
        db_engine.create_tables()
        print("✓ Tablas creadas exitosamente")
        
        # Insertar datos iniciales
        print("Insertando datos iniciales...")
        insert_initial_data(db_engine)
        print("✓ Datos iniciales insertados")
        
        print("\n✅ Base de datos inicializada correctamente")
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def insert_initial_data(db_engine):
    """Insertar datos iniciales en la base de datos"""
    from sqlalchemy.orm import Session
    from bvc_gestor.utils.constants import Moneda
    from bvc_gestor.database.models_sql import (
        ActivoDB, ConfiguracionDB
    )
    
    # Crear sesión
    session = db_engine.get_session()
    
    try:
        # Insertar configuración inicial
        configs = [
            ('app_nombre', 'BVC-GESTOR', 'string', 'General', 'Nombre de la aplicación'),
            ('app_version', '1.0.0', 'string', 'General', 'Versión de la aplicación'),
            ('comision_base', '0.005', 'number', 'Comisiones', 'Comisión base (0.5%)'),
            ('iva', '0.16', 'number', 'Comisiones', 'IVA (16%)'),
            ('moneda_principal', 'USD', 'string', 'General', 'Moneda principal'),
            ('backup_automatico', 'true', 'boolean', 'Backup', 'Backup automático activado'),
            ('tema_oscuro', 'false', 'boolean', 'Apariencia', 'Tema oscuro activado'),
        ]
        
        for clave, valor, tipo, categoria, descripcion in configs:
            config = ConfiguracionDB(
                clave=clave,
                valor=valor,
                tipo=tipo,
                categoria=categoria,
                descripcion=descripcion
            )
            session.add(config)
        
        # Insertar activos bursátiles de ejemplo (BVC)
        activos = [
            ('BNC', 'Banco Nacional de Crédito, C.A.', 'Acción', 'Financiero', Moneda.USD.value, 1.25, 100),
            ('BNV', 'Banco Nacional de Venezuela', 'Acción', 'Financiero', Moneda.USD.value, 2.10, 100),
            ('EMPV', 'Empresas Polar, C.A.', 'Acción', 'Consumo', Moneda.USD.value, 3.40, 100),
            ('TELV', 'CANTV', 'Acción', 'Telecomunicaciones', Moneda.USD.value, 0.85, 100),
            ('ELEC', 'Enel Venezuela', 'Acción', 'Energía', Moneda.USD.value, 1.50, 100),
            ('MOVI', 'Movilnet', 'Acción', 'Telecomunicaciones', Moneda.USD.value, 0.95, 100),
            ('PDV', 'Petróleos de Venezuela', 'Acción', 'Energía', Moneda.USD.value, 5.20, 100),
        ]
        
        for simbolo, nombre, tipo, sector, moneda, precio, lote in activos:
            activo = ActivoDB(
                id=simbolo,
                nombre=nombre,
                tipo=tipo,
                sector=sector,
                moneda=moneda,
                precio_actual=precio,
                precio_anterior=precio * 0.98,  # 2% menos
                variacion_diaria=2.0,
                lote_standard=lote,
                lote_minimo=1,
                activo=True
            )
            session.add(activo)
        
        # Guardar cambios
        session.commit()
        print(f"  Insertados {len(configs)} configuraciones y {len(activos)} activos")
        
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    sys.exit(main())