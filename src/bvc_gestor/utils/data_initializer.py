# src/bvc_gestor/utils/data_initializer.py
"""
Script para inicializar la base de datos con datos de prueba
"""
import csv
import os
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal
import random
from typing import List, Dict, Any

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from bvc_gestor.database.engine import get_database
from bvc_gestor.database.models_sql import (
    BancoDB, CasaBolsaDB, ClienteDB, CuentaBancariaDB, 
    CuentaBursatilDB, DocumentoDB, TituloDB
)
from bvc_gestor.utils.constants import TipoInversor

class DataInitializer:
    """Clase para inicializar datos de prueba"""
    
    def __init__(self):
        self.db_engine = get_database()
        self.session = self.db_engine.get_session()
        
    def run(self):
        """Ejecutar toda la inicialización"""
        print("🚀 Inicializando base de datos...")
        
        try:
            # 1. Cargar bancos (desde CSV o datos de prueba)
            self._load_bancos()
            
            # 2. Cargar casas de bolsa (desde CSV o datos de prueba)
            self._load_casas_bolsa()
            
            # 3. Cargar titulos (desde CSV o datos de prueba)
            self._load_titulos()
            
            # 4. Crear clientes de prueba
            self._create_clientes_prueba()
            
            # 5. Crear configuración básica
            #self._create_configuracion()
            
            self.session.commit()
            print("✅ Base de datos inicializada correctamente!")
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error: {str(e)}")
            raise
        finally:
            self.session.close()
    
    def _load_bancos(self):
        """Cargar bancos desde CSV o crear datos de prueba"""
        csv_path = Path(__file__).parent.parent / "data" / "bancos.csv"
        
        # Si existe CSV, cargarlo
        if csv_path.exists():
            print(f"📄 Cargando bancos desde {csv_path}...")
            bancos_creados = 0
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not self.session.query(BancoDB).filter_by(rif=row['rif']).first():
                        banco = BancoDB(
                            rif=row['rif'],
                            nombre=row['nombre'],
                            codigo=row['codigo']
                        )
                        self.session.add(banco)
                        bancos_creados += 1
            
            self.session.commit()
            print(f"✅ {bancos_creados} bancos cargados desde CSV")
            return
        
        # Si no hay CSV, crear datos de prueba
        print("📝 Creando bancos de prueba...")
        bancos_prueba = [
            {"rif": "J-00000000-0", "nombre": "Banco de Venezuela", "codigo": "0102"},
            {"rif": "J-00000001-1", "nombre": "Banco Mercantil", "codigo": "0105"},
            {"rif": "J-00000002-2", "nombre": "Banesco", "codigo": "0134"},
            {"rif": "J-00000003-3", "nombre": "Banco Provincial", "codigo": "0108"},
            {"rif": "J-00000004-4", "nombre": "Banco Bicentenario", "codigo": "0175"},
            {"rif": "J-00000005-5", "nombre": "Banco del Tesoro", "codigo": "0163"},
            {"rif": "J-00000006-6", "nombre": "Banco Venezolano de Crédito", "codigo": "0104"},
            {"rif": "J-00000007-7", "nombre": "Banco Exterior", "codigo": "0115"},
            {"rif": "J-00000008-8", "nombre": "Banco Plaza", "codigo": "0138"},
            {"rif": "J-00000009-9", "nombre": "100% Banco", "codigo": "0156"},
        ]
        
        for banco in bancos_prueba:
            if not self.session.query(BancoDB).filter_by(rif=banco["rif"]).first():
                banco_db = BancoDB(**banco)
                self.session.add(banco_db)
        
        self.session.commit()
        print(f"✅ {len(bancos_prueba)} bancos creados")
    
    def _load_casas_bolsa(self):
        """Cargar casas de bolsa desde CSV o crear datos de prueba"""
        csv_path = Path(__file__).parent.parent / "data" / "casas_bolsa.csv"
        
        # Si existe CSV, cargarlo
        if csv_path.exists():
            print(f"📄 Cargando casas de bolsa desde {csv_path}...")
            casas_creadas = 0
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not self.session.query(CasaBolsaDB).filter_by(rif=row['rif']).first():
                        casa = CasaBolsaDB(
                            rif=row['rif'],
                            nombre=row['nombre'],
                            sector=row.get('sector', 'Financiero'),
                            tipo=row.get('tipo', 'Casa de Bolsa')
                        )
                        self.session.add(casa)
                        casas_creadas += 1
            
            self.session.commit()
            print(f"✅ {casas_creadas} casas de bolsa cargadas desde CSV")
            return
        
        # Si no hay CSV, crear datos de prueba
        print("📝 Creando casas de bolsa de prueba...")
        casas_prueba = [
            {"rif": "J-30000000-0", "nombre": "Casa de Bolsa Mercantil", "sector": "Financiero", "tipo": "Casa de Bolsa"},
            {"rif": "J-30000001-1", "nombre": "Bancaribe Casa de Bolsa", "sector": "Financiero", "tipo": "Casa de Bolsa"},
            {"rif": "J-30000002-2", "nombre": "BOD Casa de Bolsa", "sector": "Financiero", "tipo": "Casa de Bolsa"},
            {"rif": "J-30000003-3", "nombre": "Banco de Venezuela Casa de Bolsa", "sector": "Financiero", "tipo": "Casa de Bolsa"},
            {"rif": "J-30000004-4", "nombre": "Caja Venezolana de Valores", "sector": "Financiero", "tipo": "CVV"},
            {"rif": "J-30000005-5", "nombre": "Eurocapital Casa de Bolsa", "sector": "Financiero", "tipo": "Casa de Bolsa"},
            {"rif": "J-30000006-6", "nombre": "Occidental Casa de Bolsa", "sector": "Financiero", "tipo": "Casa de Bolsa"},
            {"rif": "J-30000007-7", "nombre": "Global Casa de Bolsa", "sector": "Financiero", "tipo": "Casa de Bolsa"},
        ]
        
        for casa in casas_prueba:
            if not self.session.query(CasaBolsaDB).filter_by(rif=casa["rif"]).first():
                casa_db = CasaBolsaDB(**casa)
                self.session.add(casa_db)
        
        self.session.commit()
        print(f"✅ {len(casas_prueba)} casas de bolsa creadas")
    
    def _load_titulos(self):
        """Cargar titulos desde CSV o crear datos de prueba"""
        csv_path = Path(__file__).parent.parent / "data" / "titulos.csv"
        
        # Si existe CSV, cargarlo
        if csv_path.exists():
            print(f"📄 Cargando titulos desde {csv_path}...")
            titulos_creados = 0
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not self.session.query(TituloDB).filter_by(ticker=row['ticker']).first():
                        titulo = TituloDB(
                            rif=row['rif'],
                            nombre=row['nombre'],
                            ticker=row['ticker'],
                            tipo=row['tipo'],
                            sector=row.get('sector', 'General')
                        )
                        self.session.add(titulo)
                        titulos_creados += 1
            
            self.session.commit()
            print(f"✅ {titulos_creados} titulos cargados desde CSV")
            return
        
        # Si no hay CSV, crear datos de prueba
        print("📝 Creando titulos de prueba...")
        titulos_prueba = [
            {"rif": "J-50000000-0", "nombre": "Petróleos de Venezuela S.A.", "ticker": "PDVSA", "sector": "Petróleo y Gas"},
            {"rif": "J-50000001-1", "nombre": "Corporación Eléctrica Nacional", "ticker": "CORPOELEC", "sector": "Energía"},
            {"rif": "J-50000002-2", "nombre": "Cervecería Polar", "ticker": "POLAR", "sector": "Alimentos y Bebidas"},
            {"rif": "J-50000003-3", "nombre": "Empresas Polar", "ticker": "EMPOLAR", "sector": "Alimentos y Bebidas"},
            {"rif": "J-50000004-4", "nombre": "Banco Mercantil", "ticker": "BMERCANTIL", "sector": "Financiero"},
            {"rif": "J-50000005-5", "nombre": "Banesco Banco Universal", "ticker": "BANESCO", "sector": "Financiero"},
            {"rif": "J-50000006-6", "nombre": "Mercantil Servicios Financieros", "ticker": "MSF", "sector": "Financiero"},
            {"rif": "J-50000007-7", "nombre": "Teléfonos de Venezuela", "ticker": "CANTV", "sector": "Telecomunicaciones"},
            {"rif": "J-50000008-8", "nombre": "Mazda de Venezuela", "ticker": "MAZDA", "sector": "Automotriz"},
            {"rif": "J-50000009-9", "nombre": "Cemento Andino", "ticker": "CANDINO", "sector": "Construcción"},
        ]
        
        for titulo in titulos_prueba:
            if not self.session.query(TituloDB).filter_by(ticker=titulo["ticker"]).first():
                titulo_db = TituloDB(**titulo)
                self.session.add(titulo_db)
        
        self.session.commit()
        print(f"✅ {len(titulos_prueba)} titulos creados")
    
    def _create_clientes_prueba(self):
        """Crear 10 clientes de prueba con datos realistas"""
        print("👥 Creando clientes de prueba...")
        
        clientes_data = [
            # Clientes naturales
            {
                "nombre_completo": "Carlos José Rodríguez Pérez",
                "tipo_inversor": TipoInversor.NATURAL,
                "rif_cedula": "V-12345678-9",
                "telefono": "0414-1234567",
                "email": "carlos.rodriguez@email.com",
                "direccion_fiscal": "Av. Principal de Los Ruices, Edificio Centro Plaza, Piso 5, Oficina 501",
                "ciudad_estado": "Caracas, Distrito Capital",
                "fecha_vencimiento_rif": date.today() + timedelta(days=365),
            },
            {
                "nombre_completo": "María Elena González de López",
                "tipo_inversor": TipoInversor.NATURAL,
                "rif_cedula": "V-23456789-0",
                "telefono": "0424-2345678",
                "email": "maria.gonzalez@email.com",
                "direccion_fiscal": "Calle Los Jardines, Residencias El Paraíso, Torre B, Apto 12-B",
                "ciudad_estado": "Maracaibo, Zulia",
                "fecha_vencimiento_rif": date.today() + timedelta(days=300),
            },
            {
                "nombre_completo": "Juan Pablo Martínez Rojas",
                "tipo_inversor": TipoInversor.NATURAL,
                "rif_cedula": "V-34567890-1",
                "telefono": "0416-3456789",
                "email": "juan.martinez@email.com",
                "direccion_fiscal": "Urbanización La Floresta, Calle Los Pinos, Casa N° 45",
                "ciudad_estado": "Valencia, Carabobo",
                "fecha_vencimiento_rif": date.today() + timedelta(days=400),
            },
            # Clientes jurídicos
            {
                "nombre_completo": "Inversiones C.A. El Futuro",
                "tipo_inversor": TipoInversor.JURIDICA,
                "rif_cedula": "J-12345678-0",
                "telefono": "0212-5551234",
                "email": "info@inversioneselfuturo.com",
                "direccion_fiscal": "Centro Comercial Sambil, Nivel Oficinas, Local O-12",
                "ciudad_estado": "Caracas, Distrito Capital",
                "fecha_vencimiento_rif": date.today() + timedelta(days=200),
            },
            {
                "nombre_completo": "Constructora Edifica C.A.",
                "tipo_inversor": TipoInversor.JURIDICA,
                "rif_cedula": "J-23456789-1",
                "telefono": "0241-5555678",
                "email": "contacto@constructoraedifica.com",
                "direccion_fiscal": "Zona Industrial Norte, Galpón N° 7",
                "ciudad_estado": "Valencia, Carabobo",
                "fecha_vencimiento_rif": date.today() + timedelta(days=180),
            },
            {
                "nombre_completo": "Distribuidora de Alimentos La Prosperidad C.A.",
                "tipo_inversor": TipoInversor.JURIDICA,
                "rif_cedula": "J-34567890-2",
                "telefono": "0261-5559012",
                "email": "ventas@laprosperidad.com",
                "direccion_fiscal": "Av. Circunvalación N° 2, Edificio Industrial, Piso 3",
                "ciudad_estado": "Maracay, Aragua",
                "fecha_vencimiento_rif": date.today() + timedelta(days=220),
            },
            # Más clientes
            {
                "nombre_completo": "Ana Isabel Contreras Salazar",
                "tipo_inversor": TipoInversor.NATURAL,
                "rif_cedula": "V-45678901-2",
                "telefono": "0412-4567890",
                "email": "ana.contreras@email.com",
                "direccion_fiscal": "Urbanización El Recreo, Calle Los Olivos, Residencia Los Geranios",
                "ciudad_estado": "Barquisimeto, Lara",
                "fecha_vencimiento_rif": date.today() + timedelta(days=320),
            },
            {
                "nombre_completo": "Luis Fernando Díaz Mendoza",
                "tipo_inversor": TipoInversor.NATURAL,
                "rif_cedula": "V-56789012-3",
                "telefono": "0426-5678901",
                "email": "luis.diaz@email.com",
                "direccion_fiscal": "Conjunto Residencial Los Caobos, Torre 2, Apto 804",
                "ciudad_estado": "Puerto La Cruz, Anzoátegui",
                "fecha_vencimiento_rif": date.today() + timedelta(days=280),
            },
            {
                "nombre_completo": "Consultores Asociados S.C.",
                "tipo_inversor": TipoInversor.JURIDICA,
                "rif_cedula": "J-45678901-3",
                "telefono": "0212-7778888",
                "email": "consultores@consultoresasociados.com",
                "direccion_fiscal": "Torre Financiera, Av. Francisco de Miranda, Piso 15",
                "ciudad_estado": "Caracas, Distrito Capital",
                "fecha_vencimiento_rif": date.today() + timedelta(days=240),
            },
            {
                "nombre_completo": "Importadora Exportadora Global Trade C.A.",
                "tipo_inversor": TipoInversor.JURIDICA,
                "rif_cedula": "J-56789012-4",
                "telefono": "0286-5553333",
                "email": "info@globaltrade.com",
                "direccion_fiscal": "Zona Franca Industrial, Módulo 12",
                "ciudad_estado": "Puerto Cabello, Carabobo",
                "fecha_vencimiento_rif": date.today() + timedelta(days=260),
            }
        ]
        
        # Obtener bancos y casas de bolsa disponibles
        bancos = self.session.query(BancoDB).all()
        casas_bolsa = self.session.query(CasaBolsaDB).all()
        
        clientes_creados = 0
        
        for i, cliente_data in enumerate(clientes_data):
            # Verificar si ya existe
            if self.session.query(ClienteDB).filter_by(rif_cedula=cliente_data["rif_cedula"]).first():
                continue
            
            # Crear cliente
            cliente = ClienteDB(**cliente_data)
            self.session.add(cliente)
            self.session.flush()  # Para obtener el ID
            
            # Asignar 1-3 cuentas bancarias
            num_cuentas_banco = random.randint(1, 3)
            bancos_seleccionados = random.sample(bancos, min(num_cuentas_banco, len(bancos)))
            
            for j, banco in enumerate(bancos_seleccionados):
                cuenta = CuentaBancariaDB(
                    cliente_id=cliente.id,
                    banco_id=banco.id,
                    numero_cuenta=f"0192-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    tipo_cuenta=random.choice(["Corriente", "Ahorros", "Nómina"]),
                    default=(j == 0)  # La primera es la principal
                )
                self.session.add(cuenta)
            
            # Asignar 1-2 cuentas bursátiles
            num_cuentas_bursatil = random.randint(1, 2)
            casas_seleccionadas = random.sample(casas_bolsa, min(num_cuentas_bursatil, len(casas_bolsa)))
            
            for k, casa in enumerate(casas_seleccionadas):
                cuenta_bursatil = CuentaBursatilDB(
                    cliente_id=cliente.id,
                    casa_bolsa_id=casa.id,
                    cuenta=f"CB-{cliente.id:04d}-{casa.id:03d}-{random.randint(1000, 9999)}",
                    default=(k == 0)  # La primera es la principal
                )
                self.session.add(cuenta_bursatil)
            
            # Agregar algunos documentos de ejemplo
            tipos_documento = ["Cédula", "RIF", "Estados de Cuenta", "Declaración Patrimonial"]
            
            for tipo_doc in random.sample(tipos_documento, random.randint(1, 3)):
                documento = DocumentoDB(
                    cliente_id=cliente.id,
                    tipo_documento=tipo_doc,
                    nombre_archivo=f"{tipo_doc.lower().replace(' ', '_')}_{cliente.rif_cedula}.pdf",
                    ruta_archivo=f"/documentos/clientes/{cliente.id}/{tipo_doc.lower().replace(' ', '_')}.pdf",
                    verificado=random.choice([True, False])
                )
                self.session.add(documento)
            
            clientes_creados += 1
        
        self.session.commit()
        print(f"✅ {clientes_creados} clientes de prueba creados con cuentas y documentos")


def init_database():
    """Función principal para inicializar la base de datos"""
    initializer = DataInitializer()
    initializer.run()


if __name__ == "__main__":
    init_database()