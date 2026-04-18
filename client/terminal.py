import socket, json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor

class TerminalWidget(QWidget):
    def __init__(self, ip, port, user):
        super().__init__()
        self.ip, self.port, self.user = ip, port, user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Monospace", 11))
        self.output_area.setStyleSheet("background-color: #0c0c0c; color: #00ff00; border: none; padding: 10px;")
        
        self.input_line = QLineEdit()
        self.input_line.setFont(QFont("Monospace", 11))
        self.input_line.setStyleSheet("background-color: #0c0c0c; color: #ffffff; border: none; border-top: 1px solid #333; padding: 10px;")
        
        self.prompt = f"{self.user}@remote:~$ "
        self.input_line.setPlaceholderText(self.prompt)
        self.input_line.returnPressed.connect(self.execute_command)

        layout.addWidget(self.output_area)
        layout.addWidget(self.input_line)
        self.output_area.append("--- TeleNode Remote Terminal Connected ---")
        self.output_area.append(f"Node: {self.ip}:{self.port}\n")

    def execute_command(self):
        cmd = self.input_line.text().strip()
        if not cmd: return

        self.output_area.append(f"<b style='color: white;'>{self.prompt}{cmd}</b>")
        self.input_line.clear()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((self.ip, self.port))
                s.sendall(json.dumps({"action": "run_cmd", "command": cmd}).encode())
                res = json.loads(s.recv(8192).decode())
                
                output = res.get("output", "No output.")
                self.output_area.append(output)
        except Exception as e:
            self.output_area.append(f"<span style='color: red;'>Lỗi: {str(e)}</span>")
        
        self.output_area.moveCursor(QTextCursor.MoveOperation.End)