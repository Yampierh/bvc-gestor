# src/bvc_gestor/ui/styles/light.py
"""
Estilo claro para la aplicación
"""
LIGHT_STYLESHEET = """
/* Estilos principales */
QMainWindow {
    background-color: #f8f9fa;
}

/* Botones generales */
QPushButton {
    background-color: #2c5aa0;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #1e4a8a;
}

QPushButton:pressed {
    background-color: #153c6e;
}

QPushButton:disabled {
    background-color: #6c757d;
    color: #adb5bd;
}

/* Botones secundarios */
QPushButton.secondary {
    background-color: #6c757d;
}

QPushButton.secondary:hover {
    background-color: #5a6268;
}

QPushButton.secondary:pressed {
    background-color: #545b62;
}

/* Labels */
QLabel {
    color: #212529;
    font-size: 14px;
}

QLabel.title {
    font-size: 18px;
    font-weight: bold;
    color: #2c5aa0;
}

QLabel.subtitle {
    font-size: 16px;
    font-weight: 600;
    color: #495057;
}

/* LineEdits y TextEdits */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: white;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 14px;
    selection-background-color: #2c5aa0;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #2c5aa0;
    padding: 5px 11px;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #e9ecef;
    color: #6c757d;
}

/* ComboBox */
QComboBox {
    background-color: white;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 14px;
    min-height: 30px;
}

QComboBox:hover {
    border: 1px solid #adb5bd;
}

QComboBox:focus {
    border: 2px solid #2c5aa0;
    padding: 5px 11px;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #495057;
    margin-right: 10px;
}

/* Tablas */
QTableView, QTableWidget {
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    gridline-color: #dee2e6;
    font-size: 14px;
}

QTableView::item, QTableWidget::item {
    padding: 8px;
}

QTableView::item:selected, QTableWidget::item:selected {
    background-color: #2c5aa0;
    color: white;
}

QHeaderView::section {
    background-color: #f8f9fa;
    padding: 8px;
    border: none;
    border-right: 1px solid #dee2e6;
    border-bottom: 1px solid #dee2e6;
    font-weight: bold;
    color: #495057;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #f8f9fa;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #adb5bd;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6c757d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f8f9fa;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #adb5bd;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6c757d;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Frames y GroupBox */
QFrame, QGroupBox {
    border: 1px solid #dee2e6;
    border-radius: 6px;
    background-color: white;
    padding: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #2c5aa0;
    font-weight: bold;
}

/* ProgressBar */
QProgressBar {
    border: 1px solid #ced4da;
    border-radius: 4px;
    background-color: white;
    text-align: center;
    color: #495057;
}

QProgressBar::chunk {
    background-color: #2c5aa0;
    border-radius: 3px;
}

/* CheckBox y RadioButton */
QCheckBox, QRadioButton {
    color: #212529;
    font-size: 14px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:checked {
    background-color: #2c5aa0;
    border: 2px solid #2c5aa0;
    border-radius: 3px;
}

QRadioButton::indicator:checked {
    background-color: #2c5aa0;
    border: 2px solid #2c5aa0;
    border-radius: 9px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    background-color: white;
}

QTabBar::tab {
    background-color: #f8f9fa;
    padding: 8px 16px;
    margin-right: 2px;
    border: 1px solid #dee2e6;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    color: #6c757d;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: white;
    color: #2c5aa0;
    font-weight: bold;
}

QTabBar::tab:selected {
    border-bottom: 2px solid #2c5aa0;
}

/* ToolTip */
QToolTip {
    background-color: #212529;
    color: white;
    border: 1px solid #495057;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

/* Mensajes */
QMessageBox {
    background-color: white;
}

QMessageBox QLabel {
    color: #212529;
    font-size: 14px;
}
"""