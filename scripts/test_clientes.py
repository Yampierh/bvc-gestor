# scripts/test_clientes.py
"""
Script para probar el módulo de clientes
"""
import sys
import os
from pathlib import Path

# Añadir el directorio src al path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

def test_database():
    """Probar conexión a base de datos"""
    print("Probando conexión a base de datos...")
    
    try:
        from bvc_gestor.database.engine import get_database
        db = get_database()
        
        if db.test_connection():
            print("✓ Base de datos conectada")
            
            # Contar clientes
            session = db.get_session()
            from bvc_gestor.database.models_sql import ClienteDB
            count = session.query(ClienteDB).count()
            print(f"✓ Total clientes en DB: {count}")
            
            session.close()
            return True
        else:
            print("✗ Error conectando a base de datos")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_validators():
    """Probar validadores venezolanos"""
    print("\nProbando validadores venezolanos...")
    
    from bvc_gestor.utils.validators_venezuela import (
        validar_cedula, validar_rif, validar_telefono_venezolano
    )
    
    # Test cédulas
    cedulas_validas = ["V-12345678", "E-87654321", "V12345678"]
    cedulas_invalidas = ["V-11111111", "X-12345678", "12345678"]
    
    print("Cédulas válidas:")
    for ced in cedulas_validas:
        print(f"  {ced}: {validar_cedula(ced)}")
    
    print("Cédulas inválidas:")
    for ced in cedulas_invalidas:
        print(f"  {ced}: {validar_cedula(ced)}")
    