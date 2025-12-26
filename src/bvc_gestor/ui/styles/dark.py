# src/bvc_gestor/ui/styles/dark.py
"""
Estilo oscuro para la aplicación
"""
DARK_STYLESHEET = """
/* Estilos principales */
QMainWindow {
    background-color: #1a1d21;
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
    background-color: #495057;
    color: #6c757d;
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
    color: #e9ecef;
    font-size: 14px;
}

QLabel.title {
    font-size: 18px;
    font-weight: bold;
    color: #4dabf7;
}

QLabel.subtitle {
    font-size: 16px;
    font-weight: 600;
    color: #adb5bd;
}

/* LineEdits y TextEdits */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #2d333b;
    border: 1px solid #444c56;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 14px;
    color: #e9ecef;
    selection-background-color: #2c5aa0;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #4dabf7;
    padding: 5px 11px;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #343a40;
    color: #6c757d;
}

/* ComboBox */
QComboBox {
    background-color: #2d333b;
    border: 1px solid #444c56;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 14px;
    color: #e9ecef;
    min-height: 30px;
}

QComboBox:hover {
    border: 1px solid #5a6268;
}

QComboBox:focus {
    border: 2px solid #4dabf7;
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
    border-top: 5px solid #adb5bd;
    margin-right: 10px;
}

/* Tablas */
QTableView, QTableWidget {
    background-color: #2d333b;
    border: 1px solid #444c56;
    border-radius: 4px;
    gridline-color: #444c56;
    font-size: 14px;
    color: #e9ecef;
}

QTableView::item, QTableWidget::item {
    padding: 8px;
    color: #e9ecef;
}

QTableView::item:selected, QTableWidget::item:selected {
    background-color: #2c5aa0;
    color: white;
}

QHeaderView::section {
    background-color: #343a40;
    padding: 8px;
    border: none;
    border-right: 1px solid #444c56;
    border-bottom: 1px solid #444c56;
    font-weight: bold;
    color: #adb5bd;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #343a40;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #495057;
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
    background-color: #343a40;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #495057;
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
    border: 1px solid #444c56;
    border-radius: 6px;
    background-color: #2d333b;
    padding: 10px;
    color: #e9ecef;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #4dabf7;
    font-weight: bold;
}

/* ProgressBar */
QProgressBar {
    border: 1px solid #444c56;
    border-radius: 4px;
    background-color: #2d333b;
    text-align: center;
    color: #adb5bd;
}

QProgressBar::chunk {
    background-color: #2c5aa0;
    border-radius: 3px;
}

/* CheckBox y RadioButton */
QCheckBox, QRadioButton {
    color: #e9ecef;
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
    border: 1px solid #444c56;
    border-radius: 4px;
    background-color: #2d333b;
}

QTabBar::tab {
    background-color: #343a40;
    padding: 8px 16px;
    margin-right: 2px;
    border: 1px solid #444c56;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    color: #adb5bd;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: #2d333b;
    color: #4dabf7;
    font-weight: bold;
}

QTabBar::tab:selected {
    border-bottom: 2px solid #4dabf7;
}

/* ToolTip */
QToolTip {
    background-color: #212529;
    color: #e9ecef;
    border: 1px solid #495057;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

/* Mensajes */
QMessageBox {
    background-color: #2d333b;
}

QMessageBox QLabel {
    color: #e9ecef;
    font-size: 14px;
}
"""