import logging
from decimal import Decimal
from src.bvc_gestor.database.engine import get_database
from src.bvc_gestor.services.orden_service import OrdenService
from src.bvc_gestor.services.portfolio_service import PortfolioService

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("TEST-SISTEMA")

def ejecutar_ciclo_completo():
    db_manager = get_database()
    session = db_manager.get_session()
    
    try:
        # 1. SERVICIOS
        orden_service = OrdenService(session)
        portfolio_service = PortfolioService(session)
        
        logger.info("--- 1. ESTADO INICIAL ---")
        resumen = portfolio_service.obtener_resumen_cliente(cliente_id=1)
        logger.info(f"Disponible: {resumen['saldo_disponible']} Bs | Patrimonio: {resumen['patrimonio_total']} Bs")

        # 2. CREAR ORDEN (BLOQUEO DE FONDOS)
        logger.info("\n--- 2. CREANDO ORDEN DE COMPRA (1000 BNC) ---")
        orden = orden_service.ejecutar_orden_compra(
            cliente_id=1, cuenta_id=1, activo_id="BNC", 
            cantidad=1000, precio=Decimal("0.0050")
        )
        session.refresh(orden)
        
        resumen_mid = portfolio_service.obtener_resumen_cliente(1)
        logger.info(f"Estado Orden: {orden.estado}")
        logger.info(f"Disponible tras bloqueo: {resumen_mid['saldo_disponible']} Bs")
        logger.info(f"Bloqueado por orden: {resumen_mid['saldo_bloqueado']} Bs")

        # 3. EJECUCIÓN (SIMULACIÓN DE MERCADO)
        logger.info("\n--- 3. PROCESANDO EJECUCIÓN DE MERCADO ---")
        ejecutadas = orden_service.procesar_ordenes_pendientes()
        logger.info(f"Órdenes procesadas con éxito: {ejecutadas}")

        # 4. RESULTADO FINAL EN PORTAFOLIO
        logger.info("\n--- 4. ESTADO FINAL DEL INVERSIONISTA ---")
        resumen_final = portfolio_service.obtener_resumen_cliente(1)
        
        logger.info(f"Nuevo Saldo Disponible: {resumen_final['saldo_disponible']} Bs")
        logger.info(f"Valor en Acciones: {resumen_final['valor_en_titulos']} Bs")
        logger.info(f"Patrimonio Total: {resumen_final['patrimonio_total']} Bs")
        
        for activo in resumen_final['activos']:
            logger.info(f"   > Posee: {activo['cantidad']} de {activo['activo']} | P&L: {activo['pnl_pct']:.2f}%")

    except Exception as e:
        logger.error(f"Error en el ciclo: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    ejecutar_ciclo_completo()