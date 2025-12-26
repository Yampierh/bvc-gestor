
# BVC-GESTOR - Gestor de Bolsa de Valores de Caracas



Aplicación de escritorio profesional para gestión individual de múltiples clientes en la Bolsa de Valores de Venezuela.



## Características principales



- ✅ Gestión completa de clientes con validación venezolana

- ✅ Operaciones bursátiles (órdenes de compra/venta)

- ✅ Portafolios y análisis de inversión

- ✅ Reportes profesionales en PDF/Excel

- ✅ Sistema de backup automático y encriptación

- ✅ Interfaz moderna y responsiva



## Requisitos



- Python 3.8 o superior

- 4GB RAM mínimo

- 500MB espacio en disco



## Instalación



1. Clonar repositorio

2. Crear entorno virtual: `python -m venv venv`

3. Activar entorno: `source venv/bin/activate` (Linux/Mac) o `venv\Scripts\activate` (Windows)

4. Instalar dependencias: `pip install -r requirements.txt`

5. Copiar `.env.example` a `.env` y configurar

6. Ejecutar: `python run.py`



## Estructura del proyecto



BVC-GESTOR/

├── src/ # Código fuente

├── data/ # Datos locales

├── docs/ # Documentación

├── tests/ # Pruebas

└── scripts/ # Scripts utilitarios



## Desarrollo



Para contribuir al desarrollo:



1. Instalar dependencias de desarrollo: `pip install -r requirements.txt -e ".[dev]"`

2. Configurar pre-commit: `pre-commit install`

3. Ejecutar pruebas: `pytest`



## Licencia



MIT License - Ver LICENSE para más detalles.

