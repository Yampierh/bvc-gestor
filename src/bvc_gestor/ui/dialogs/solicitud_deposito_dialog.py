"""
Diálogo para solicitar depósitos a cuentas bancarias.
Genera PDF con instrucciones de transferencia.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QMessageBox,
    QFileDialog, QFrame, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from datetime import datetime
import locale

# Configurar locale para formato de moneda
try:
    locale.setlocale(locale.LC_ALL, 'es_VE.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Spanish_Venezuela')
    except:
        locale.setlocale(locale.LC_ALL, '')


class SolicitudDepositoDialog(QDialog):
    """
    Diálogo para crear solicitudes de depósito.
    
    Signals:
        deposito_solicitado: Emitido cuando se crea la solicitud
    """
    
    deposito_solicitado = pyqtSignal(dict)  # info del depósito
    
    def __init__(self, parent=None, controller=None, inversor_id=None, 
                cuenta_bancaria_id=None, monto_sugerido=None):
        super().__init__(parent)
        self.controller = controller
        self.inversor_id = inversor_id
        self.cuenta_bancaria_id = cuenta_bancaria_id
        self.monto_sugerido = monto_sugerido
        
        self.inversor_data = None
        self.cuenta_bancaria_data = None
        
        self.setWindowTitle("Solicitud de Depósito")
        self.setModal(True)
        self.resize(700, 800)
        
        self.setup_ui()
        self.cargar_datos_iniciales()
        self.aplicar_estilos()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel("💰 Solicitud de Depósito")
        header_label.setObjectName("dialogHeader")
        layout.addWidget(header_label)
        
        # Descripción
        desc_label = QLabel(
            "Complete los datos del depósito que realizará a su cuenta bancaria. "
            "Se generará un PDF con las instrucciones para su registro."
        )
        desc_label.setWordWrap(True)
        desc_label.setObjectName("dialogDescription")
        layout.addWidget(desc_label)
        
        # Scroll area para el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # --- SECCIÓN 1: INFORMACIÓN DEL INVERSOR ---
        scroll_layout.addWidget(self._crear_seccion_inversor())
        
        # --- SECCIÓN 2: CUENTA DE DESTINO ---
        scroll_layout.addWidget(self._crear_seccion_cuenta())
        
        # --- SECCIÓN 3: DATOS DEL DEPÓSITO ---
        scroll_layout.addWidget(self._crear_seccion_deposito())
        
        # --- SECCIÓN 4: OBSERVACIONES ---
        scroll_layout.addWidget(self._crear_seccion_observaciones())
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)
        
        # --- BOTONES ---
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.btn_generar_pdf = QPushButton("📄 Generar PDF")
        self.btn_generar_pdf.setObjectName("primaryButton")
        self.btn_generar_pdf.clicked.connect(self.generar_pdf)
        
        self.btn_guardar = QPushButton("💾 Guardar y Cerrar")
        self.btn_guardar.setObjectName("successButton")
        self.btn_guardar.clicked.connect(self.guardar_deposito)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("secondaryButton")
        self.btn_cancelar.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.btn_generar_pdf)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_cancelar)
        buttons_layout.addWidget(self.btn_guardar)
        
        layout.addLayout(buttons_layout)
    
    def _crear_seccion_inversor(self):
        """Crea la sección de información del inversor"""
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("👤 Información del Inversor")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Nombre
        self.lbl_inversor_nombre = QLabel("Cargando...")
        self.lbl_inversor_nombre.setObjectName("dataLabel")
        layout.addWidget(self._crear_campo_info("Nombre:", self.lbl_inversor_nombre))
        
        # Cédula
        self.lbl_inversor_cedula = QLabel("Cargando...")
        self.lbl_inversor_cedula.setObjectName("dataLabel")
        layout.addWidget(self._crear_campo_info("Cédula:", self.lbl_inversor_cedula))
        
        return frame
    
    def _crear_seccion_cuenta(self):
        """Crea la sección de cuenta de destino"""
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("🏦 Cuenta de Destino")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Banco
        self.lbl_banco = QLabel("Cargando...")
        self.lbl_banco.setObjectName("dataLabel")
        layout.addWidget(self._crear_campo_info("Banco:", self.lbl_banco))
        
        # Número de cuenta
        self.lbl_numero_cuenta = QLabel("Cargando...")
        self.lbl_numero_cuenta.setObjectName("dataLabel")
        layout.addWidget(self._crear_campo_info("Número de Cuenta:", self.lbl_numero_cuenta))
        
        # Tipo de cuenta
        self.lbl_tipo_cuenta = QLabel("Cargando...")
        self.lbl_tipo_cuenta.setObjectName("dataLabel")
        layout.addWidget(self._crear_campo_info("Tipo:", self.lbl_tipo_cuenta))
        
        return frame
    
    def _crear_seccion_deposito(self):
        """Crea la sección de datos del depósito"""
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("💵 Datos del Depósito")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Monto
        monto_layout = QVBoxLayout()
        monto_layout.setSpacing(5)
        
        lbl_monto = QLabel("Monto a Depositar (Bs.):*")
        lbl_monto.setObjectName("fieldLabel")
        
        self.input_monto = QLineEdit()
        self.input_monto.setPlaceholderText("0.00")
        self.input_monto.setObjectName("formInput")
        validator = QDoubleValidator(0.01, 999999999.99, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.input_monto.setValidator(validator)
        
        if self.monto_sugerido:
            self.input_monto.setText(f"{self.monto_sugerido:.2f}")
        
        self.input_monto.textChanged.connect(self.actualizar_monto_formateado)
        
        self.lbl_monto_formateado = QLabel("")
        self.lbl_monto_formateado.setObjectName("montoFormateado")
        
        monto_layout.addWidget(lbl_monto)
        monto_layout.addWidget(self.input_monto)
        monto_layout.addWidget(self.lbl_monto_formateado)
        
        layout.addLayout(monto_layout)
        
        # Fecha del depósito
        fecha_layout = QVBoxLayout()
        fecha_layout.setSpacing(5)
        
        lbl_fecha = QLabel("Fecha del Depósito:*")
        lbl_fecha.setObjectName("fieldLabel")
        
        self.input_fecha = QDateEdit()
        self.input_fecha.setDate(QDate.currentDate())
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDisplayFormat("dd/MM/yyyy")
        self.input_fecha.setObjectName("formInput")
        
        fecha_layout.addWidget(lbl_fecha)
        fecha_layout.addWidget(self.input_fecha)
        
        layout.addLayout(fecha_layout)
        
        # Referencia
        ref_layout = QVBoxLayout()
        ref_layout.setSpacing(5)
        
        lbl_ref = QLabel("Número de Referencia:")
        lbl_ref.setObjectName("fieldLabel")
        
        self.input_referencia = QLineEdit()
        self.input_referencia.setPlaceholderText("Ej: 123456789")
        self.input_referencia.setObjectName("formInput")
        self.input_referencia.setMaxLength(50)
        
        ref_layout.addWidget(lbl_ref)
        ref_layout.addWidget(self.input_referencia)
        
        layout.addLayout(ref_layout)
        
        return frame
    
    def _crear_seccion_observaciones(self):
        """Crea la sección de observaciones"""
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("📝 Observaciones")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # TextEdit
        self.input_observaciones = QTextEdit()
        self.input_observaciones.setPlaceholderText(
            "Ingrese cualquier observación o detalle adicional sobre el depósito..."
        )
        self.input_observaciones.setObjectName("formTextArea")
        self.input_observaciones.setMaximumHeight(100)
        
        layout.addWidget(self.input_observaciones)
        
        return frame
    
    def _crear_campo_info(self, label_text, value_widget):
        """Helper para crear campos de información"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        label = QLabel(label_text)
        label.setObjectName("infoLabel")
        label.setMinimumWidth(150)
        
        layout.addWidget(label)
        layout.addWidget(value_widget, 1)
        
        return container
    
    def cargar_datos_iniciales(self):
        """Carga los datos del inversor y cuenta bancaria"""
        if not self.controller:
            return
        
        try:
            # Cargar datos del inversor
            if self.inversor_id:
                self.inversor_data = self.controller.obtener_inversor_por_id(self.inversor_id)
                if self.inversor_data:
                    self.lbl_inversor_nombre.setText(self.inversor_data.get('nombre_completo', 'N/A'))
                    self.lbl_inversor_cedula.setText(self.inversor_data.get('cedula', 'N/A'))
            
            # Cargar datos de la cuenta bancaria
            if self.cuenta_bancaria_id:
                self.cuenta_bancaria_data = self.controller.obtener_cuenta_bancaria_por_id(
                    self.cuenta_bancaria_id
                )
                if self.cuenta_bancaria_data:
                    self.lbl_banco.setText(self.cuenta_bancaria_data.get('banco', 'N/A'))
                    self.lbl_numero_cuenta.setText(self.cuenta_bancaria_data.get('numero_cuenta', 'N/A'))
                    self.lbl_tipo_cuenta.setText(self.cuenta_bancaria_data.get('tipo_cuenta', 'N/A'))
        
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error al Cargar Datos",
                f"No se pudieron cargar los datos iniciales:\n{str(e)}"
            )
    
    def actualizar_monto_formateado(self, texto):
        """Muestra el monto formateado en bolivares"""
        try:
            if texto and float(texto.replace(',', '.')) > 0:
                monto = float(texto.replace(',', '.'))
                # Formatear con separadores de miles
                monto_fmt = f"{monto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                self.lbl_monto_formateado.setText(f"Bs. {monto_fmt}")
            else:
                self.lbl_monto_formateado.setText("")
        except ValueError:
            self.lbl_monto_formateado.setText("")
    
    def validar_formulario(self):
        """Valida que todos los campos obligatorios estén completos"""
        # Validar monto
        monto_text = self.input_monto.text().strip()
        if not monto_text:
            QMessageBox.warning(self, "Campo Requerido", "Debe ingresar el monto del depósito.")
            self.input_monto.setFocus()
            return False
        
        try:
            monto = float(monto_text.replace(',', '.'))
            if monto <= 0:
                QMessageBox.warning(self, "Monto Inválido", "El monto debe ser mayor a cero.")
                self.input_monto.setFocus()
                return False
        except ValueError:
            QMessageBox.warning(self, "Monto Inválido", "Ingrese un monto válido.")
            self.input_monto.setFocus()
            return False
        
        # Validar fecha
        fecha = self.input_fecha.date()
        if not fecha.isValid():
            QMessageBox.warning(self, "Fecha Inválida", "Seleccione una fecha válida.")
            return False
        
        # Validar que no sea fecha futura
        if fecha > QDate.currentDate():
            QMessageBox.warning(
                self, 
                "Fecha Inválida", 
                "La fecha del depósito no puede ser futura."
            )
            return False
        
        return True
    
    def obtener_datos_deposito(self):
        """Retorna los datos del depósito como diccionario"""
        monto = float(self.input_monto.text().replace(',', '.'))
        fecha = self.input_fecha.date().toPyDate()
        
        return {
            'inversor_id': self.inversor_id,
            'cuenta_bancaria_id': self.cuenta_bancaria_id,
            'monto': monto,
            'fecha_deposito': fecha,
            'referencia': self.input_referencia.text().strip() or None,
            'observaciones': self.input_observaciones.toPlainText().strip() or None,
            'estado': 'PENDIENTE',  # Estado inicial
            'inversor_nombre': self.lbl_inversor_nombre.text(),
            'inversor_cedula': self.lbl_inversor_cedula.text(),
            'banco': self.lbl_banco.text(),
            'numero_cuenta': self.lbl_numero_cuenta.text(),
            'tipo_cuenta': self.lbl_tipo_cuenta.text()
        }
    
    def guardar_deposito(self):
        """Guarda la solicitud de depósito en la BD"""
        if not self.validar_formulario():
            return
        
        try:
            datos = self.obtener_datos_deposito()
            
            # Guardar en BD a través del controller
            if self.controller:
                resultado = self.controller.crear_solicitud_deposito(datos)
                
                if resultado:
                    QMessageBox.information(
                        self,
                        "Depósito Registrado",
                        f"La solicitud de depósito por Bs. {datos['monto']:,.2f} "
                        f"ha sido registrada exitosamente.\n\n"
                        f"Estado: PENDIENTE\n"
                        f"Referencia: {datos['referencia'] or 'N/A'}"
                    )
                    
                    self.deposito_solicitado.emit(datos)
                    self.accept()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "No se pudo registrar el depósito. Intente nuevamente."
                    )
            else:
                # Modo sin controller (testing)
                self.deposito_solicitado.emit(datos)
                self.accept()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al Guardar",
                f"Ocurrió un error al guardar el depósito:\n{str(e)}"
            )
    
    def generar_pdf(self):
        """Genera el PDF con las instrucciones de depósito"""
        if not self.validar_formulario():
            return
        
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            
            # Pedir ubicación para guardar
            ruta, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar PDF",
                f"Solicitud_Deposito_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if not ruta:
                return
            
            datos = self.obtener_datos_deposito()
            
            # Crear documento
            doc = SimpleDocTemplate(ruta, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Estilos personalizados
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#FF6B00'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#333333'),
                spaceAfter=12,
                spaceBefore=20
            )
            
            # Título
            elements.append(Paragraph("SOLICITUD DE DEPÓSITO", title_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Información del Inversor
            elements.append(Paragraph("Información del Inversor", header_style))
            
            data_inversor = [
                ['Nombre:', datos['inversor_nombre']],
                ['Cédula:', datos['inversor_cedula']],
            ]
            
            table_inversor = Table(data_inversor, colWidths=[2*inch, 4*inch])
            table_inversor.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD'))
            ]))
            elements.append(table_inversor)
            
            # Cuenta Bancaria
            elements.append(Paragraph("Cuenta de Destino", header_style))
            
            data_cuenta = [
                ['Banco:', datos['banco']],
                ['Número de Cuenta:', datos['numero_cuenta']],
                ['Tipo de Cuenta:', datos['tipo_cuenta']],
            ]
            
            table_cuenta = Table(data_cuenta, colWidths=[2*inch, 4*inch])
            table_cuenta.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD'))
            ]))
            elements.append(table_cuenta)
            
            # Datos del Depósito
            elements.append(Paragraph("Detalles del Depósito", header_style))
            
            monto_fmt = f"Bs. {datos['monto']:,.2f}"
            fecha_fmt = datos['fecha_deposito'].strftime('%d/%m/%Y')
            
            data_deposito = [
                ['Monto:', monto_fmt],
                ['Fecha:', fecha_fmt],
                ['Referencia:', datos['referencia'] or 'N/A'],
            ]
            
            table_deposito = Table(data_deposito, colWidths=[2*inch, 4*inch])
            table_deposito.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#E8F5E9')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#2E7D32')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('FONTSIZE', (1, 0), (1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD'))
            ]))
            elements.append(table_deposito)
            
            # Observaciones
            if datos['observaciones']:
                elements.append(Paragraph("Observaciones", header_style))
                obs_style = ParagraphStyle(
                    'Observaciones',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=12
                )
                elements.append(Paragraph(datos['observaciones'], obs_style))
            
            # Footer
            elements.append(Spacer(1, 0.5*inch))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.gray,
                alignment=TA_CENTER
            )
            elements.append(Paragraph(
                f"Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')} | BVC Gestor",
                footer_style
            ))
            
            # Generar PDF
            doc.build(elements)
            
            QMessageBox.information(
                self,
                "PDF Generado",
                f"El PDF se ha generado exitosamente en:\n{ruta}"
            )
        
        except ImportError:
            QMessageBox.critical(
                self,
                "Biblioteca No Disponible",
                "La biblioteca ReportLab no está instalada.\n\n"
                "Para generar PDFs, instale: pip install reportlab"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al Generar PDF",
                f"Ocurrió un error al generar el PDF:\n{str(e)}"
            )
    
    def aplicar_estilos(self):
        """Aplica los estilos CSS al diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            
            #dialogHeader {
                font-size: 24px;
                font-weight: bold;
                color: #FF6B00;
                padding: 10px 0;
            }
            
            #dialogDescription {
                font-size: 13px;
                color: #AAAAAA;
                line-height: 1.5;
            }
            
            #sectionFrame {
                background-color: #2D2D2D;
                border-radius: 8px;
                padding: 20px;
            }
            
            #sectionTitle {
                font-size: 16px;
                font-weight: bold;
                color: #FF6B00;
                padding-bottom: 10px;
                border-bottom: 2px solid #3D3D3D;
            }
            
            #infoLabel {
                font-size: 13px;
                color: #AAAAAA;
                font-weight: bold;
            }
            
            #dataLabel {
                font-size: 14px;
                color: #FFFFFF;
                padding: 5px 10px;
                background-color: #1E1E1E;
                border-radius: 4px;
            }
            
            #fieldLabel {
                font-size: 13px;
                color: #CCCCCC;
                font-weight: bold;
            }
            
            #formInput {
                background-color: #1E1E1E;
                border: 2px solid #3D3D3D;
                border-radius: 6px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 14px;
                min-height: 35px;
            }
            
            #formInput:focus {
                border: 2px solid #FF6B00;
            }
            
            #formTextArea {
                background-color: #1E1E1E;
                border: 2px solid #3D3D3D;
                border-radius: 6px;
                padding: 10px;
                color: #FFFFFF;
                font-size: 13px;
            }
            
            #formTextArea:focus {
                border: 2px solid #FF6B00;
            }
            
            #montoFormateado {
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                padding: 5px 0;
            }
            
            #primaryButton {
                background-color: #FF6B00;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
            }
            
            #primaryButton:hover {
                background-color: #FF8534;
            }
            
            #primaryButton:pressed {
                background-color: #CC5500;
            }
            
            #successButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
            }
            
            #successButton:hover {
                background-color: #66BB6A;
            }
            
            #successButton:pressed {
                background-color: #388E3C;
            }
            
            #secondaryButton {
                background-color: transparent;
                color: #AAAAAA;
                border: 2px solid #3D3D3D;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                min-width: 100px;
            }
            
            #secondaryButton:hover {
                border-color: #FF6B00;
                color: #FF6B00;
            }
            
            QScrollArea {
                border: none;
            }
            
            QDateEdit::drop-down {
                background-color: #3D3D3D;
                border: none;
                width: 25px;
            }
            
            QDateEdit::down-arrow {
                image: url(down_arrow.png);
                width: 25px;
            }""")