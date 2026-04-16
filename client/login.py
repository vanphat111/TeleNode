from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class LoginWindow(QWidget):
    connection_submitted = pyqtSignal(str, int, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TeleNode - Connect")
        self.setFixedSize(350, 400)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(15)
        
        title = QLabel("TELENODE") # Đổi cái chữ to nhất ở giữa
        title.setStyleSheet("color: #0063b1; font-weight: bold;")
        title.setStyleSheet("color: #0063b1;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Style chung cho ô nhập
        input_style = "padding: 10px; border: 1px solid #ccc; border-radius: 5px; color: #333;"

        self.user_input = QLineEdit("vanphat111") # Để mặc định tên mày luôn cho tiện
        self.user_input.setPlaceholderText("SSH Username")
        self.user_input.setStyleSheet(input_style)
        layout.addWidget(self.user_input)

        self.ip_input = QLineEdit("127.0.0.1")
        self.ip_input.setPlaceholderText("Agent IP")
        self.ip_input.setStyleSheet(input_style)
        layout.addWidget(self.ip_input)

        self.port_input = QLineEdit("8888")
        self.port_input.setPlaceholderText("Port")
        self.port_input.setStyleSheet(input_style)
        layout.addWidget(self.port_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #d83b01; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

        layout.addStretch()

        self.btn_connect = QPushButton("Connect to Agent")
        self.btn_connect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_connect.setStyleSheet("""
            QPushButton { background: #0063b1; color: white; padding: 12px; font-weight: bold; border-radius: 5px; }
            QPushButton:hover { background: #0078d7; }
        """)
        self.btn_connect.clicked.connect(self.submit)
        layout.addWidget(self.btn_connect)

    def submit(self):
        ip = self.ip_input.text().strip()
        port_raw = self.port_input.text().strip()

        # 1. Kiểm tra IP trống
        if not ip:
            self.error_label.setText("❌ Vui lòng nhập IP")
            return
        
        # 2. Kiểm tra Port trống
        if not port_raw:
            self.error_label.setText("❌ Vui lòng nhập port")
            return

        # 3. Kiểm tra Port có phải là số không
        try:
            port = int(port_raw)
            # Nếu mọi thứ OK thì xóa thông báo lỗi và gửi tín hiệu
            self.error_label.setText("") 
            self.connection_submitted.emit(ip, port, self.user_input.text().strip())
        except ValueError:
            self.error_label.setText("❌ Port phải là số")