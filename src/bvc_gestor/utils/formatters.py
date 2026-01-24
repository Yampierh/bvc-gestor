# src/bvc_gestor/utils/formatters.py
"""
Utilidades para formatear datos para la UI.
Mantiene consistencia en cómo se muestran los datos en toda la aplicación.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataFormatter:
    """
    Clase estática para formatear datos de manera consistente.
    No necesita instanciarse, solo usa los métodos estáticos.
    """
    
    # ==================== INVERSORES ====================
    
    @staticmethod
    def format_inversor(inversor: Dict) -> str:
        """
        Formatea un inversor para combobox.
        
        Args:
            inversor: Diccionario con datos del inversor
        
        Returns:
            str: Texto formateado para mostrar
        """
        try:
            nombre = inversor.get('nombre_completo', 'Sin nombre').strip()
            cedula = inversor.get('rif_cedula', 'Sin cédula').strip()
            
            if not nombre or nombre == 'Sin nombre':
                return f"ID: {inversor.get('id', '?')} - {cedula}"
            
            return f"{nombre} - {cedula}"
            
        except Exception as e:
            logger.error(f"Error formateando inversor: {e}")
            return f"Inversor ID: {inversor.get('id', '?')}"
    
    @staticmethod
    def format_inversor_simple(inversor: Dict) -> str:
        """Versión más simple, solo nombre"""
        nombre = inversor.get('nombre_completo', 'Sin nombre').strip()
        return nombre if nombre else f"ID: {inversor.get('id', '?')}"
    
    # ==================== CUENTAS BANCARIAS ====================
    
    @staticmethod
    def format_cuenta_bancaria(
        cuenta: Dict, 
        banco_nombre: Optional[str] = None,
        enmascarar: bool = True
    ) -> str:
        """
        Formatea cuenta bancaria para combobox.
        
        Args:
            cuenta: Diccionario con datos de la cuenta
            banco_nombre: Nombre del banco (opcional)
            enmascarar: Si True, enmascara el número
        
        Returns:
            str: Texto formateado para mostrar
        """
        try:
            numero = str(cuenta.get('numero_cuenta', '')).strip()
            
            # Enmascarar número si está habilitado
            if enmascarar:
                numero_display = DataFormatter.enmascarar_numero_cuenta(numero)
            else:
                numero_display = numero if numero else "Sin número"
            
            # Usar nombre del banco si está disponible
            if banco_nombre:
                banco_display = banco_nombre.strip()
            else:
                banco_id = cuenta.get('banco_id', '?')
                banco_display = f"Banco {banco_id}"
            
            # Formato: "Banco - ****1234"
            return f"{banco_display} - {numero_display}"
            
        except Exception as e:
            logger.error(f"Error formateando cuenta bancaria: {e}")
            return f"Cuenta ID: {cuenta.get('id', '?')}"
    
    @staticmethod
    def get_cuenta_bancaria_tooltip(cuenta: Dict, banco_nombre: str = None) -> str:
        """Genera tooltip para cuenta bancaria"""
        try:
            numero = cuenta.get('numero_cuenta', 'N/A')
            tipo = cuenta.get('tipo_cuenta', 'N/A')
            banco = banco_nombre or f"Banco {cuenta.get('banco_id', '?')}"
            
            return (f"📋 Información de Cuenta\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🏦 Banco: {banco}\n"
                    f"🔢 Número: {numero}\n"
                    f"📝 Tipo: {tipo}\n"
                    f"👤 Cliente ID: {cuenta.get('cliente_id', 'N/A')}")
        except Exception as e:
            logger.error(f"Error generando tooltip: {e}")
            return "Información no disponible"
    
    # ==================== CUENTAS BURSÁTILES ====================
    
    @staticmethod
    def format_cuenta_bursatil(
        cuenta: Dict, 
        casa_nombre: Optional[str] = None
    ) -> str:
        """
        Formatea cuenta bursátil para combobox.
        
        Args:
            cuenta: Diccionario con datos de la cuenta
            casa_nombre: Nombre de la casa de bolsa (opcional)
        
        Returns:
            str: Texto formateado para mostrar
        """
        try:
            numero = str(cuenta.get('cuenta', 'Sin número')).strip()
            
            # Usar nombre de la casa si está disponible
            if casa_nombre:
                casa_display = casa_nombre.strip()
            else:
                casa_id = cuenta.get('casa_bolsa_id', '?')
                casa_display = f"Casa {casa_id}"
            
            # Formato: "Casa de Bolsa - Número"
            return f"{casa_display} - {numero}"
            
        except Exception as e:
            logger.error(f"Error formateando cuenta bursátil: {e}")
            return f"Cuenta ID: {cuenta.get('id', '?')}"
    
    @staticmethod
    def get_cuenta_bursatil_tooltip(cuenta: Dict, casa_nombre: str = None) -> str:
        """Genera tooltip para cuenta bursátil"""
        try:
            numero = cuenta.get('cuenta', 'N/A')
            casa = casa_nombre or f"Casa {cuenta.get('casa_bolsa_id', '?')}"
            
            return (f"📈 Información de Cuenta Bursátil\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🏢 Casa de Bolsa: {casa}\n"
                    f"🔢 Número: {numero}\n"
                    f"👤 Cliente ID: {cuenta.get('cliente_id', 'N/A')}\n"
                    f"⭐ Principal: {'Sí' if cuenta.get('default') else 'No'}")
        except Exception as e:
            logger.error(f"Error generando tooltip: {e}")
            return "Información no disponible"
    
    # ==================== UTILIDADES GENERALES ====================
    
    @staticmethod
    def enmascarar_numero_cuenta(
        numero: str, 
        mostrar_ultimos: int = 4, 
        caracter_enmascarado: str = "*"
    ) -> str:
        """
        Enmascara un número de cuenta.
        
        Args:
            numero: Número a enmascarar
            mostrar_ultimos: Cuántos dígitos mostrar al final
            caracter_enmascarado: Carácter para enmascarar
        
        Returns:
            str: Número enmascarado
        """
        if not numero:
            return "Sin número"
        
        numero = str(numero).strip()
        
        if len(numero) <= mostrar_ultimos:
            return numero
        
        # Crear máscara
        mascara = caracter_enmascarado * (len(numero) - mostrar_ultimos)
        ultimos_digitos = numero[-mostrar_ultimos:]
        
        return f"{mascara}{ultimos_digitos}"
    
    @staticmethod
    def format_moneda(monto: float, simbolo: str = "Bs.", decimales: int = 2) -> str:
        """Formatea un monto de dinero"""
        try:
            return f"{simbolo} {monto:,.{decimales}f}"
        except:
            return f"{simbolo} 0.00"
    
    @staticmethod
    def format_fecha(fecha_str: str) -> str:
        """Formatea una fecha ISO a formato legible"""
        try:
            from datetime import datetime
            fecha = datetime.fromisoformat(fecha_str.replace('Z', ''))
            return fecha.strftime("%d/%m/%Y %H:%M")
        except:
            return fecha_str
    
    @staticmethod
    def format_estado_orden(estado: str) -> tuple:
        """
        Formatea el estado de una orden.
        
        Returns:
            tuple: (texto, color_css, clase_css)
        """
        estados = {
            'PENDIENTE': ('⏳ Pendiente', '#FF9800', 'badgeWarning'),
            'EJECUTADA': ('✅ Ejecutada', '#4CAF50', 'badgeSuccess'),
            'CANCELADA': ('❌ Cancelada', '#F44336', 'badgeDanger'),
            'ESPERANDO_FONDOS': ('💰 Esperando Fondos', '#2196F3', 'badgeInfo'),
        }
        
        return estados.get(estado.upper(), (estado, '#757575', 'badgeDefault'))