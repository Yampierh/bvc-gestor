# src/bvc_gestor/ui/controllers/clientes_controller.py
from contextlib import contextmanager
from typing import Optional, List
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog
from PyQt6.QtCore import Qt, QDate, QUrl
from PyQt6.QtGui import QDesktopServices
import os
from sqlalchemy.orm import joinedload

from ..database.engine import get_database
from ..database.models_sql import (
    ClienteDB, BancoDB, CasaBolsaDB, 
    CuentaBancariaDB, CuentaBursatilDB,
    DocumentoDB
)
from ..utils.constants import TipoInversor


class ClientesController:
    """Controlador completo para gestión de clientes"""
    
    def __init__(self, main_view):
        self.view_stack = main_view
        self.lista = main_view.view_lista
        self.detalle = main_view.view_detalle
        self.db_engine = get_database()
        
        self._connect_signals()
        self._init_data()

    def _connect_signals(self):
        """Conectar todas las señales"""
        self.lista.btn_nuevo.clicked.connect(self.nuevo_cliente)
        self.lista.cliente_seleccionado.connect(self.cargar_cliente)
        self.lista.search_bar.textChanged.connect(self.filtrar_tabla)
        self.detalle.btn_save.clicked.connect(self.guardar_cliente)
        self.detalle.btn_delete.clicked.connect(self.borrar_cliente)
        self.detalle.back_clicked.connect(self.volver_lista)
        self.detalle.documento_agregado.connect(self.manejar_documento)

    def _init_data(self):
        """Inicializar datos"""
        self.filtrar_tabla()

    @contextmanager
    def _get_session(self):
        """Context manager para sesiones de BD"""
        session = self.db_engine.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ============= MÉTODOS PÚBLICOS PRINCIPALES =============

    def nuevo_cliente(self):
        """Preparar formulario para nuevo cliente"""
        self._limpiar_formulario()
        self._cargar_catalogos()
        self._setup_widgets_dinamicos()
        self._mostrar_detalle("Nuevo Cliente")

    def cargar_cliente(self, cliente_id):
        """Cargar cliente existente para edición"""
        with self._get_session() as session:
            cliente = self._obtener_cliente_completo(session, cliente_id)
            if not cliente:
                QMessageBox.warning(self.detalle, "Error", "Cliente no encontrado")
                return
            
            self._cargar_catalogos()
            self._cargar_datos_cliente(cliente)
            self._mostrar_detalle(cliente.nombre_completo)

    def guardar_cliente(self):
        """Guardar cliente con todas sus relaciones"""
        rif = self.detalle.txt_rif.text().strip()
        
        if not rif:
            QMessageBox.warning(self.detalle, "Error", "RIF/Cédula es obligatorio")
            return
        
        if not self._validar_datos():
            return
        
        with self._get_session() as session:
            try:
                cliente = self._obtener_o_crear_cliente(session, rif)
                es_nuevo = cliente.id is None
                
                self._actualizar_datos_cliente(cliente)
                self._actualizar_cuentas_bancarias(session, cliente)
                self._actualizar_cuentas_bursatiles(session, cliente)
                # Documentos se manejan por separado
                
                mensaje = "creado" if es_nuevo else "actualizado"
                QMessageBox.information(self.detalle, "Éxito", f"Cliente {mensaje} correctamente")
                
                self.filtrar_tabla()
                self.volver_lista()
                
            except Exception as e:
                QMessageBox.critical(self.detalle, "Error", f"No se pudo guardar: {str(e)}")

    def borrar_cliente(self):
        """Borrar cliente o limpiar formulario"""
        rif = self.detalle.txt_rif.text().strip()
        
        if not rif:
            # Solo borrar formulario
            confirm = QMessageBox.question(
                self.detalle, "Limpiar formulario",
                "¿Borrar todos los datos del formulario?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                self.nuevo_cliente()
                QMessageBox.information(self.detalle, "Éxito", "Formulario limpiado")
            return
        
        # Borrar cliente de la base de datos
        with self._get_session() as session:
            cliente = session.query(ClienteDB).filter_by(rif_cedula=rif, estatus=True).first()
            
            if not cliente:
                QMessageBox.warning(self.detalle, "Error", "Cliente no encontrado")
                return
            
            confirm = QMessageBox.question(
                self.detalle, "Confirmar borrado",
                f"¿Está seguro de borrar al cliente '{cliente.nombre_completo}'?\n\n"
                f"RIF: {cliente.rif_cedula}\n"
                f"Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    # Soft delete
                    cliente.estatus = False
                    session.commit()
                    QMessageBox.information(self.detalle, "Éxito", "Cliente eliminado correctamente")
                    self.filtrar_tabla()
                    self.volver_lista()
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self.detalle, "Error", f"No se pudo eliminar: {str(e)}")

    def filtrar_tabla(self):
        """Filtrar tabla de clientes titulos"""
        filtro = self.lista.search_bar.text()
        
        with self._get_session() as session:
            query = session.query(ClienteDB).filter(ClienteDB.estatus == True)
            
            if filtro:
                query = query.filter(
                    ClienteDB.rif_cedula.ilike(f"%{filtro}%") |
                    ClienteDB.nombre_completo.ilike(f"%{filtro}%")
                )
            
            clientes = query.order_by(ClienteDB.nombre_completo).all()
            self._actualizar_tabla(clientes)

    def manejar_documento(self, datos):
        """Manejar subida/gestión de documentos"""
        if datos.get("accion") == "agregar":
            self._subir_documento()

    # ============= MÉTODOS PRIVADOS =============

    def _limpiar_formulario(self):
        """Limpiar formulario completamente"""
        # Limpiar campos básicos
        self.detalle.txt_nombre.clear()
        self.detalle.txt_rif.clear()
        self.detalle.txt_email.clear()
        self.detalle.txt_telefono.clear()
        self.detalle.txt_direccion.clear()
        self.detalle.txt_ciudad.clear()
        
        # Resetear combos
        if self.detalle.cmb_tipo.count() > 0:
            self.detalle.cmb_tipo.setCurrentIndex(0)
        
        
        # Limpiar widgets dinámicos
        self.detalle.clear_dynamic()

    def _cargar_catalogos(self):
        """Cargar todos los catálogos necesarios"""
        with self._get_session() as session:
            # Bancos
            bancos = session.query(BancoDB).filter(BancoDB.estatus == True).all()
            self.detalle.bancos = [
                {"id": b.id, "nombre": f"{b.rif} | {b.nombre}"}
                for b in bancos
            ]
            
            # Casas de bolsa
            corredores = session.query(CasaBolsaDB).filter(CasaBolsaDB.estatus == True).all()
            self.detalle.corredores = [
                {"id": c.id, "nombre": f"{c.rif} | {c.nombre}"}
                for c in corredores
            ]
            
            # Tipos de inversor
            self.detalle.load_combos(TipoInversor)

    def _setup_widgets_dinamicos(self):
        """Configurar widgets dinámicos iniciales"""
        self.detalle.add_cuenta_banco()
        self.detalle.add_cuenta_bursatil()

    def _mostrar_detalle(self, titulo):
        """Mostrar vista de detalle"""
        self.detalle.lbl_title.setText(titulo)
        self.view_stack.setCurrentIndex(1)
        self.detalle.txt_nombre.setFocus()

    def _obtener_cliente_completo(self, session, cliente_id):
        """Obtener cliente con todas sus relaciones"""
        return session.query(ClienteDB).options(
            joinedload(ClienteDB.cuentas_bancarias),
            joinedload(ClienteDB.cuentas_bursatiles),
            joinedload(ClienteDB.documentos)
        ).filter_by(id=cliente_id, estatus=True).first()

    def _cargar_datos_cliente(self, cliente):
        """Cargar datos del cliente en formulario"""
        # Datos básicos
        self.detalle.txt_rif.setText(cliente.rif_cedula)
        self.detalle.txt_nombre.setText(cliente.nombre_completo)
        self.detalle.txt_email.setText(cliente.email)
        self.detalle.txt_telefono.setText(cliente.telefono)
        self.detalle.txt_direccion.setPlainText(cliente.direccion_fiscal)
        self.detalle.txt_ciudad.setText(cliente.ciudad_estado)
        
        # Tipo de inversor
        if cliente.tipo_inversor:
            index = self.detalle.cmb_tipo.findData(cliente.tipo_inversor)
            if index >= 0:
                self.detalle.cmb_tipo.setCurrentIndex(index)

        
        # Limpiar widgets existentes
        self.detalle.clear_dynamic()
        
        # Cuentas bancarias
        if cliente.cuentas_bancarias:
            for cuenta in cliente.cuentas_bancarias:
                self.detalle.add_cuenta_banco(
                    banco_id=cuenta.banco_id,
                    numero=cuenta.numero_cuenta,
                    tipo=cuenta.tipo_cuenta,
                    principal=cuenta.default
                )
        
        # Cuentas bursátiles
        if cliente.cuentas_bursatiles:
            for cuenta in cliente.cuentas_bursatiles:
                self.detalle.add_cuenta_bursatil(
                    casa_id=cuenta.casa_bolsa_id,
                    cuenta=cuenta.cuenta,
                    tipo="Individual",  # Por defecto
                    default=cuenta.default
                )
        
        # Si no hay cuentas, agregar vacías
        if not cliente.cuentas_bancarias:
            self.detalle.add_cuenta_banco()
        if not cliente.cuentas_bursatiles:
            self.detalle.add_cuenta_bursatil()
        
        # Documentos (opcional - cargaría en una lista separada)
        if cliente.documentos:
            for doc in cliente.documentos:
                self.detalle.add_documento(
                    tipo_doc=doc.tipo_documento,
                    nombre=doc.nombre_archivo,
                    ruta=doc.ruta_archivo
                )

    def _validar_datos(self):
        """Validar datos antes de guardar"""
        errores = []
        
        if not self.detalle.txt_nombre.text().strip():
            errores.append("Nombre completo es obligatorio")
        
        if not self.detalle.txt_email.text().strip():
            errores.append("Correo electrónico es obligatorio")
        
        if not self.detalle.txt_telefono.text().strip():
            errores.append("Teléfono es obligatorio")
        
        if not self.detalle.txt_direccion.toPlainText().strip():
            errores.append("Dirección fiscal es obligatoria")
        
        if not self.detalle.txt_ciudad.text().strip():
            errores.append("Ciudad/Estado es obligatorio")
        
        # Validar que al menos haya una cuenta bancaria con datos
        datos_bancos = self.detalle.get_bancos_data()
        if not any(d.get("banco_id") and d.get("numero_cuenta") for d in datos_bancos):
            errores.append("Al menos una cuenta bancaria completa es requerida")
        
        if errores:
            QMessageBox.warning(
                self.detalle, 
                "Error de validación", 
                "Por favor corrija los siguientes errores:\n\n• " + "\n• ".join(errores)
            )
            return False
        
        return True

    def _obtener_o_crear_cliente(self, session, rif):
        """Obtener cliente existente o crear nuevo"""
        cliente = session.query(ClienteDB).filter_by(rif_cedula=rif).first()
        
        if not cliente:
            cliente = ClienteDB(rif_cedula=rif)
            session.add(cliente)
        elif not cliente.estatus:
            cliente.estatus = True  # Reactivar si estaba eliminado
        
        return cliente

    def _actualizar_datos_cliente(self, cliente):
        """Actualizar datos básicos del cliente"""
        cliente.nombre_completo = self.detalle.txt_nombre.text().strip()
        cliente.email = self.detalle.txt_email.text().strip()
        cliente.telefono = self.detalle.txt_telefono.text().strip()
        cliente.direccion_fiscal = self.detalle.txt_direccion.toPlainText().strip()
        cliente.ciudad_estado = self.detalle.txt_ciudad.text().strip()
        
        tipo = self.detalle.cmb_tipo.currentData()
        if tipo:
            cliente.tipo_inversor = tipo
        

    def _actualizar_cuentas_bancarias(self, session, cliente):
        """Actualizar cuentas bancarias del cliente"""
        # Eliminar cuentas existentes
        for cuenta in cliente.cuentas_bancarias:
            session.delete(cuenta)
        cliente.cuentas_bancarias.clear()
        
        # Agregar nuevas cuentas
        datos_bancos = self.detalle.get_bancos_data()
        for datos in datos_bancos:
            if datos.get("banco_id") and datos.get("numero_cuenta"):
                cuenta = CuentaBancariaDB(
                    banco_id=datos["banco_id"],
                    numero_cuenta=datos["numero_cuenta"],
                    tipo_cuenta=datos.get("tipo_cuenta", "Corriente"),
                    default=datos.get("default", False)
                )
                cliente.cuentas_bancarias.append(cuenta)

    def _actualizar_cuentas_bursatiles(self, session, cliente):
        """Actualizar cuentas bursátiles del cliente"""
        # Eliminar cuentas existentes
        for cuenta in cliente.cuentas_bursatiles:
            session.delete(cuenta)
        cliente.cuentas_bursatiles.clear()
        
        # Agregar nuevas cuentas
        datos_bursatiles = self.detalle.get_bursatiles_data()
        for datos in datos_bursatiles:
            if datos.get("casa_bolsa_id") and datos.get("cuenta"):
                cuenta = CuentaBursatilDB(
                    casa_bolsa_id=datos["casa_bolsa_id"],
                    cuenta=datos["cuenta"],
                    default=datos.get("default", False)
                )
                cliente.cuentas_bursatiles.append(cuenta)

    def _subir_documento(self):
        """Manejar subida de documentos"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Documentos (*.pdf *.jpg *.jpeg *.png *.doc *.docx)")
        
        if file_dialog.exec():
            archivos = file_dialog.selectedFiles()
            if archivos:
                ruta = archivos[0]
                nombre = os.path.basename(ruta)
                
                # Aquí normalmente se copiaría el archivo a una carpeta segura
                # Por ahora solo mostramos en la interfaz
                self.detalle.add_documento(
                    tipo_doc="Documento",
                    nombre=nombre,
                    ruta=ruta
                )

    def _actualizar_tabla(self, clientes):
        """Actualizar tabla de clientes"""
        tabla = self.lista.table
        tabla.setRowCount(0)
        
        for cliente in clientes:
            row = tabla.rowCount()
            tabla.insertRow(row)
            
            item_rif = QTableWidgetItem(cliente.rif_cedula)
            item_rif.setData(Qt.ItemDataRole.UserRole, cliente.id)
            
            tabla.setItem(row, 0, item_rif)
            tabla.setItem(row, 1, QTableWidgetItem(cliente.nombre_completo))
            tabla.setItem(row, 2, QTableWidgetItem(cliente.tipo_inversor.value))
            tabla.setItem(row, 3, QTableWidgetItem(cliente.email))
            tabla.setItem(row, 4, QTableWidgetItem(cliente.telefono))

    def volver_lista(self):
        """Volver a la vista de lista"""
        self.view_stack.setCurrentIndex(0)