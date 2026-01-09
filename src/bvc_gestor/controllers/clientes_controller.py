from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from ..database.engine import get_database
from ..database.models_sql import ClienteDB, BancoDB, CasaBolsaDB
from ..utils.constants import TipoInversor, PerfilRiesgo
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
        self.detalle.btn_delete.clicked.connect(self.borrar_cliente)
        self.detalle.back_clicked.connect(lambda: self.view_stack.setCurrentIndex(0))

        # Inicialización
        self.actualizar_tabla()
        self.precargar_catalogos()

    def preparar_nuevo_cliente(self):
        """Limpia el formulario y cambia a la vista de detalle"""
        # 1. Limpiar campos de texto
        self.detalle.edit_nombre.clear()
        self.detalle.edit_rif.clear()
        self.detalle.edit_cvv.clear()
        self.detalle.edit_email.clear()
        self.detalle.edit_tlf.clear()
        self.detalle.edit_cuenta_num.clear()
        self.detalle.edit_dir.clear()

        # 2. Resetear combos (seleccionar por defecto)
        if self.detalle.combo_banco.count() > 0:
            self.detalle.combo_banco.setCurrentIndex(0)
        if self.detalle.combo_casa_bolsa.count() > 0:
            self.detalle.combo_casa_bolsa.setCurrentIndex(0)
        if self.detalle.combo_perfil.count() > 0:
            self.detalle.combo_perfil.setCurrentIndex(1)
        if self.detalle.combo_estado.count() > 0:
            self.detalle.combo_estado.setCurrentIndex(0)
        if self.detalle.combo_tipo_inversor.count() > 0:
            self.detalle.combo_tipo_inversor.setCurrentIndex(0)
            
        # 3. Cambiar la vista al Detalle (Index 1)
        self.view_stack.setCurrentIndex(1)
        
        # Opcional: Poner el foco en el primer campo
        self.detalle.edit_nombre.setFocus()

    def precargar_catalogos(self):
        """Carga bancos en los combos del detalle"""
        
        session = self.db_engine.get_session()
        try:
            # --- 1. Llenar Bancos desde la DB ---
            self.detalle.combo_banco.clear()
            self.detalle.combo_banco.addItem("-- Seleccione un Banco --", None)
            
            bancos = session.query(BancoDB).filter_by(estatus=True).order_by(BancoDB.nombre).all()
            for banco in bancos:
                # addItem(texto_visible, data_interna)
                self.detalle.combo_banco.addItem(banco.nombre, banco.id)
            
            # --- 2. Llenar Perfil de Riesgo (desde constants.py) ---
            if hasattr(self.detalle, 'combo_perfil'):
                self.detalle.combo_perfil.clear()
                self.detalle.combo_perfil.addItem("-- Seleccione un Perfil --", None)
                for perfil in PerfilRiesgo:
                    self.detalle.combo_perfil.addItem(perfil.value, perfil)

            # --- 3. Llenar Tipo de Persona (desde constants.py) ---
            if hasattr(self.detalle, 'combo_tipo_inversor'):
                self.detalle.combo_tipo_inversor.clear()
                self.detalle.combo_tipo_inversor.addItem("-- Seleccione un Tipo --", None)
                for tipo in TipoInversor:
                    self.detalle.combo_tipo_inversor.addItem(tipo.value, tipo)

            # --- 4. Llenar Casas de Bolsa (si agregaste el combo) ---
            if hasattr(self.detalle, 'combo_casa_bolsa'):
                self.detalle.combo_casa_bolsa.clear()
                self.detalle.combo_casa_bolsa.addItem("-- Seleccione una Casa --", None)
                casas = session.query(CasaBolsaDB).order_by(CasaBolsaDB.nombre).all()
                for casa in casas:
                    self.detalle.combo_casa_bolsa.addItem(casa.nombre, casa.id)
        finally:
            session.close()

    def actualizar_tabla(self):
        filtro = self.lista.search_bar.text()
        session = self.db_engine.get_session()
        try:
            query = session.query(ClienteDB).filter(ClienteDB.estatus == True)
            if filtro:
                query = query.filter(
                    (ClienteDB.rif_cedula.ilike(f"%{filtro}%")) | 
                    (ClienteDB.nombre_completo.ilike(f"%{filtro}%"))
                )
            
            clientes = query.all()
            self.lista.table.setRowCount(0)
            for c in clientes:
                row = self.lista.table.rowCount()
                self.lista.table.insertRow(row)
                
                # Guardamos el ID en el UserRole para recuperarlo luego
                item_rif = QTableWidgetItem(str(c.rif_cedula))
                item_rif.setData(Qt.ItemDataRole.UserRole, c.id)
                
                self.lista.table.setItem(row, 0, item_rif)
                self.lista.table.setItem(row, 1, QTableWidgetItem(c.nombre_completo))
                self.lista.table.setItem(row, 2, QTableWidgetItem(c.tipo_inversor.value))
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
            self.detalle.edit_rif.setText(cliente.rif_cedula)
            self.detalle.edit_nombre.setText(cliente.nombre_completo)
            self.detalle.edit_email.setText(cliente.email)
            self.detalle.edit_tlf.setText(cliente.telefono)
            self.detalle.edit_dir.setText(cliente.direccion_fiscal)
            self.detalle.edit_ciudad.setText(cliente.ciudad_estado)

            # Mostrar la vista de detalle
            self.view_stack.setCurrentIndex(1)
        finally:
            session.close()

    def borrar_cliente(self):
        
        session = self.db_engine.get_session()
        try:
            rif = self.detalle.edit_rif.text().strip()
            cliente = session.query(ClienteDB).filter_by(rif_cedula=rif).first()
            
            not_confirm = QMessageBox.question(
                self.detalle, "Confirmar Borrado de formulario",
                f"¿Está seguro de que desea borrar todo?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if not_confirm == QMessageBox.StandardButton.Yes:
                
                """Lógica para borrar un Formulario desde la vista de detalle"""
                # 1. Limpiar campos de texto
                self.detalle.edit_nombre.clear()
                self.detalle.edit_rif.clear()
                self.detalle.edit_cvv.clear()
                self.detalle.edit_email.clear()
                self.detalle.edit_tlf.clear()
                self.detalle.edit_cuenta_num.clear()
                self.detalle.edit_dir.clear()

                # 2. Resetear combos (seleccionar el primer banco por defecto)
                if self.detalle.combo_banco.count() > 0:
                    self.detalle.combo_banco.setCurrentIndex(0)
                if self.detalle.combo_casa_bolsa.count() > 0:
                    self.detalle.combo_casa_bolsa.setCurrentIndex(0)
                if self.detalle.combo_perfil.count() > 0:
                    self.detalle.combo_perfil.setCurrentIndex(1)
                if self.detalle.combo_estado.count() > 0:
                    self.detalle.combo_estado.setCurrentIndex(0)
                if self.detalle.combo_tipo_inversor.count() > 0:
                    self.detalle.combo_tipo_inversor.setCurrentIndex(0)
                
                # Opcional: Poner el foco en el primer campo
                self.detalle.edit_nombre.setFocus()
                QMessageBox.information(self.detalle, "Éxito", "Formulario borrado correctamente.")
                self.actualizar_tabla()
                self.view_stack.setCurrentIndex(0) # Volver a la lista
                return
            
            confirm = QMessageBox.question(
                self.detalle, "Confirmar Borrado",
                f"¿Está seguro de que desea borrar al cliente '{cliente.nombre_completo}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                session.delete(cliente)
                session.commit()
                QMessageBox.information(self.detalle, "Éxito", "Cliente borrado correctamente.")
                self.actualizar_tabla()
                self.view_stack.setCurrentIndex(0) # Volver a la lista
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self.detalle, "Error", f"No se pudo borrar: {str(e)}")
        finally:
            session.close()
    
    def guardar_cliente(self):
        """Lógica para actualizar o crear desde la vista de detalle"""
        session = self.db_engine.get_session()
        try:
            rif = self.detalle.edit_rif.text().strip()
            # Buscar si existe el cliente por RIF
            cliente = session.query(ClienteDB).filter_by(rif_cedula=rif).first()
            
            if not cliente:
                cliente = ClienteDB(rif_cedula=rif)
                session.add(cliente)

            # Mapear campos de la UI al Modelo
            cliente.nombre_completo = self.detalle.edit_nombre.text()
            cliente.rif_cedula = self.detalle.edit_rif.text()
            cliente.email = self.detalle.edit_email.text()
            cliente.telefono = self.detalle.edit_tlf.text()
            cliente.direccion_fiscal = self.detalle.edit_dir.text()
            cliente.ciudad_estado = self.detalle.edit_ciudad.text()            
            
            # Guardar cambios y actualizar la tabla
            session.commit()
            QMessageBox.information(self.detalle, "Éxito", "Información actualizada correctamente.")
            self.actualizar_tabla()
            self.view_stack.setCurrentIndex(0) # Volver a la lista
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self.detalle, "Error", f"No se pudo guardar: {str(e)}")
        finally:
            session.close()