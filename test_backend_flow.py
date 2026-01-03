import logging
from decimal import Decimal
from src.bvc_gestor.database.engine import get_database
from src.bvc_gestor.database.repositories import RepositoryFactory
from src.bvc_gestor.services.orden_service import OrdenService
from src.bvc_gestor.utils.constants import Moneda

# Configuración de logs para ver qué pasa "bajo el capó"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST-BACKEND")

def probrar_flujo_compra():
    # 1. Inicializar conexión
    db_manager = get_database()
    session = db_manager.get_session()
    
    try:
        logger.info("=== INICIANDO PRUEBA DE BACKEND ===")
        
        # 2. Obtener datos del seed (Juan Pérez)
        # Usamos el repositorio para buscar la cuenta que creamos en el seed
        cuenta_repo = RepositoryFactory.get_repository(session, 'cuenta')
        todas_las_cuentas = cuenta_repo.get_by_cliente(1) # Asumiendo ID 1 para Juan
        
        if not todas_las_cuentas:
            logger.error("No se encontró la cuenta del seed. ¿Corriste el seed_data.py?")
            return

        cuenta = todas_las_cuentas[0]
        saldo_inicial = cuenta.saldo_disponible_bs
        logger.info(f"Cliente: Juan Pérez | Saldo Inicial: {saldo_inicial} Bs")

        # 3. Inicializar el Servicio de Órdenes
        # Le pasamos la sesión activa
        servicio = OrdenService(session)

        # 4. Intentar una compra de 1000 acciones de BNC a 0.0050
        logger.info("Intentando crear orden: Compra 1000 BNC @ 0.0050 Bs...")
        
        nueva_orden = servicio.ejecutar_orden_compra(
            cliente_id=cuenta.cliente_id,
            cuenta_id=cuenta.id,
            activo_id="BNC",
            cantidad=1000,
            precio=Decimal("0.0050")
        )

        # 5. Verificar Resultados
        # Refrescamos el objeto cuenta para ver el cambio de saldo tras el commit
        session.refresh(cuenta)
        
        logger.info(f"✅ ORDEN CREADA: {nueva_orden.numero_orden}")
        logger.info(f"📊 NUEVO ESTADO DE CUENTA:")
        logger.info(f"   - Saldo Disponible: {cuenta.saldo_disponible_bs} Bs")
        logger.info(f"   - Saldo Bloqueado:   {cuenta.saldo_bloqueado_bs} Bs")
        
        # El saldo total debería seguir siendo el mismo (Disponible + Bloqueado)
        total = cuenta.saldo_disponible_bs + cuenta.saldo_bloqueado_bs
        logger.info(f"   - Saldo Total (Patrimonio): {total} Bs")

    except Exception as e:
        logger.error(f"❌ LA PRUEBA FALLÓ: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    probrar_flujo_compra()