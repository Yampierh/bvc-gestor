# src/bvc_gestor/ui/styles/components/forms.py
"""
Estilos para formularios y controles de entrada
"""
from ..utils.color_palette import ColorPalette


class FormStyles:
    """Estilos para formularios de la aplicación"""
    
    @staticmethod
    def get_styles(theme: str = 'light') -> str:
        """Obtener estilos CSS para formularios"""
        colors = ColorPalette.get_palette(theme)
        
        return f"""
        /* ===== FORMULARIOS Y CONTROLES ===== */
        
        /* Labels de formulario */
        QLabel.form-label {{
            font-size: 14px;
            font-weight: 500;
            color: {colors['text']};
            margin-bottom: 4px;
        }}
        
        QLabel.form-label.required::after {{
            content: " *";
            color: {colors['danger']};
        }}
        
        /* Campos de texto */
        QLineEdit.form-input {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            min-height: 36px;
        }}
        
        QLineEdit.form-input:focus {{
            border: 2px solid {colors['primary']};
            padding: 7px 11px;
        }}
        
        QLineEdit.form-input:disabled {{
            background-color: {colors['disabled']};
            color: {colors['text_muted']};
        }}
        
        QLineEdit.form-input:read-only {{
            background-color: {colors['surface_secondary']};
        }}
        
        QLineEdit.form-input[data-state="valid"] {{
            border-color: {colors['success']};
        }}
        
        QLineEdit.form-input[data-state="invalid"] {{
            border-color: {colors['danger']};
        }}
        
        QLineEdit.form-input[data-state="warning"] {{
            border-color: {colors['warning']};
        }}
        
        /* Áreas de texto */
        QTextEdit.form-textarea {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            min-height: 80px;
        }}
        
        QTextEdit.form-textarea:focus {{
            border: 2px solid {colors['primary']};
            padding: 7px 11px;
        }}
        
        /* Combobox (dropdown) */
        QComboBox.form-select {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            min-height: 36px;
        }}
        
        QComboBox.form-select:focus {{
            border: 2px solid {colors['primary']};
            padding: 7px 11px;
        }}
        
        QComboBox.form-select:on {{ /* when the popup is open */
            padding-bottom: 7px;
        }}
        
        QComboBox.form-select::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox.form-select::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors['text_secondary']};
            margin-right: 10px;
        }}
        
        QComboBox.form-select QAbstractItemView {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            selection-background-color: {colors['selected']};
            selection-color: {colors['text_inverse']};
            padding: 4px;
        }}
        
        /* Spinboxes (números) */
        QSpinBox.form-spinbox, QDoubleSpinBox.form-spinbox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            min-height: 36px;
        }}
        
        QSpinBox.form-spinbox:focus, QDoubleSpinBox.form-spinbox:focus {{
            border: 2px solid {colors['primary']};
            padding: 7px 11px;
        }}
        
        /* Date/Time editors */
        QDateEdit.form-date, QDateTimeEdit.form-date {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: {colors['text']};
            min-height: 36px;
        }}
        
        QDateEdit.form-date:focus, QDateTimeEdit.form-date:focus {{
            border: 2px solid {colors['primary']};
            padding: 7px 11px;
        }}
        
        /* Checkboxes */
        QCheckBox.form-checkbox {{
            font-size: 14px;
            color: {colors['text']};
            spacing: 8px;
        }}
        
        QCheckBox.form-checkbox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {colors['border']};
            border-radius: 4px;
            background-color: {colors['surface']};
        }}
        
        QCheckBox.form-checkbox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
            image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path fill='white' d='M10.3 3.3L4.8 8.8 2.3 6.3c-.4-.4-.4-1 0-1.4.4-.4 1-.4 1.4 0l1.8 1.8 4.4-4.4c.4-.4 1-.4 1.4 0 .4.4.4 1 0 1.4z'/></svg>");
        }}
        
        QCheckBox.form-checkbox::indicator:disabled {{
            border-color: {colors['disabled']};
            background-color: {colors['disabled']};
        }}
        
        /* Radio buttons */
        QRadioButton.form-radio {{
            font-size: 14px;
            color: {colors['text']};
            spacing: 8px;
        }}
        
        QRadioButton.form-radio::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {colors['border']};
            border-radius: 9px;
            background-color: {colors['surface']};
        }}
        
        QRadioButton.form-radio::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        /* Grupo de formulario */
        QGroupBox.form-group {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
            font-weight: bold;
        }}
        
        QGroupBox.form-group::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px;
            background-color: {colors['surface']};
            color: {colors['primary']};
            font-size: 15px;
            font-weight: 600;
        }}
        
        /* Mensajes de validación */
        QLabel.form-error {{
            color: {colors['danger']};
            font-size: 12px;
            margin-top: 4px;
            padding-left: 4px;
        }}
        
        QLabel.form-warning {{
            color: {colors['warning']};
            font-size: 12px;
            margin-top: 4px;
            padding-left: 4px;
        }}
        
        QLabel.form-help {{
            color: {colors['text_muted']};
            font-size: 12px;
            margin-top: 4px;
            font-style: italic;
        }}
        
        /* Botones de formulario */
        QPushButton.form-submit {{
            background-color: {colors['primary']};
            color: {colors['text_inverse']};
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 14px;
            min-height: 40px;
            min-width: 120px;
        }}
        
        QPushButton.form-submit:hover {{
            background-color: {colors['primary_dark']};
        }}
        
        QPushButton.form-reset {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 500;
            font-size: 14px;
            min-height: 40px;
        }}
        
        QPushButton.form-reset:hover {{
            background-color: {colors['hover']};
        }}
        
        /* Formulario inline (horizontal) */
        QWidget.form-inline QLabel {{
            margin-right: 8px;
            margin-bottom: 0;
        }}
        
        QWidget.form-inline QLineEdit,
        QWidget.form-inline QComboBox,
        QWidget.form-inline QSpinBox {{
            margin-right: 16px;
            margin-bottom: 0;
        }}
        
        /* Campo con icono */
        QLineEdit.with-icon {{
            padding-left: 36px;
        }}
        
        QLabel.input-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: {colors['text_muted']};
            font-size: 16px;
        }}
        """