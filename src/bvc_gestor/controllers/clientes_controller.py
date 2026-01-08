from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from ..database.engine import get_database
from ..database.models_sql import ClienteDB, BancoDB, CuentaDB

class ClientesController:
    def __init__(self, main_view):
        self.view_stack = main_view
        self.lista = main_view.view_lista
        self.detalle = main_view.view_detalle
        self.db_engine = get_database()

        # Conexiones
        self.lista.btn_nuevo.clicked.connect(self.preparar_nuevo_cliente)
        self.lista.cliente_seleccionado.connect(self.cargar_y_mostrar_detalle)
        self.lista.search_bar.textChanged.connect(self.actualizar_tabla)
        self.detalle.btn_save.clicked.connect(self.guardar_cliente)
        self.detalle.back_clicked.connect(lambda: self.view_stack.setCurrentIndex(0))

        # Inicialización
        self.actualizar_tabla()
        self.precargar_catalogos()

    def preparar_nuevo_cliente(self):
        """Limpia el formulario y cambia a la vista de detalle"""
        # 1. Limpiar campos de texto
        self.detalle.lbl_nombre.setText("Nuevo Cliente")
        self.detalle.edit_rif.clear()
        self.detalle.edit_nombre.clear()
        self.detalle.edit_email.clear()
        self.detalle.edit_tlf.clear()
        self.detalle.edit_dir.clear()
        self.detalle.edit_ciudad.clear()
        
        # 2. Resetear combos (seleccionar el primer banco por defecto)
        if self.detalle.combo_banco.count() > 0:
            self.detalle.combo_banco.setCurrentIndex(0)
            
        # 3. Cambiar la vista al Detalle (Index 1)
        self.view_stack.setCurrentIndex(1)
        
        # Opcional: Poner el foco en el primer campo
        self.detalle.edit_rif.setFocus()

    def precargar_catalogos(self):
        """Carga bancos en los combos del detalle"""
        session = self.db_engine.get_session()
        try:
            bancos = session.query(BancoDB).all()
            self.detalle.combo_banco.clear()
            for banco in bancos:
                self.detalle.combo_banco.addItem(banco.nombre, banco.id)
        finally:
            session.close()

    def actualizar_tabla(self):
        filtro = self.lista.search_bar.text()
        session = self.db_engine.get_session()
        try:
            query = session.query(ClienteDB).filter(ClienteDB.activo == True)
            if filtro:
                query = query.filter(
                    (ClienteDB.rif.ilike(f"%{filtro}%")) | 
                    (ClienteDB.nombre_completo.ilike(f"%{filtro}%"))
                )
            
            clientes = query.all()
            self.lista.table.setRowCount(0)
            for c in clientes:
                row = self.lista.table.rowCount()
                self.lista.table.insertRow(row)
                
                # Guardamos el ID en el UserRole para recuperarlo luego
                item_rif = QTableWidgetItem(str(c.rif))
                item_rif.setData(Qt.ItemDataRole.UserRole, c.id)
                
                self.lista.table.setItem(row, 0, item_rif)
                self.lista.table.setItem(row, 1, QTableWidgetItem(c.nombre_completo))
                self.lista.table.setItem(row, 2, QTableWidgetItem(c.tipo_persona.value))
                self.lista.table.setItem(row, 3, QTableWidgetItem(c.email))
        finally:
            session.close()

    def cargar_y_mostrar_detalle(self, cliente_id):
        """Busca el cliente y llena todas las secciones del formulario"""
        session = self.db_engine.get_session()
        try:
            # Eager loading para traer las cuentas de una vez
            cliente = session.query(ClienteDB).filter_by(id=cliente_id).first()
            if not cliente: return

            # Llenar cabecera y datos básicos
            self.detalle.lbl_nombre.setText(cliente.nombre_completo)
            self.detalle.edit_rif.setText(cliente.rif)
            self.detalle.edit_nombre.setText(cliente.nombre_completo)
            self.detalle.edit_email.setText(cliente.email)
            self.detalle.edit_tlf.setText(cliente.telefono)
            self.detalle.edit_dir.setText(cliente.direccion)
            self.detalle.edit_ciudad.setText(cliente.ciudad)
            
            # Seleccionar banco asociado
            index = self.detalle.combo_banco.findData(cliente.id_banco)
            self.detalle.combo_banco.setCurrentIndex(index)

            # Mostrar la vista de detalle
            self.view_stack.setCurrentIndex(1)
        finally:
            session.close()

    def guardar_cliente(self):
        """Lógica para actualizar o crear desde la vista de detalle"""
        session = self.db_engine.get_session()
        try:
            rif = self.detalle.edit_rif.text().strip()
            # Buscar si existe
            cliente = session.query(ClienteDB).filter_by(rif=rif).first()
            
            if not cliente:
                cliente = ClienteDB(rif=rif)
                session.add(cliente)

            # Mapear campos de la UI al Modelo
            cliente.nombre_completo = self.detalle.edit_nombre.text()
            cliente.email = self.detalle.edit_email.text()
            cliente.telefono = self.detalle.edit_tlf.text()
            cliente.direccion = self.detalle.edit_dir.text()
            cliente.id_banco = self.detalle.combo_banco.currentData()
            
            session.commit()
            QMessageBox.information(self.detalle, "Éxito", "Información actualizada correctamente.")
            self.actualizar_tabla()
            self.view_stack.setCurrentIndex(0) # Volver a la lista
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self.detalle, "Error", f"No se pudo guardar: {str(e)}")
        finally:
            session.close()