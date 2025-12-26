# Makefile
.PHONY: help install run test clean db-init db-reset backup restore lint format

help:
	@echo "Comandos disponibles para BVC-GESTOR:"
	@echo ""
	@echo "  install     Instalar dependencias"
	@echo "  run         Ejecutar aplicación"
	@echo "  test        Ejecutar pruebas"
	@echo "  clean       Limpiar archivos temporales"
	@echo "  db-init     Inicializar base de datos"
	@echo "  db-reset    Reinicializar base de datos (¡cuidado!)"
	@echo "  backup      Crear backup manual"
	@echo "  restore     Restaurar desde backup"
	@echo "  lint        Verificar estilo de código"
	@echo "  format      Formatear código con black"
	@echo ""

install:
	pip install -r requirements.txt

run:
	python run.py

test:
	pytest tests/ -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .coverage

db-init:
	@echo "Inicializando base de datos..."
	python -c "from src.bvc_gestor.database.engine import get_database; db = get_database(); db.create_tables(); print('✓ Base de datos inicializada')"

db-reset:
	@echo "⚠  ¡ADVERTENCIA! Esto eliminará todos los datos."
	@read -p "¿Está seguro? (s/n): " confirm && [ $$confirm = "s" ] || exit 1
	python -c "from src.bvc_gestor.database.engine import get_database; db = get_database(); db.drop_tables(); db.create_tables(); print('✓ Base de datos reinicializada')"

backup:
	python scripts/backup.py

restore:
	@echo "Restaurando desde backup..."
	python scripts/restore.py

lint:
	flake8 src/ --max-line-length=88 --exclude=__pycache__

format:
	black src/ tests/ --line-length=88

dev:
	@echo "Iniciando modo desarrollo..."
	export PYTHONPATH=$$PYTHONPATH:$$(pwd)/src && python run.py

setup:
	@echo "Configurando entorno de desarrollo..."
	python -m venv venv
	@echo "✓ Entorno virtual creado"
	@echo ""
	@echo "Para activar el entorno virtual:"
	@echo "  • Linux/Mac: source venv/bin/activate"
	@echo "  • Windows: venv\\Scripts\\activate"
	@echo ""
	@echo "Luego ejecute: make install"

update:
	pip install --upgrade -r requirements.txt

check:
	@echo "Verificando sistema..."
	make lint
	pytest tests/ -q
	@echo "✓ Verificación completada"