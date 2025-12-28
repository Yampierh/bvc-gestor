# scripts/seed_activos.py
"""
Script para crear datos de prueba de activos BVC
"""
import sys
import os
from pathlib import Path

# Añadir el directorio src al path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from bvc_gestor.database.engine import get_database
from bvc_gestor.database.models_sql import ActivoDB
from bvc_gestor.utils.constants import Moneda
from datetime import datetime
from decimal import Decimal
import random

def crear_activos_prueba():
    """Crear activos de prueba de la BVC"""
    print("Creando activos bursátiles de prueba...")
    
    try:
        # Obtener sesión de base de datos
        db = get_database()
        session = db.get_session()
        
        # Lista de activos de prueba (acciones reales de la BVC)
        activos_prueba = [
            # Acciones blue chips
            ActivoDB(
                id="BNC",
                nombre="Banco Nacional de Crédito C.A.",
                tipo="Acción",
                sector="Financiero",
                subsector="Banca Universal",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('1.2500'),
                precio_anterior=Decimal('1.2300'),
                variacion_diaria=Decimal('0.0200'),
                volumen_promedio=1500000,
                lote_standard=100,
                lote_minimo=1,
                activo=True
            ),
            
            ActivoDB(
                id="EMPV",
                nombre="Empresas Polar C.A.",
                tipo="Acción",
                sector="Consumo",
                subsector="Alimentos y Bebidas",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('3.4500'),
                precio_anterior=Decimal('3.4000'),
                variacion_diaria=Decimal('0.0500'),
                volumen_promedio=800000,
                lote_standard=100,
                lote_minimo=1,
                activo=True
            ),
            
            ActivoDB(
                id="BNV",
                nombre="Banco de Venezuela S.A.C.A.",
                tipo="Acción",
                sector="Financiero",
                subsector="Banca Universal",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('2.1000'),
                precio_anterior=Decimal('2.1500'),
                variacion_diaria=Decimal('-0.0500'),
                volumen_promedio=1200000,
                lote_standard=100,
                lote_minimo=1,
                activo=True
            ),
            
            ActivoDB(
                id="TEL",
                nombre="CANTV C.A.",
                tipo="Acción",
                sector="Telecomunicaciones",
                subsector="Telefonía",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('0.8500'),
                precio_anterior=Decimal('0.8200'),
                variacion_diaria=Decimal('0.0300'),
                volumen_promedio=2000000,
                lote_standard=100,
                lote_minimo=1,
                activo=True
            ),
            
            # Bonos
            ActivoDB(
                id="BVTA2030",
                nombre="Bono de la República 2030",
                tipo="Bono",
                sector="Deuda Pública",
                subsector="Bonos Soberanos",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('95.5000'),
                precio_anterior=Decimal('95.2000'),
                variacion_diaria=Decimal('0.3000'),
                volumen_promedio=50000,
                lote_standard=1,
                lote_minimo=1,
                activo=True
            ),
            
            ActivoDB(
                id="PDVSA27",
                nombre="Bono PDVSA 2027",
                tipo="Bono",
                sector="Deuda Corporativa",
                subsector="Petróleo y Gas",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('32.1500'),
                precio_anterior=Decimal('32.0000'),
                variacion_diaria=Decimal('0.1500'),
                volumen_promedio=75000,
                lote_standard=1,
                lote_minimo=1,
                activo=True
            ),
            
            # ETFs y fondos
            ActivoDB(
                id="IBVC",
                nombre="ETF Índice BVC",
                tipo="ETF",
                sector="Índice",
                subsector="ETF Diversificado",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('125.7500'),
                precio_anterior=Decimal('124.5000'),
                variacion_diaria=Decimal('1.2500'),
                volumen_promedio=300000,
                lote_standard=10,
                lote_minimo=1,
                activo=True
            ),
            
            ActivoDB(
                id="FIM",
                nombre="Fondo de Inversión Mercantil",
                tipo="Fondo de Inversión",
                sector="Financiero",
                subsector="Fondos Mutuos",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('10.2500'),
                precio_anterior=Decimal('10.2000'),
                variacion_diaria=Decimal('0.0500'),
                volumen_promedio=500000,
                lote_standard=100,
                lote_minimo=10,
                activo=True
            ),
            
            # Más acciones
            ActivoDB(
                id="MAD",
                nombre="Maderas del Orinoco C.A.",
                tipo="Acción",
                sector="Industrial",
                subsector="Madera y Papel",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('0.4500'),
                precio_anterior=Decimal('0.4300'),
                variacion_diaria=Decimal('0.0200'),
                volumen_promedio=3000000,
                lote_standard=1000,
                lote_minimo=100,
                activo=True
            ),
            
            ActivoDB(
                id="SVS",
                nombre="Siderúrgica del Orinoco C.A.",
                tipo="Acción",
                sector="Industrial",
                subsector="Siderurgia",
                moneda=Moneda.DOLAR,
                precio_actual=Decimal('0.2800'),
                precio_anterior=Decimal('0.2750'),
                variacion_diaria=Decimal('0.0050'),
                volumen_promedio=5000000,
                lote_standard=1000,
                lote_minimo=100,
                activo=True
            )
        ]
        
        # Agregar activos a la sesión
        for activo in activos_prueba:
            # Verificar si ya existe
            existe = session.query(ActivoDB).filter_by(id=activo.id).first()
            if not existe:
                session.add(activo)
                print(f"Añadido activo: {activo.id} - {activo.nombre}")
        
        # Guardar cambios
        session.commit()
        print(f"\n✓ {len(activos_prueba)} activos bursátiles creados exitosamente")
        
        # Mostrar resumen
        total_activos = session.query(ActivoDB).count()
        print(f"Total de activos en base de datos: {total_activos}")
        
        session.close()
        
    except Exception as e:
        print(f"✗ Error creando activos de prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_activos_prueba()