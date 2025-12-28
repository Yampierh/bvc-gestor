# scripts/seed_clientes.py
"""
Script para crear datos de prueba de clientes
"""
import sys
import os
from pathlib import Path

# Añadir el directorio src al path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from bvc_gestor.database.engine import get_database
from bvc_gestor.database.models_sql import ClienteDB, CuentaDB
from bvc_gestor.utils.constants import TipoPersona, TipoDocumento, PerfilRiesgo
from datetime import datetime, date

def crear_clientes_prueba():
    """Crear clientes de prueba"""
    print("Creando clientes de prueba...")
    
    try:
        # Obtener sesión de base de datos
        db = get_database()
        session = db.get_session()
        
        # Lista de clientes de prueba
        clientes_prueba = [
            ClienteDB(
                id="V-12345678",
                tipo_persona=TipoPersona.NATURAL,
                tipo_documento=TipoDocumento.CEDULA,
                nombre_completo="María González Pérez",
                fecha_nacimiento=date(1985, 5, 15),
                profesion_ocupacion="Ingeniero Civil",
                telefono_principal="0414-5551234",
                email="maria.gonzalez@email.com",
                direccion="Av. Principal, Residencias Las Acacias, Apt 4B",
                ciudad="Caracas",
                estado="Distrito Capital",
                perfil_riesgo=PerfilRiesgo.MODERADO,
                limite_inversion_usd=50000.00,
                limite_inversion_bs=500000000.00,
                ingresos_mensuales_usd=3000.00,
                ingresos_mensuales_bs=30000000.00,
                banco_principal="Banco de Venezuela",
                numero_cuenta="0102-1234-5678-9012",
                tipo_cuenta="Ahorros",
                tiene_patrimonio_declarado=True,
                monto_patrimonio_usd=150000.00,
                monto_patrimonio_bs=1500000000.00,
                notas="Cliente preferencial. Le gustan inversiones a mediano plazo."
            ),
            
            ClienteDB(
                id="V-87654321",
                tipo_persona=TipoPersona.NATURAL,
                tipo_documento=TipoDocumento.CEDULA,
                nombre_completo="Carlos Rodríguez López",
                fecha_nacimiento=date(1978, 11, 30),
                profesion_ocupacion="Empresario",
                telefono_principal="0424-6667890",
                telefono_secundario="0212-5556677",
                email="carlos.rodriguez@empresa.com",
                direccion="Urbanización La Florida, Calle 3, Casa #45",
                ciudad="Caracas",
                estado="Miranda",
                perfil_riesgo=PerfilRiesgo.AGRESIVO,
                limite_inversion_usd=250000.00,
                limite_inversion_bs=2500000000.00,
                ingresos_mensuales_usd=15000.00,
                ingresos_mensuales_bs=150000000.00,
                banco_principal="Banesco",
                numero_cuenta="0134-9876-5432-1098",
                tipo_cuenta="Corriente",
                tiene_patrimonio_declarado=True,
                monto_patrimonio_usd=500000.00,
                monto_patrimonio_bs=5000000000.00,
                notas="Cliente de alto patrimonio. Prefiere acciones de crecimiento."
            ),
            
            ClienteDB(
                id="V-11223344",
                tipo_persona=TipoPersona.NATURAL,
                tipo_documento=TipoDocumento.CEDULA,
                nombre_completo="Ana Martínez Fernández",
                fecha_nacimiento=date(1990, 3, 22),
                profesion_ocupacion="Abogada",
                telefono_principal="0412-7778889",
                email="ana.martinez@abogados.com",
                direccion="El Rosal, Torre Exec, Piso 8, Oficina 802",
                ciudad="Caracas",
                estado="Distrito Capital",
                perfil_riesgo=PerfilRiesgo.CONSERVADOR,
                limite_inversion_usd=20000.00,
                limite_inversion_bs=200000000.00,
                ingresos_mensuales_usd=2500.00,
                ingresos_mensuales_bs=25000000.00,
                banco_principal="Mercantil",
                numero_cuenta="0105-5566-7788-9900",
                tipo_cuenta="Ahorros",
                tiene_patrimonio_declarado=False,
                notas="Cliente nuevo. Prefiere inversiones seguras con rendimiento estable."
            ),
            
            ClienteDB(
                id="J-12345678-9",
                tipo_persona=TipoPersona.JURIDICA,
                tipo_documento=TipoDocumento.RIF,
                nombre_completo="Inversiones Tecnológicas, C.A.",
                telefono_principal="0212-4445566",
                telefono_secundario="0212-4445577",
                email="info@inversionestec.com",
                direccion="Centro Comercial San Ignacio, Nivel 3, Local 15",
                ciudad="Caracas",
                estado="Distrito Capital",
                perfil_riesgo=PerfilRiesgo.MODERADO,
                limite_inversion_usd=500000.00,
                limite_inversion_bs=5000000000.00,
                ingresos_mensuales_usd=50000.00,
                ingresos_mensuales_bs=500000000.00,
                banco_principal="Banco Provincial",
                numero_cuenta="0108-1122-3344-5566",
                tipo_cuenta="Corriente Empresarial",
                tiene_patrimonio_declarado=True,
                monto_patrimonio_usd=1000000.00,
                monto_patrimonio_bs=10000000000.00,
                notas="Empresa de tecnología. Buscan diversificar su portafolio de inversiones."
            ),
            
            ClienteDB(
                id="V-55667788",
                tipo_persona=TipoPersona.NATURAL,
                tipo_documento=TipoDocumento.CEDULA,
                nombre_completo="Luis Pérez Mendoza",
                fecha_nacimiento=date(1965, 8, 10),
                profesion_ocupacion="Médico",
                telefono_principal="0416-9990001",
                email="dr.luis.perez@clinica.com",
                direccion="Urbanización Altamira, Edificio Los Pinos, Apt 12A",
                ciudad="Caracas",
                estado="Miranda",
                perfil_riesgo=PerfilRiesgo.CONSERVADOR,
                limite_inversion_usd=100000.00,
                limite_inversion_bs=1000000000.00,
                ingresos_mensuales_usd=8000.00,
                ingresos_mensuales_bs=80000000.00,
                banco_principal="Banco Bicentenario",
                numero_cuenta="0175-9988-7766-5544",
                tipo_cuenta="Ahorros",
                tiene_patrimonio_declarado=True,
                monto_patrimonio_usd=300000.00,
                monto_patrimonio_bs=3000000000.00,
                notas="Cliente de larga data. Prefiere bonos y fondos de inversión."
            )
        ]
        
        # Agregar clientes a la sesión
        for cliente in clientes_prueba:
            # Verificar si ya existe
            existe = session.query(ClienteDB).filter_by(id=cliente.id).first()
            if not existe:
                session.add(cliente)
                print(f"Añadido cliente: {cliente.nombre_completo}")
                
                # Crear cuenta automática
                import random
                numero_cuenta = f"CTA-{cliente.id}-{random.randint(1000, 9999)}"
                cuenta = CuentaDB(
                    cliente_id=cliente.id,
                    numero_cuenta=numero_cuenta,
                    tipo_cuenta="Individual" if cliente.tipo_persona == TipoPersona.NATURAL else "Corporativa",
                    moneda_base="USD",
                    saldo_disponible_usd=0.00,
                    saldo_disponible_bs=0.00,
                    estado="Activa"
                )
                session.add(cuenta)
                print(f"  Cuenta creada: {numero_cuenta}")
        
        # Guardar cambios
        session.commit()
        print(f"\n✓ {len(clientes_prueba)} clientes de prueba creados exitosamente")
        
        # Mostrar resumen
        total_clientes = session.query(ClienteDB).count()
        print(f"Total de clientes en base de datos: {total_clientes}")
        
        session.close()
        
    except Exception as e:
        print(f"✗ Error creando clientes de prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_clientes_prueba()