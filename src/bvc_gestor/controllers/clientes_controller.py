from sqlalchemy.orm import Session
from ..database.models_sql import ClienteDB as Cliente
from ..ui.views.clientes_view import ClientesView
from sqlalchemy.exc import IntegrityError
from PyQt6.QtWidgets import QTableWidgetItem

class ClientesController:
    def __init__(self, view: ClientesView):
        self.view = view
        # Conectamos los eventos de la UI a nuestras funciones
        self.view.btn_save.clicked.connect(self.guardar_cliente)
        self.view.search_bar.textChanged.connect(self.filtrar_clientes)
        self.view.table.itemSelectionChanged.connect(self.cargar_detalle_cliente)
        
        # Cargar datos iniciales
        self.actualizar_tabla()

    def actualizar_tabla(self, filtro=""):
        db = SessionLocal()
        try:
            # Idea de busqueda.py: Filtrar por RIF o Nombre
            query = db.query(Cliente)
            if filtro:
                query = query.filter(
                    (Cliente.rif.like(f"%{filtro}%")) | 
                    (Cliente.nombre_completo.like(f"%{filtro}%"))
                )
            
            clientes = query.all()
            
            self.view.table.setRowCount(0)
            for cliente in clientes:
                row = self.view.table.rowCount()
                self.view.table.insertRow(row)
                self.view.table.setItem(row, 0, QTableWidgetItem(cliente.rif))
                self.view.table.setItem(row, 1, QTableWidgetItem(f"{cliente.nombre_principal} {cliente.nombre_secundario or ''}"))
                self.view.table.setItem(row, 2, QTableWidgetItem(cliente.tipo_persona))
                self.view.table.setItem(row, 3, QTableWidgetItem("ACTIVO"))
        finally:
            db.close()

    def filtrar_clientes(self):
        texto = self.view.search_bar.text()
        self.actualizar_tabla(texto)

    def cargar_detalle_cliente(self):
        # Cuando tocas una fila, cargamos los datos de apertura.py en el panel derecho
        selected_items = self.view.table.selectedItems()
        if not selected_items:
            return
            
        rif = selected_items[0].text()
        db = SessionLocal()
        cliente = db.query(Cliente).filter(Cliente.rif == rif).first()
        
        if cliente:
            self.view.edit_rif.setText(cliente.rif)
            self.view.edit_nombre.setText(cliente.nombre_completo)
            self.view.edit_tipo.setText(cliente.tipo_persona)
            self.view.edit_direccion.setText(cliente.direccion)
            self.view.edit_email.setText(cliente.email)
        db.close()
        
    def guardar_cliente(self):
        """Captura los datos de la ficha y los persiste en la DB."""
        rif = self.view.edit_rif.text().strip().upper()
        nombre = self.view.edit_nombre.text().strip()
        tipo = self.view.edit_tipo.text().strip().upper()
        
        # Validación de Negocio (Idea de robustez profesional)
        if not rif or not nombre:
            print("Error: RIF y Nombre son obligatorios")
            return

        db = SessionLocal()
        try:
            # Buscamos si el cliente ya existe para actualizarlo o crearlo
            cliente = db.query(Cliente).filter(Cliente.rif == rif).first()
            
            if not cliente:
                cliente = Cliente(rif=rif)
                db.add(cliente)
            
            # Asignamos los valores (Inyectando tus campos de apertura.py)
            cliente.nombre_completo = nombre
            cliente.tipo_persona = tipo
            cliente.direccion = self.view.edit_direccion.text().strip()
            cliente.email = self.view.edit_email.text().strip()
            
            db.commit()
            print(f"Éxito: Cliente {rif} guardado correctamente.")
            self.actualizar_tabla() # Refresca la lista automáticamente
            
        except IntegrityError:
            db.rollback()
            print("Error: El RIF ya existe en el sistema.")
        finally:
            db.close()