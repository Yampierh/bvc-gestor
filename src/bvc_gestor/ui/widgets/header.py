from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon

class HeaderWidget(QWidget):
    def __init__(self, title="Main Dashboard"):
        super().__init__()
        self.setFixedHeight(70) # Altura fija para el header
        
        # Layout horizontal principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # 1. Título de la página dinámica
        self.title_label = QLabel(title)
        self.title_label.setObjectName("HeaderTitle")
        layout.addWidget(self.title_label)
        
        # 2. Espaciador (empuja lo que sigue a la derecha)
        layout.addStretch()
        
        # 3. Contenedor de Perfil / Notificaciones
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(15)
        
        # Botón de búsqueda o notificación (Opcional)
        self.btn_search = QPushButton()
        self.btn_search.setIcon(QIcon("src/bvc_gestor/assets/icons/search.svg")) # Si tienes el svg
        self.btn_search.setObjectName("IconButton")
        
        # Info del Usuario
        user_info = QVBoxLayout() # Para nombre y rol uno sobre otro
        user_info.setSpacing(0)
        
        user_name = QLabel("Yampier Hernandez")
        user_name.setObjectName("UserName")
        
        user_role = QLabel("Logo Designer")
        user_role.setObjectName("UserRole")
        
        # user_info.addWidget(user_name)
        # user_info.addWidget(user_role)
        
        # Avatar (Círculo de imagen)
        self.avatar = QLabel()
        self.avatar.setFixedSize(40, 40)
        self.avatar.setStyleSheet("""
            background-color: #333; 
            border-radius: 20px; 
            border: 1px solid #FF6B00;
        """)
        # Si tienes una imagen real: 
        # self.avatar.setPixmap(QPixmap("assets/user.jpg").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatioByExpanding))

        layout.addWidget(self.btn_search)
        layout.addWidget(user_name)
        layout.addWidget(self.avatar)

    def update_title(self, new_title):
        """Método para cambiar el título según la página"""
        self.title_label.setText(new_title)