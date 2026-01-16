# 📊 PLAN COMPLETO Y DETALLADO
## Módulo de Operaciones - BVC Gestor

---

## 🎯 OBJETIVO GENERAL
Implementar un módulo completo de gestión de operaciones bursátiles (compra/venta de acciones) en la Bolsa de Valores de Caracas, integrado al sistema existente, con manejo de fondos, generación de reportes PDF y seguimiento completo del ciclo de vida de las operaciones.

---

## 📐 ARQUITECTURA DEL MÓDULO

### Estructura de Archivos
```
src/bvc_gestor/
│
├── controllers/
│   └── operaciones_controller.py          [NUEVO]
│
├── database/
│   └── models_sql.py                      [MODIFICAR]
│
├── services/
│   ├── operaciones_service.py             [NUEVO]
│   ├── scraper_bvc_service.py             [NUEVO]
│   ├── calculadora_service.py             [NUEVO]
│   └── movimientos_service.py             [NUEVO]
│
├── reports/
│   ├── generators/
│   │   ├── deposito_generator.py          [NUEVO]
│   │   ├── venta_rendimiento_generator.py [NUEVO]
│   │   └── comprobante_operacion.py       [NUEVO]
│   └── templates/
│       └── pdf/
│           ├── instruccion_deposito.html  [NUEVO]
│           ├── reporte_venta.html         [NUEVO]
│           └── comprobante_orden.html     [NUEVO]
│
├── ui/
│   ├── views/
│   │   ├── operaciones_module.py          [NUEVO]
│   │   ├── operaciones_dashboard.py       [NUEVO]
│   │   ├── operaciones_list_view.py       [NUEVO]
│   │   └── portafolio_view.py             [NUEVO]
│   │
│   ├── dialogs/
│   │   ├── nueva_compra_dialog.py         [NUEVO]
│   │   ├── nueva_venta_dialog.py          [NUEVO]
│   │   ├── solicitud_deposito_dialog.py   [NUEVO]
│   │   ├── confirmar_deposito_dialog.py   [NUEVO]
│   │   ├── detalle_operacion_dialog.py    [NUEVO]
│   │   └── actualizar_precios_dialog.py   [NUEVO]
│   │
│   └── widgets/
│       ├── operacion_card_widget.py       [NUEVO]
│       ├── ticker_search_widget.py        [NUEVO]
│       ├── calculadora_comisiones.py      [NUEVO]
│       ├── saldo_widget.py                [NUEVO]
│       └── estado_orden_badge.py          [NUEVO]
│
├── utils/
│   ├── formatters.py                      [NUEVO]
│   └── constants.py                       [MODIFICAR]
│
└── data/
    └── tickers_bvc.csv                    [NUEVO]
```

---

## 🗄️ BASE DE DATOS

### Tablas Existentes (A Mantener)
✅ **ClienteDB** - Inversores registrados
✅ **BancoDB** - Bancos venezolanos
✅ **CasaBolsaDB** - Casas de bolsa
✅ **CuentaBancariaDB** - Cuentas bancarias de clientes
✅ **CuentaBursatilDB** - Cuentas en casas de bolsa
✅ **ActivoDB** - Tickers de la BVC
✅ **DocumentoDB** - Documentos de clientes (Fase 2)
✅ **ConfiguracionDB** - Configuraciones generales (Fase 2)

### Tablas a Modificar

#### 1. **ActivoDB** (Agregar campos)
```python
# CAMPOS NUEVOS:
precio_actual: Mapped[Decimal]                    # Último precio conocido
fecha_actualizacion_precio: Mapped[datetime]      # Cuándo se actualizó
mercado: Mapped[str]                              # 'Acciones', 'Bonos', 'ETF'
estado_mercado: Mapped[bool]                      # Activo/Suspendido
```

#### 2. **SaldoDB** (Refactorizar)
```python
# CAMPOS ACTUALES:
disponible: Mapped[Decimal]      # Saldo que puede usar YA
en_transito: Mapped[Decimal]     # Depósitos pendientes de confirmar
bloqueado: Mapped[Decimal]       # Comprometido en órdenes pendientes

# PROPIEDAD CALCULADA:
@property
def saldo_proyectado(self) -> Decimal:
    return self.disponible + self.en_transito - self.bloqueado
```

#### 3. **OrdenDB** (Agregar campos)
```python
# CAMPOS NUEVOS:
cuenta_bancaria_id: Mapped[int]           # De dónde salen/entran fondos
observaciones: Mapped[Optional[str]]      # Notas del usuario
comision_estimada: Mapped[Decimal]        # Comisión calculada al crear
monto_total_estimado: Mapped[Decimal]     # Total con comisiones

# CAMBIAR:
activo_id: ForeignKey("activos.id")       # Era ticker, ahora ID
```

#### 4. **MovimientoDB** (Refactorizar completo)
```python
class MovimientoDB(Base, AuditMixin):
    __tablename__ = "movimientos"
    
    id: Mapped[int]
    cuenta_bursatil_id: Mapped[int] = ForeignKey("cuentas_bursatiles.id")
    cuenta_bancaria_id: Mapped[int] = ForeignKey("cuentas_bancarias.id")
    
    tipo: Mapped[TipoMovimiento]              # DEPOSITO, RETIRO, COMISION, DIVIDENDO
    monto: Mapped[Decimal]
    moneda: Mapped[str] = 'VES'
    
    estado: Mapped[EstadoMovimiento]          # PENDIENTE, EN_TRANSITO, COMPLETADO, RECHAZADO
    
    fecha_solicitud: Mapped[datetime]
    fecha_completado: Mapped[Optional[datetime]]
    
    referencia_bancaria: Mapped[Optional[str]]    # Número de transferencia
    comprobante_ruta: Mapped[Optional[str]]       # Ruta del comprobante PDF/imagen
    observaciones: Mapped[Optional[str]]
    tasa_bcv: Mapped[Decimal]
    
    # Relaciones
    cuenta_bursatil = relationship("CuentaBursatilDB")
    cuenta_bancaria = relationship("CuentaBancariaDB")
```

### Tablas Nuevas

#### 5. **PrecioActualDB** (Nueva)
```python
class PrecioActualDB(Base, AuditMixin):
    """Precio actual y datos de mercado en tiempo real"""
    __tablename__ = "precios_actuales"
    
    id: Mapped[int]
    activo_id: Mapped[str] = ForeignKey("activos.ticker")
    
    precio: Mapped[Decimal]
    volumen: Mapped[int]                      # Volumen del día
    variacion: Mapped[Decimal]                # % de cambio
    precio_apertura: Mapped[Decimal]
    precio_maximo: Mapped[Decimal]
    precio_minimo: Mapped[Decimal]
    
    fecha_hora: Mapped[datetime]              # Timestamp de actualización
    fuente: Mapped[str]                       # 'SCRAPING_BVC', 'MANUAL'
```

#### 6. **OrdenMovimientoDB** (Nueva)
```python
class OrdenMovimientoDB(Base, AuditMixin):
    """Relación entre órdenes y movimientos de fondos"""
    __tablename__ = "ordenes_movimientos"
    
    id: Mapped[int]
    orden_id: Mapped[int] = ForeignKey("ordenes.id")
    movimiento_id: Mapped[int] = ForeignKey("movimientos.id")
    tipo_relacion: Mapped[str]  # 'DEPOSITO_PARA_COMPRA', 'RETIRO_POST_VENTA'
```

### Enums a Agregar en constants.py

```python
class TipoMovimiento(Enum):
    DEPOSITO = "Deposito"
    RETIRO = "Retiro"
    COMISION = "Comision"
    DIVIDENDO = "Dividendo"

class EstadoMovimiento(Enum):
    PENDIENTE = "Pendiente"           # Registrado pero no confirmado
    EN_TRANSITO = "En Tránsito"       # Transferencia en proceso
    COMPLETADO = "Completado"         # Ya reflejado en cuenta
    RECHAZADO = "Rechazado"           # La transferencia falló

class EstadoOrden(Enum):  # ACTUALIZAR el existente
    BORRADOR = "Borrador"
    ESPERANDO_FONDOS = "Esperando Fondos"     # NUEVO
    PENDIENTE = "Pendiente"
    PARCIALMENTE_EJECUTADA = "Parcialmente Ejecutada"
    EJECUTADA = "Ejecutada"
    CANCELADA = "Cancelada"
    RECHAZADA = "Rechazada"
```

---

## 🔄 FLUJOS DE OPERACIÓN

### FLUJO 1: Compra de Acciones con Fondos Existentes

```
Usuario → Nueva Compra Dialog
  ↓
[PASO 1: Selección de Inversor y Cuenta]
  - Combo: Inversor
  - Combo: Cuenta Bursátil (filtrada por inversor)
  - Combo: Cuenta Bancaria (para vincular origen)
  ↓
[PASO 2: Detalles de la Operación]
  - Widget búsqueda: Ticker (autocomplete)
  - Input: Cantidad de acciones
  - Combo: Tipo de orden (Mercado / Límite)
  - Input: Precio límite (si aplica)
  - Date: Vigencia
  ↓
[PASO 3: Confirmación]
  - Mostrar resumen de la operación
  - Calculadora en tiempo real:
    * Subtotal: cantidad × precio
    * Comisión corretaje: X%
    * Comisión BVC: Y%
    * Comisión CVV: Z%
    * IVA: 16%
    * TOTAL: Bs. XX,XXX.XX
  ↓
Sistema verifica: SaldoDB.disponible >= monto_total
  ↓
SI HAY FONDOS:
  ✅ Crear OrdenDB con estado=PENDIENTE
  ✅ SaldoDB: disponible -= monto_total
  ✅ SaldoDB: bloqueado += monto_total
  ✅ Mostrar confirmación
  ✅ Generar PDF comprobante de orden
  
NO HAY FONDOS:
  ❌ Mostrar: "Saldo insuficiente"
  ❌ Botón: "Solicitar Depósito" → FLUJO 2
```

### FLUJO 2: Compra con Solicitud de Depósito

```
Usuario hace clic en "Solicitar Depósito"
  ↓
[Dialog: Solicitud de Depósito]
  - Desde: Combo Cuenta Bancaria
  - Hacia: Cuenta Bursátil (pre-seleccionada)
  - Monto: Pre-calculado (faltante) [editable]
  - Referencia interna: Input texto
  ↓
Usuario hace clic en "Generar PDF Instrucciones"
  ↓
Sistema ejecuta:
  1. Crear MovimientoDB:
     - tipo = DEPOSITO
     - estado = PENDIENTE
     - monto = monto_necesario
  
  2. Crear OrdenMovimientoDB:
     - vincula orden con movimiento
     - tipo_relacion = 'DEPOSITO_PARA_COMPRA'
  
  3. Actualizar OrdenDB:
     - estado = ESPERANDO_FONDOS
  
  4. Actualizar SaldoDB:
     - en_transito += monto
  
  5. Generar PDF:
     - Beneficiario (Casa de Bolsa)
     - Datos bancarios completos
     - Monto exacto
     - Concepto con número de cuenta bursátil
     - QR code (opcional)
  
  6. Abrir PDF generado
  ↓
Usuario realiza transferencia bancaria física
  ↓
Usuario vuelve al sistema → "Confirmar Depósito"
  ↓
[Dialog: Confirmar Depósito]
  - Mostrar movimientos PENDIENTES
  - Subir comprobante (opcional)
  - Input: Referencia bancaria
  - Botón: "Confirmar"
  ↓
Sistema ejecuta:
  1. Actualizar MovimientoDB:
     - estado = COMPLETADO
     - fecha_completado = now()
  
  2. Actualizar SaldoDB:
     - en_transito -= monto
     - disponible += monto
  
  3. Si la orden estaba en ESPERANDO_FONDOS:
     - Verificar si ahora hay fondos suficientes
     - Si SÍ → cambiar a PENDIENTE (lista para ejecutar)
```

### FLUJO 3: Ejecución de Orden (Manual)

```
Usuario va a "Listado de Órdenes"
  ↓
Selecciona orden con estado = PENDIENTE
  ↓
Clic en "Ejecutar Orden"
  ↓
[Dialog: Ejecutar Orden]
  - Mostrar detalles de la orden
  - Input: Precio de ejecución real
  - Input: Cantidad ejecutada (puede ser parcial)
  - Date/Time: Fecha y hora de ejecución
  - Input: Número de operación BVC
  ↓
Sistema ejecuta:
  1. Crear TransaccionDB:
     - cantidad_ejecutada
     - precio_ejecucion
     - monto_bruto = cantidad × precio
     - Calcular comisiones:
       * comision_corretaje
       * comision_bvc
       * comision_cvv
       * iva
     - monto_neto
     - numero_operacion_bvc
  
  2. Actualizar SaldoDB:
     - bloqueado -= monto_orden
     - (El dinero ya fue descontado al crear la orden)
  
  3. Actualizar PortafolioItemDB:
     - Si es COMPRA:
       * cantidad += cantidad_ejecutada
       * Recalcular costo_promedio:
         nuevo_costo = (costo_actual × cant_anterior + precio_exec × cant_nueva) / cant_total
     - Si es VENTA:
       * cantidad -= cantidad_ejecutada
       * Si cantidad llega a 0, eliminar item
  
  4. Actualizar OrdenDB:
     - Si cantidad_ejecutada == cantidad_total:
       estado = EJECUTADA
     - Si cantidad_ejecutada < cantidad_total:
       estado = PARCIALMENTE_EJECUTADA
  
  5. Generar comprobante PDF de ejecución
```

### FLUJO 4: Venta de Acciones con Reporte

```
Usuario va a "Nueva Venta"
  ↓
[PASO 1: Selección]
  - Combo: Inversor
  - Combo: Cuenta Bursátil
  - Sistema carga: PortafolioItemDB (acciones disponibles)
  ↓
[PASO 2: Detalles]
  - Combo: Ticker (solo los que posee)
  - Mostrar: Cantidad disponible
  - Input: Cantidad a vender (validar <= disponible)
  - Combo: Tipo orden (Mercado/Límite)
  - Input: Precio límite (si aplica)
  ↓
[PASO 3: Confirmación]
  - Calculadora en tiempo real
  - Mostrar ganancia/pérdida estimada:
    * Precio compra promedio: Bs. XX
    * Precio venta: Bs. YY
    * G/P por acción: Bs. ±ZZ
    * G/P total: Bs. ±WWWW (±XX%)
  ↓
Usuario confirma
  ↓
Sistema:
  1. Crear OrdenDB tipo=VENTA, estado=PENDIENTE
  2. NO bloquear saldo (es venta)
  ↓
Cuando se ejecuta (ver FLUJO 3):
  ↓
Al finalizar ejecución:
  ↓
Sistema genera automáticamente:
  📄 PDF: "Reporte de Rendimiento de Venta"
  
Contenido del PDF:
  ┌─────────────────────────────────────┐
  │ REPORTE DE VENTA                    │
  │                                     │
  │ Cliente: [Nombre]                   │
  │ Ticker: [TICKER]                    │
  │ Fecha: [DD/MM/YYYY]                 │
  │                                     │
  │ OPERACIÓN:                          │
  │ • Cantidad: XXX acciones            │
  │ • Precio venta: Bs. XX.XX           │
  │ • Monto bruto: Bs. X,XXX.XX        │
  │ • Comisiones: Bs. XXX.XX           │
  │ • Monto neto: Bs. X,XXX.XX         │
  │                                     │
  │ ANÁLISIS DE RENDIMIENTO:            │
  │ • Costo promedio: Bs. XX.XX         │
  │ • Inversión total: Bs. X,XXX.XX    │
  │ • Ganancia/Pérdida: ±Bs. XXX.XX    │
  │ • Rendimiento: ±XX.XX%              │
  │ • Tiempo tenencia: XX días          │
  │ • ROI anualizado: ±XX.XX%           │
  │                                     │
  │ HISTORIAL DE COMPRAS:               │
  │ [Tabla con fechas, precios]         │
  │                                     │
  │ [Gráfico evolución precio]          │
  └─────────────────────────────────────┘
```

### FLUJO 5: Actualización de Precios (Web Scraping)

```
Usuario hace clic en "Actualizar Precios"
  ↓
[Dialog: Actualizar Precios]
  - Progress bar
  - Log de acciones:
    "Actualizando BPV... ✓"
    "Actualizando BOD... ✓"
    "Actualizando CORP... ✗ Error"
  ↓
Sistema ejecuta:
  1. scraper_bvc_service.actualizar_precios_masivo()
  2. Para cada ticker en ActivoDB:
     - Hacer scraping de la BVC
     - Obtener: precio, volumen, variación
     - Actualizar/Crear PrecioActualDB
     - Actualizar ActivoDB.precio_actual
  3. Manejar errores y timeouts
  4. Generar reporte de actualización
```

---

## 🎨 INTERFAZ DE USUARIO

### Vista Principal: Dashboard de Operaciones

```
┌─────────────────────────────────────────────────────────────┐
│  [🏠 Home] [👥 Clientes] [💼 Operaciones*] [📊 Reportes]   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  GESTIÓN DE OPERACIONES                                     │
│                                                              │
│  Inversor: [Juan Pérez ▼] Casa Bolsa: [XYZ ▼] Cuenta: [▼] │
└─────────────────────────────────────────────────────────────┘

┌────────────┬────────────┬────────────┬────────────┐
│ Portafolio │ Pendientes │  G/P Total │   Última   │
│ Bs.125,000 │     3      │  +15.5%    │ Act. Hoy   │
│   ↑ 12.3%  │ En proceso │ Bs. 19,375 │   10:30    │
└────────────┴────────────┴────────────┴────────────┘

┌─────────────────────────────────────────────────────────────┐
│  [🛒 Nueva Compra] [💰 Nueva Venta]                        │
│  [📂 Ver Portafolio] [🔄 Actualizar Precios]               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  OPERACIONES RECIENTES                    [Ver todas →]     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Fecha     │ Tipo   │ Ticker │ Cant │ Estado          │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ 16/01/26  │ COMPRA │ BPV    │ 500  │ ⏳ Pendiente   │  │
│  │ 15/01/26  │ VENTA  │ BOD    │ 300  │ ✅ Ejecutada   │  │
│  │ 14/01/26  │ COMPRA │ CORP   │ 1000 │ 💰 Esp.Fondos │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Componentes con ObjectNames

```python
# Header
header_frame.setObjectName("operacionesHeader")
title_label.setObjectName("operacionesTitle")

# Selectores
label.setObjectName("selectorLabel")
combo.setObjectName("selectorCombo")

# Metric Cards
card.setObjectName("metricCard")  # o metricCardGreen/Blue/Orange
title.setObjectName("metricCardTitle")
value.setObjectName("metricCardValue")
subtitle.setObjectName("metricCardSubtitle")

# Botones principales
btn_compra.setObjectName("primaryButton")
btn_venta.setObjectName("secondaryButton")
btn_portafolio.setObjectName("outlineButton")

# Tabla
table.setObjectName("")  # Usa estilos por defecto de QTableWidget

# Badges de estado
badge_pendiente.setObjectName("badgeWarning")
badge_ejecutada.setObjectName("badgeSuccess")
badge_esperando.setObjectName("badgeInfo")
```

---

## 📦 SERVICIOS (LÓGICA DE NEGOCIO)

### operaciones_service.py

```python
class OperacionesService:
    
    def crear_orden_compra(
        self,
        cliente_id: int,
        cuenta_bursatil_id: int,
        cuenta_bancaria_id: int,
        ticker: str,
        cantidad: int,
        precio_limite: Decimal,
        tipo_orden: TipoOrden
    ) -> dict:
        """
        Crea una orden de compra y valida fondos disponibles
        
        Returns:
            {
                'exito': bool,
                'orden_id': int,
                'requiere_deposito': bool,
                'monto_faltante': Decimal,
                'mensaje': str
            }
        """
        
    def solicitar_deposito(
        self,
        cuenta_bursatil_id: int,
        cuenta_bancaria_id: int,
        monto: Decimal,
        orden_id: int = None
    ) -> MovimientoDB:
        """
        Crea un movimiento de depósito pendiente y actualiza saldo en_transito
        """
        
    def confirmar_deposito(
        self,
        movimiento_id: int,
        referencia_bancaria: str,
        comprobante_path: str = None
    ) -> bool:
        """
        Confirma que el depósito se reflejó y actualiza saldos
        """
        
    def ejecutar_orden(
        self,
        orden_id: int,
        precio_ejecucion: Decimal,
        cantidad_ejecutada: int,
        numero_operacion_bvc: str
    ) -> TransaccionDB:
        """
        Ejecuta una orden y actualiza portafolio
        """
        
    def crear_orden_venta(
        self,
        cliente_id: int,
        cuenta_bursatil_id: int,
        ticker: str,
        cantidad: int,
        precio_limite: Decimal
    ) -> dict:
        """
        Crea orden de venta con validación de posición disponible
        """
        
    def calcular_rendimiento_venta(
        self,
        transaccion_id: int
    ) -> dict:
        """
        Calcula métricas de rendimiento de una venta
        
        Returns:
            {
                'costo_promedio': Decimal,
                'precio_venta': Decimal,
                'ganancia_perdida': Decimal,
                'porcentaje': Decimal,
                'roi_anualizado': Decimal,
                'dias_tenencia': int
            }
        """
```

### calculadora_service.py

```python
class CalculadoraService:
    
    def calcular_comisiones(
        self,
        monto_bruto: Decimal,
        casa_bolsa_id: int
    ) -> dict:
        """
        Calcula todas las comisiones según configuración
        
        Returns:
            {
                'comision_corretaje': Decimal,
                'comision_bvc': Decimal,
                'comision_cvv': Decimal,
                'iva': Decimal,
                'total_comisiones': Decimal,
                'monto_neto': Decimal
            }
        """
        
    def calcular_precio_promedio(
        self,
        costo_anterior: Decimal,
        cantidad_anterior: int,
        precio_nuevo: Decimal,
        cantidad_nueva: int
    ) -> Decimal:
        """
        Calcula el nuevo precio promedio ponderado
        """
        
    def calcular_roi_anualizado(
        self,
        inversion_inicial: Decimal,
        valor_final: Decimal,
        dias_tenencia: int
    ) -> Decimal:
        """
        Calcula ROI anualizado
        """
```

### scraper_bvc_service.py

```python
class ScraperBVCService:
    
    def obtener_precio_actual(self, ticker: str) -> dict:
        """
        Scraping del precio actual de un ticker
        
        Returns:
            {
                'precio': Decimal,
                'volumen': int,
                'variacion': Decimal,
                'precio_apertura': Decimal,
                'precio_maximo': Decimal,
                'precio_minimo': Decimal,
                'fecha_hora': datetime
            }
        """
        
    def actualizar_precios_masivo(self) -> dict:
        """
        Actualiza todos los tickers activos
        
        Returns:
            {
                'actualizados': int,
                'errores': int,
                'detalles': list
            }
        """
```

---

## 📄 GENERACIÓN DE PDFs

### deposito_generator.py

```python
class DepositoGenerator:
    
    def generar(
        self,
        movimiento: MovimientoDB,
        cuenta_bancaria: CuentaBancariaDB,
        cuenta_bursatil: CuentaBursatilDB
    ) -> str:
        """
        Genera PDF con instrucciones de depósito
        
        Returns:
            ruta_pdf: str
        """
        # Template: instruccion_deposito.html
        # Incluye:
        # - Datos del cliente
        # - Banco origen y destino
        # - Monto exacto
        # - Concepto
        # - Instrucciones
```

### venta_rendimiento_generator.py

```python
class VentaRendimientoGenerator:
    
    def generar(
        self,
        transaccion: TransaccionDB,
        metricas: dict
    ) -> str:
        """
        Genera PDF con análisis de rendimiento de venta
        
        Returns:
            ruta_pdf: str
        """
        # Template: reporte_venta.html
        # Incluye:
        # - Detalles de la operación
        # - Análisis de rendimiento
        # - Historial de compras
        # - Gráfico de evolución (matplotlib)
```

---

## 🧪 TESTING

### Prioridades de Testing

1. **Unitarios (services):**
   - calculadora_service.py
   - operaciones_service.py
   
2. **Integración (database):**
   - Flujo completo de compra
   - Flujo completo de venta
   - Actualización de saldos
   - Actualización de portafolio

3. **UI (manual):**
   - Navegación entre vistas
   - Validaciones de formularios
   - Generación de PDFs

---

## 📅 FASES DE IMPLEMENTACIÓN

### FASE 1: Base de Datos (2-3 días)
- [ ] Modificar models_sql.py
- [ ] Crear migraciones
- [ ] Agregar Enums a constants.py
- [ ] Poblar tickers_bvc.csv
- [ ] Testing de modelos

### FASE 2: Servicios Core (3-4 días)
- [ ] calculadora_service.py
- [ ] operaciones_service.py
- [ ] movimientos_service.py
- [ ] operaciones_controller.py
- [ ] Testing unitarios

### FASE 3: Scraping (2 días)
- [ ] scraper_bvc_service.py
- [ ] Actualización de precios
- [ ] Manejo de errores

### FASE 4: UI - Dashboard (3 días)
- [ ] operaciones_module.py
- [ ] operaciones_dashboard.py
- [ ] operaciones_list_view.py
- [ ] portafolio_view.py
- [ ] Widgets reutilizables

### FASE 5: UI - Dialogs de Operaciones (4 días)
- [ ] nueva_compra_dialog.py (wizard 3 pasos)
- [ ] nueva_venta_dialog.py
- [ ] solicitud_deposito_dialog.py
- [ ] confirmar_deposito_dialog.py
- [ ] detalle_operacion_dialog.py
- [ ] actualizar_precios_dialog.py

### FASE 6: Generación de PDFs (3 días)
- [ ] deposito_generator.py
- [ ] venta_rendimiento_generator.py
- [ ] comprobante_operacion.py
- [ ] Templates HTML
- [ ] Testing de generación

### FASE 7: Widgets Especializados (2 días)
- [ ] ticker_search_widget.py (autocomplete)
- [ ] calculadora_comisiones.py (en tiempo real)
- [ ] saldo_widget.py (display mejorado)
- [ ] operacion_card_widget.py
- [ ] estado_orden_badge.py

### FASE 8: Integración y Pulido (2-3 días)
- [ ] Integrar al main_window.py
- [ ] Actualizar sidebar.py
- [ ] Agregar estilos al styles.qss
- [ ] Testing de integración
- [ ] Corrección de bugs

### FASE 9: Optimización y Documentación (2 días)
- [ ] Optimizar queries de base de datos
- [ ] Agregar índices faltantes
- [ ] Documentación de código
- [ ] Manual de usuario básico
- [ ] Video tutorial (opcional)

**TIEMPO TOTAL ESTIMADO: 21-25 días de desarrollo**

---

## 🎯 FUNCIONALIDADES CLAVE

### ✅ Funcionalidades Básicas (MVP)

1. **Gestión de Órdenes:**
   - Crear orden de compra
   - Crear orden de venta
   - Cancelar orden pendiente
   - Ver listado de órdenes
   - Ver detalle de orden

2. **Gestión de Fondos:**
   - Solicitar depósito con PDF
   - Confirmar depósito recibido
   - Ver saldo disponible/bloqueado/en tránsito
   - Historial de movimientos

3. **Ejecución de Operaciones:**
   - Ejecutar orden manualmente
   - Registro de transacción completa
   - Actualización automática de portafolio
   - Cálculo de comisiones

4. **Portafolio:**
   - Ver posiciones actuales
   - Calcular valor actual
   - Ver ganancia/pérdida no realizada
   - Filtrar por cuenta/ticker

5. **Reportes:**
   - PDF instrucción de depósito
   - PDF reporte de venta con análisis
   - Comprobante de orden

### 🚀 Funcionalidades Avanzadas (Fase 2)

6. **Scraping Automatizado:**
   - Actualización periódica de precios
   - Alertas de variación de precio
   - Histórico de precios

7. **Análisis Avanzado:**
   - Gráficos de evolución de portafolio
   - ROI por activo
   - Comparación de rendimiento
   - Estadísticas de trading

8. **Automatización:**
   - Órdenes programadas
   - Stop loss / Take profit
   - Alertas de precios objetivo

9. **Reportes Extendidos:**
   - Estado de cuenta mensual
   - Declaración de impuestos
   - Análisis de comisiones pagadas

---

## 🛡️ VALIDACIONES Y REGLAS DE NEGOCIO

### Validaciones de Compra

```python
# Al crear orden de compra:
✓ Cliente existe y está activo
✓ Cuenta bursátil pertenece al cliente
✓ Ticker existe y está activo en BVC
✓ Cantidad > 0
✓ Precio límite > 0 (si aplica)
✓ Fecha vencimiento > fecha actual

# Al ejecutar orden de compra:
✓ Saldo disponible >= monto_total + comisiones
✓ Orden está en estado PENDIENTE
✓ Cantidad ejecutada <= cantidad total de la orden
✓ Precio ejecución > 0
```

### Validaciones de Venta

```python
# Al crear orden de venta:
✓ Cliente posee el activo en su portafolio
✓ Cantidad a vender <= cantidad disponible
✓ No vender más de lo que tiene
✓ Precio límite > 0 (si aplica)

# Al ejecutar orden de venta:
✓ Orden está en estado PENDIENTE
✓ Portafolio tiene cantidad suficiente
✓ Cantidad ejecutada <= cantidad de la orden
```

### Validaciones de Movimientos

```python
# Al solicitar depósito:
✓ Cuenta bancaria pertenece al cliente
✓ Cuenta bursátil pertenece al cliente
✓ Monto > 0
✓ Moneda válida (VES, USD)

# Al confirmar depósito:
✓ Movimiento existe y está PENDIENTE
✓ Referencia bancaria no está vacía
✓ No duplicar confirmación
```

### Reglas de Saldos

```python
# Invariante del sistema:
SaldoDB.disponible + SaldoDB.bloqueado + SaldoDB.en_transito >= 0

# Al crear orden COMPRA:
disponible -= monto_total
bloqueado += monto_total

# Al ejecutar orden COMPRA:
bloqueado -= monto_total
# El dinero ya salió, no se devuelve al disponible

# Al crear orden VENTA:
# No se bloquea saldo (son acciones, no dinero)

# Al ejecutar orden VENTA:
disponible += monto_neto
```

---

## 🔐 SEGURIDAD Y AUDITORÍA

### Campos de Auditoría (Ya existentes en AuditMixin)

```python
fecha_registro: datetime      # Cuándo se creó
fecha_actualizacion: datetime # Última modificación
estatus: bool                 # Soft delete
```

### Logging de Operaciones Críticas

```python
# Registrar en logs:
- Creación de órdenes
- Ejecución de transacciones
- Confirmación de depósitos
- Modificación de saldos
- Actualización de portafolio
- Generación de PDFs
- Errores de scraping

# Formato de log:
[2026-01-16 10:30:45] [INFO] [OperacionesService] 
Orden de compra creada: ID=123, Cliente=Juan Pérez, 
Ticker=BPV, Cantidad=500, Estado=PENDIENTE
```

### Restricciones de Integridad

```sql
-- Foreign Keys para garantizar integridad referencial
-- Constraints para validar rangos (cantidad > 0, precio > 0)
-- Unique Constraints para evitar duplicados
-- Índices para mejorar performance de búsquedas
```

---

## 📊 MÉTRICAS Y KPIs DEL DASHBOARD

### Métricas Principales

```python
1. Valor Total del Portafolio
   = Σ (cantidad × precio_actual) para todas las posiciones
   
2. Operaciones Pendientes
   = COUNT(ordenes WHERE estado IN ['PENDIENTE', 'ESPERANDO_FONDOS'])
   
3. Ganancia/Pérdida Total No Realizada
   = Σ ((precio_actual - costo_promedio) × cantidad)
   
4. Ganancia/Pérdida Total Realizada
   = Σ (monto_neto_venta - (costo_promedio × cantidad_vendida))
   
5. Última Actualización de Precios
   = MAX(fecha_hora) FROM precios_actuales
```

### Métricas por Activo

```python
1. Rendimiento del Activo
   = ((precio_actual - costo_promedio) / costo_promedio) × 100
   
2. Valor de Mercado de la Posición
   = cantidad × precio_actual
   
3. Costo Total de Adquisición
   = cantidad × costo_promedio
   
4. G/P de la Posición
   = valor_mercado - costo_adquisicion
```

---

## 💾 MANEJO DE DATOS

### Archivos CSV

#### tickers_bvc.csv
```csv
ticker,nombre,rif,sector,mercado,estado
BPV,Banco Provincial,J-00000000-0,Financiero,Acciones,ACTIVO
BOD,Banco Occidental de Descuento,J-00000000-1,Financiero,Acciones,ACTIVO
CORP,Corpoelec,J-00000000-2,Servicios,Acciones,ACTIVO
BNC,Banco Nacional de Crédito,J-00000000-3,Financiero,Acciones,ACTIVO
```

### Estructura de Directorios para PDFs

```
data/
├── exports/
│   └── pdf/
│       ├── operaciones/
│       │   ├── ordenes/
│       │   │   └── orden_123_20260116.pdf
│       │   ├── depositos/
│       │   │   └── deposito_45_20260116.pdf
│       │   └── reportes_venta/
│       │       └── venta_789_20260116.pdf
│       └── comprobantes/
│           └── comprobante_orden_123.pdf
```

---

## 🎨 DISEÑO DE COMPONENTES CLAVE

### Widget: Calculadora de Comisiones en Tiempo Real

```python
class CalculadoraComisionesWidget(QWidget):
    """
    Widget que muestra cálculo en tiempo real de comisiones
    Se actualiza automáticamente cuando cambian cantidad o precio
    """
    
    # Señales
    total_changed = pyqtSignal(Decimal)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Subtotal
        self.label_subtotal = self.create_row("Subtotal:", "Bs. 0.00")
        
        # Comisiones
        self.label_corretaje = self.create_row("Comisión Corretaje (0.5%):", "Bs. 0.00")
        self.label_bvc = self.create_row("Comisión BVC (0.05%):", "Bs. 0.00")
        self.label_cvv = self.create_row("Comisión CVV (0.05%):", "Bs. 0.00")
        self.label_iva = self.create_row("IVA (16%):", "Bs. 0.00")
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("separator")
        
        # Total
        self.label_total = self.create_row("TOTAL A PAGAR:", "Bs. 0.00", bold=True)
        
        layout.addLayout(self.label_subtotal)
        layout.addLayout(self.label_corretaje)
        layout.addLayout(self.label_bvc)
        layout.addLayout(self.label_cvv)
        layout.addLayout(self.label_iva)
        layout.addWidget(line)
        layout.addLayout(self.label_total)
        
    def actualizar(self, cantidad: int, precio: Decimal):
        """Recalcula todo automáticamente"""
        comisiones = CalculadoraService().calcular_comisiones(
            monto_bruto=cantidad * precio,
            casa_bolsa_id=self.casa_bolsa_id
        )
        
        self.label_subtotal[1].setText(f"Bs. {cantidad * precio:,.2f}")
        self.label_corretaje[1].setText(f"Bs. {comisiones['comision_corretaje']:,.2f}")
        # ... actualizar todos los labels
        
        self.total_changed.emit(comisiones['monto_total'])
```

### Widget: Búsqueda de Ticker con Autocomplete

```python
class TickerSearchWidget(QWidget):
    """
    Widget de búsqueda con autocomplete de tickers
    Muestra sugerencias mientras se escribe
    """
    
    # Señales
    ticker_selected = pyqtSignal(str, dict)  # ticker, info_completa
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_tickers()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Input de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setObjectName("form_input")
        self.input_busqueda.setPlaceholderText("Buscar ticker o nombre...")
        self.input_busqueda.textChanged.connect(self.on_text_changed)
        
        # Lista de sugerencias
        self.list_sugerencias = QListWidget()
        self.list_sugerencias.setMaximumHeight(200)
        self.list_sugerencias.hide()
        self.list_sugerencias.itemClicked.connect(self.on_sugerencia_clicked)
        
        # Label de ticker seleccionado
        self.label_seleccionado = QLabel()
        self.label_seleccionado.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        layout.addWidget(QLabel("Ticker:"))
        layout.addWidget(self.input_busqueda)
        layout.addWidget(self.list_sugerencias)
        layout.addWidget(self.label_seleccionado)
        
    def on_text_changed(self, text):
        """Filtrar tickers según texto"""
        if len(text) < 2:
            self.list_sugerencias.hide()
            return
            
        # Buscar coincidencias
        matches = [
            t for t in self.tickers 
            if text.upper() in t['ticker'] or text.upper() in t['nombre'].upper()
        ]
        
        self.list_sugerencias.clear()
        
        if matches:
            for ticker_info in matches[:5]:  # Máximo 5 sugerencias
                item_text = f"{ticker_info['ticker']} - {ticker_info['nombre']}"
                self.list_sugerencias.addItem(item_text)
            self.list_sugerencias.show()
        else:
            self.list_sugerencias.hide()
```

### Widget: Badge de Estado de Orden

```python
class EstadoOrdenBadge(QLabel):
    """
    Badge visual para mostrar estado de una orden
    Con colores según el estado
    """
    
    ESTILOS = {
        EstadoOrden.BORRADOR: ("badge", "#666666"),
        EstadoOrden.ESPERANDO_FONDOS: ("badgeWarning", "#FF9800"),
        EstadoOrden.PENDIENTE: ("badgeInfo", "#2196F3"),
        EstadoOrden.PARCIALMENTE_EJECUTADA: ("badgeWarning", "#FF9800"),
        EstadoOrden.EJECUTADA: ("badgeSuccess", "#4CAF50"),
        EstadoOrden.CANCELADA: ("badgeDanger", "#666666"),
        EstadoOrden.RECHAZADA: ("badgeDanger", "#F44336"),
    }
    
    def __init__(self, estado: EstadoOrden):
        super().__init__()
        self.set_estado(estado)
        
    def set_estado(self, estado: EstadoOrden):
        """Actualiza el estado y el estilo"""
        self.setText(estado.value)
        object_name, color = self.ESTILOS[estado]
        self.setObjectName(object_name)
        self.setStyleSheet(f"""
            #{object_name} {{
                background-color: {color};
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
```

---

## 🔄 ACTUALIZACIONES EN TIEMPO REAL

### Sistema de Señales Qt

```python
# En OperacionesController
class OperacionesController(QObject):
    
    # Señales para actualizar UI
    orden_creada = pyqtSignal(int)  # orden_id
    orden_ejecutada = pyqtSignal(int)  # orden_id
    deposito_confirmado = pyqtSignal(int)  # movimiento_id
    saldo_actualizado = pyqtSignal(int, Decimal)  # cuenta_id, nuevo_saldo
    portafolio_actualizado = pyqtSignal(int)  # cuenta_id
    precios_actualizados = pyqtSignal(dict)  # {ticker: precio}
    
    def __init__(self):
        super().__init__()
        self.service = OperacionesService()
        
    def crear_compra(self, datos: dict):
        """Crear orden de compra y emitir señal"""
        resultado = self.service.crear_orden_compra(**datos)
        
        if resultado['exito']:
            self.orden_creada.emit(resultado['orden_id'])
            self.saldo_actualizado.emit(
                datos['cuenta_bursatil_id'],
                resultado['nuevo_saldo']
            )
            
        return resultado

# En las vistas
class OperacionesDashboard(QWidget):
    
    def __init__(self, controller: OperacionesController):
        super().__init__()
        self.controller = controller
        
        # Conectar señales
        self.controller.orden_creada.connect(self.on_orden_creada)
        self.controller.saldo_actualizado.connect(self.actualizar_saldo_display)
        self.controller.precios_actualizados.connect(self.actualizar_precios_tabla)
        
    def on_orden_creada(self, orden_id: int):
        """Refrescar tabla cuando se crea una orden"""
        self.cargar_ordenes_recientes()
        self.mostrar_notificacion(f"Orden #{orden_id} creada exitosamente")
```

---

## 📱 NOTIFICACIONES Y FEEDBACK

### Sistema de Notificaciones

```python
class NotificationManager:
    """
    Gestor centralizado de notificaciones
    """
    
    @staticmethod
    def success(parent, titulo: str, mensaje: str):
        """Notificación de éxito (verde)"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E1E;
            }
            QLabel {
                color: #4CAF50;
            }
        """)
        msg.exec()
        
    @staticmethod
    def warning(parent, titulo: str, mensaje: str):
        """Notificación de advertencia (naranja)"""
        # Similar pero con color #FF9800
        
    @staticmethod
    def error(parent, titulo: str, mensaje: str):
        """Notificación de error (rojo)"""
        # Similar pero con color #F44336
        
    @staticmethod
    def confirm(parent, titulo: str, mensaje: str) -> bool:
        """Diálogo de confirmación"""
        reply = QMessageBox.question(
            parent,
            titulo,
            mensaje,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

# Uso en código:
if NotificationManager.confirm(
    self,
    "Confirmar Compra",
    f"¿Desea comprar {cantidad} acciones de {ticker}?"
):
    self.controller.crear_compra(datos)
```

---

## 🐛 MANEJO DE ERRORES

### Excepciones Personalizadas

```python
# utils/exceptions.py

class OperacionesError(Exception):
    """Excepción base para el módulo de operaciones"""
    pass

class SaldoInsuficienteError(OperacionesError):
    """Se intenta comprar sin fondos suficientes"""
    def __init__(self, disponible, necesario):
        self.disponible = disponible
        self.necesario = necesario
        super().__init__(
            f"Saldo insuficiente. Disponible: Bs. {disponible:,.2f}, "
            f"Necesario: Bs. {necesario:,.2f}"
        )

class PosicionInsuficienteError(OperacionesError):
    """Se intenta vender más acciones de las que se poseen"""
    def __init__(self, ticker, disponible, solicitado):
        self.ticker = ticker
        self.disponible = disponible
        self.solicitado = solicitado
        super().__init__(
            f"Posición insuficiente en {ticker}. "
            f"Disponible: {disponible}, Solicitado: {solicitado}"
        )

class OrdenNoEncontradaError(OperacionesError):
    """La orden especificada no existe"""
    pass

class ScrapingError(OperacionesError):
    """Error al hacer scraping de la BVC"""
    pass

# Uso en servicios:
def crear_orden_compra(self, ...):
    # Validar saldo
    saldo = self.get_saldo(cuenta_id)
    monto_total = self.calcular_total(cantidad, precio)
    
    if saldo.disponible < monto_total:
        raise SaldoInsuficienteError(saldo.disponible, monto_total)
    
    # Crear orden...

# Uso en UI:
try:
    self.controller.crear_compra(datos)
    NotificationManager.success(self, "Éxito", "Orden creada")
except SaldoInsuficienteError as e:
    NotificationManager.warning(
        self,
        "Saldo Insuficiente",
        f"{str(e)}\n\n¿Desea solicitar un depósito?"
    )
    self.abrir_solicitud_deposito(e.necesario - e.disponible)
except OperacionesError as e:
    NotificationManager.error(self, "Error", str(e))
```

---

## 📚 DOCUMENTACIÓN Y COMENTARIOS

### Estándares de Documentación

```python
"""
Módulo: operaciones_service.py
Descripción: Servicio principal para gestión de operaciones bursátiles
Autor: [Tu nombre]
Fecha: 2026-01-16
"""

class OperacionesService:
    """
    Servicio que encapsula toda la lógica de negocio relacionada
    con operaciones de compra y venta en la Bolsa de Valores de Caracas.
    
    Este servicio maneja:
    - Creación y ejecución de órdenes
    - Validación de fondos y posiciones
    - Actualización de saldos y portafolios
    - Cálculo de comisiones y rendimientos
    
    Attributes:
        session: Sesión de SQLAlchemy para acceso a BD
        calculadora: Instancia de CalculadoraService
        logger: Logger para registro de operaciones
    """
    
    def crear_orden_compra(
        self,
        cliente_id: int,
        cuenta_bursatil_id: int,
        ticker: str,
        cantidad: int,
        precio_limite: Decimal,
        tipo_orden: TipoOrden
    ) -> dict:
        """
        Crea una orden de compra de acciones.
        
        Este método:
        1. Valida que el cliente y cuenta existan
        2. Verifica saldo disponible
        3. Calcula comisiones estimadas
        4. Crea la orden en estado apropiado
        5. Actualiza saldos según disponibilidad
        
        Args:
            cliente_id: ID del cliente que realiza la compra
            cuenta_bursatil_id: ID de la cuenta bursátil a usar
            ticker: Símbolo del activo a comprar (ej: 'BPV')
            cantidad: Número de acciones a comprar (>0)
            precio_limite: Precio máximo por acción (si es orden límite)
            tipo_orden: MERCADO o LIMITE
            
        Returns:
            dict: {
                'exito': bool,
                'orden_id': int,
                'requiere_deposito': bool,
                'monto_faltante': Decimal,
                'mensaje': str
            }
            
        Raises:
            ValueError: Si cantidad <= 0 o precio <= 0
            ClienteNoEncontradoError: Si el cliente no existe
            CuentaNoEncontradaError: Si la cuenta no existe
            
        Example:
            >>> service = OperacionesService()
            >>> resultado = service.crear_orden_compra(
            ...     cliente_id=1,
            ...     cuenta_bursatil_id=5,
            ...     ticker='BPV',
            ...     cantidad=500,
            ...     precio_limite=Decimal('15.50'),
            ...     tipo_orden=TipoOrden.LIMITE
            ... )
            >>> print(resultado['exito'])
            True
        """
        # Implementación...
```

---

## 🎓 RECURSOS Y REFERENCIAS

### Librerías Utilizadas

```python
# requirements.txt (agregar)
PyQt6>=6.5.0
SQLAlchemy>=2.0.0
beautifulsoup4>=4.12.0  # Para web scraping
requests>=2.31.0         # Para HTTP requests
reportlab>=4.0.0         # Para generar PDFs
matplotlib>=3.7.0        # Para gráficos en PDFs
pandas>=2.0.0            # Para análisis de datos (opcional)
```

### Documentación Externa

- **PyQt6:** https://doc.qt.io/qtforpython-6/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **ReportLab:** https://www.reportlab.com/docs/reportlab-userguide.pdf
- **Beautiful Soup:** https://www.crummy.com/software/BeautifulSoup/bs4/doc/

### Regulaciones BVC (Referencias)

- Comisiones vigentes de la BVC
- Horarios de trading
- Reglas de liquidación (T+2)
- Requisitos KYC/AML

---

## ✅ CHECKLIST FINAL

### Antes de Entregar a Producción

- [ ] Todas las migraciones de BD ejecutadas
- [ ] Tests unitarios pasando (>80% coverage)
- [ ] Tests de integración pasando
- [ ] Manejo de errores completo
- [ ] Logging configurado correctamente
- [ ] PDFs generándose correctamente
- [ ] Scraping funcionando (con rate limiting)
- [ ] UI responsive y sin bugs visuales
- [ ] Validaciones de formularios funcionando
- [ ] Cálculos de comisiones verificados
- [ ] Actualización de saldos correcta
- [ ] Actualización de portafolio correcta
- [ ] Documentación de código completa
- [ ] Manual de usuario básico
- [ ] Backup de base de datos configurado
- [ ] Testing con datos reales (sandbox)

---

## 🎉 RESUMEN EJECUTIVO

Este plan detalla la implementación completa de un **módulo de operaciones bursátiles** para el sistema BVC Gestor. El módulo permite:

✅ **Comprar y vender acciones** con validación completa de fondos y posiciones
✅ **Gestionar depósitos y retiros** entre bancos y casas de bolsa
✅ **Generar PDFs automáticos** para instrucciones y reportes
✅ **Calcular rendimientos** con análisis detallado de G/P
✅ **Actualizar precios** mediante web scraping de la BVC
✅ **Mantener portafolio** actualizado en tiempo real
✅ **Auditar todas las operaciones** con logs completos

**Arquitectura:** Modular, escalable, siguiendo patrón MVC
**Tecnologías:** PyQt6, SQLAlchemy, ReportLab, BeautifulSoup
**Tiempo estimado:** 21-25 días de desarrollo
**Complejidad:** Media-Alta

El módulo se integra perfectamente con la estructura existente del proyecto y mantiene el mismo estilo visual dark mode con acento naranja (#FF6B00).