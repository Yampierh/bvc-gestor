# src/bvc_gestor/utils/calculos_financieros.py
"""
Utilidades para cálculos financieros específicos de BVC
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

def calcular_comision_bvc(
    monto: Decimal,
    tipo_operacion: str = "normal",
    comision_base: Decimal = Decimal('0.005'),  # 0.5%
    iva: Decimal = Decimal('0.16'),  # 16%
    comision_minima: Decimal = Decimal('1.00'),
    comision_maxima: Decimal = Decimal('1000.00')
) -> Dict[str, Decimal]:
    """
    Calcular comisiones BVC según reglas venezolanas
    
    Args:
        monto: Monto de la operación
        tipo_operacion: "normal", "especial", "internacional"
        comision_base: Porcentaje base de comisión
        iva: Porcentaje de IVA
        comision_minima: Comisión mínima aplicable
        comision_maxima: Comisión máxima aplicable
    
    Returns:
        Dict con comisión base, IVA y total
    """
    if monto <= 0:
        return {
            'comision_base': Decimal('0.00'),
            'iva': Decimal('0.00'),
            'comision_total': Decimal('0.00')
        }
    
    # Ajustar comisión según tipo de operación
    if tipo_operacion == "especial":
        comision_base *= Decimal('0.8')  # 20% descuento
    elif tipo_operacion == "internacional":
        comision_base *= Decimal('1.2')  # 20% recargo
    
    # Calcular comisión base
    comision = monto * comision_base
    
    # Aplicar límites
    if comision < comision_minima:
        comision = comision_minima
    elif comision > comision_maxima:
        comision = comision_maxima
    
    # Calcular IVA
    iva_calculado = comision * iva
    
    # Calcular total
    total = comision + iva_calculado
    
    # Redondear a 2 decimales
    comision = comision.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    iva_calculado = iva_calculado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return {
        'comision_base': comision,
        'iva': iva_calculado,
        'comision_total': total
    }

def calcular_monto_total_orden(
    cantidad: int,
    precio_unitario: Decimal,
    tipo_orden: str = "Compra"
) -> Decimal:
    """
    Calcular monto total de una orden
    
    Args:
        cantidad: Número de acciones/títulos
        precio_unitario: Precio por unidad
        tipo_orden: "Compra" o "Venta"
    
    Returns:
        Monto total (positivo para compra, negativo para venta)
    """
    monto = Decimal(cantidad) * precio_unitario
    
    if tipo_orden == "Venta":
        monto = -monto  # Monto negativo para ventas
    
    return monto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def validar_limites_cliente(
    monto_operacion: Decimal,
    moneda: str,
    limite_inversion: Decimal,
    saldo_disponible: Decimal,
    perfil_riesgo: str = "Moderado"
) -> Tuple[bool, str]:
    """
    Validar si un cliente puede realizar una operación
    
    Args:
        monto_operacion: Monto de la operación (positivo para compra)
        moneda: "USD" o "Bs"
        limite_inversion: Límite configurado para el cliente
        saldo_disponible: Saldo disponible en la cuenta
        perfil_riesgo: Perfil de riesgo del cliente
    
    Returns:
        (es_valido, mensaje_error)
    """
    monto_absoluto = abs(monto_operacion)
    
    # 1. Validar límite de inversión
    if monto_absoluto > limite_inversion:
        return False, f"Supera límite de inversión ({moneda} {limite_inversion:,.2f})"
    
    # 2. Validar saldo disponible (solo para compras)
    if monto_operacion > 0:  # Compra
        if monto_operacion > saldo_disponible:
            return False, f"Saldo insuficiente. Disponible: {moneda} {saldo_disponible:,.2f}"
    
    # 3. Validaciones adicionales según perfil de riesgo
    if perfil_riesgo == "Conservador":
        # Límites más estrictos para conservadores
        max_porcentaje_portafolio = Decimal('0.10')  # 10% máximo por operación
        if monto_absoluto > limite_inversion * max_porcentaje_portafolio:
            return False, "Operación muy grande para perfil conservador"
    
    elif perfil_riesgo == "Agresivo":
        # Mayor tolerancia para agresivos
        # Podrían permitirse operaciones más grandes
        pass
    
    return True, "Operación válida"

def calcular_rendimiento(
    precio_compra: Decimal,
    precio_actual: Decimal,
    cantidad: int,
    comisiones_pagadas: Decimal = Decimal('0.00')
) -> Dict[str, Any]:
    """
    Calcular rendimiento de una inversión
    
    Returns:
        Dict con ganancia/pérdida absoluta y porcentual
    """
    inversion_total = precio_compra * Decimal(cantidad) + comisiones_pagadas
    valor_actual = precio_actual * Decimal(cantidad)
    
    ganancia_perdida = valor_actual - inversion_total
    rendimiento_porcentual = (ganancia_perdida / inversion_total) * Decimal('100') if inversion_total > 0 else Decimal('0.00')
    
    return {
        'inversion_total': inversion_total.quantize(Decimal('0.01')),
        'valor_actual': valor_actual.quantize(Decimal('0.01')),
        'ganancia_perdida': ganancia_perdida.quantize(Decimal('0.01')),
        'rendimiento_porcentual': rendimiento_porcentual.quantize(Decimal('0.01')),
        'rentabilidad': "Ganancia" if ganancia_perdida >= 0 else "Pérdida"
    }

def simular_ejecucion_orden(
    tipo_orden: str,
    cantidad: int,
    precio_solicitado: Decimal,
    precio_mercado: Decimal,
    spread: Decimal = Decimal('0.01')  # 1% spread típico
) -> Dict[str, Any]:
    """
    Simular ejecución de una orden en el mercado
    
    Args:
        tipo_orden: "Compra" o "Venta"
        cantidad: Cantidad solicitada
        precio_solicitado: Precio de la orden (None para mercado)
        precio_mercado: Precio actual de mercado
        spread: Spread promedio del mercado
    
    Returns:
        Dict con resultados de la simulación
    """
    if tipo_orden == "Compra":
        # Para compras, el precio de ejecución podría ser mayor al solicitado
        if precio_solicitado:
            # Orden limitada de compra
            if precio_solicitado >= precio_mercado:
                precio_ejecucion = precio_mercado
                probabilidad = 0.9  # Alta probabilidad de ejecución
            else:
                precio_ejecucion = precio_solicitado
                probabilidad = 0.3  # Baja probabilidad (precio muy bajo)
        else:
            # Orden de mercado de compra
            precio_ejecucion = precio_mercado * (Decimal('1') + spread)
            probabilidad = 1.0  # Seguro de ejecución
    
    else:  # Venta
        if precio_solicitado:
            # Orden limitada de venta
            if precio_solicitado <= precio_mercado:
                precio_ejecucion = precio_mercado
                probabilidad = 0.9
            else:
                precio_ejecucion = precio_solicitado
                probabilidad = 0.3
        else:
            # Orden de mercado de venta
            precio_ejecucion = precio_mercado * (Decimal('1') - spread)
            probabilidad = 1.0
    
    monto_total = Decimal(cantidad) * precio_ejecucion
    
    return {
        'precio_ejecucion': precio_ejecucion.quantize(Decimal('0.0001')),
        'monto_total': monto_total.quantize(Decimal('0.01')),
        'probabilidad_ejecucion': round(probabilidad, 2),
        'tiempo_estimado_minutos': 5 if probabilidad > 0.8 else 30,
        'comentario': "Ejecución inmediata" if probabilidad == 1.0 else "Ejecución posible"
    }

def convertir_moneda(
    monto: Decimal,
    moneda_origen: str,
    moneda_destino: str,
    tasa_cambio: Decimal
) -> Decimal:
    """
    Convertir montos entre monedas (USD <-> Bs)
    
    Args:
        monto: Monto a convertir
        moneda_origen: "USD" o "Bs"
        moneda_destino: "USD" o "Bs"
        tasa_cambio: Tasa USD/Bs
    
    Returns:
        Monto convertido
    """
    if moneda_origen == moneda_destino:
        return monto
    
    if moneda_origen == "USD" and moneda_destino == "Bs":
        return monto * tasa_cambio
    elif moneda_origen == "Bs" and moneda_destino == "USD":
        return monto / tasa_cambio
    else:
        raise ValueError(f"Conversión no soportada: {moneda_origen} -> {moneda_destino}")