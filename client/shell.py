from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from monitor import MonitorWidget
from terminal import TerminalWidget
from explorer import FileExplorerWidget

class AppShell(QMainWindow):
    def __init__(self, ip, port, user):
        super().__init__()
        self.setWindowTitle("TeleNode Dashboard")
        self.resize(1250, 750)
        self.setStyleSheet("QMainWindow { background-color: #f3f3f3; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.nav_buttons = []

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(70)
        self.sidebar.setStyleSheet("background-color: #eeeeee; border-right: 1px solid #ddd;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(5, 20, 5, 20)
        self.sidebar_layout.setSpacing(15)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: white;")

        self.monitor_tab = MonitorWidget(ip, port)
        self.terminal_tab = TerminalWidget(ip, port, user)

        self.content_stack.addWidget(self.monitor_tab)
        self.content_stack.addWidget(self.terminal_tab)
        self.explorer_tab = FileExplorerWidget(ip, port)
        self.content_stack.addWidget(self.explorer_tab)
        
        self.add_nav_button("📊", 0, "TeleNode Performance")
        self.add_nav_button("💻", 1, "Terminal Console")
        self.add_nav_button("📁", 2, "File Management")
        self.sidebar_layout.addStretch()

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_stack)
        
        self.update_sidebar_style(0)

    def add_nav_button(self, icon, index, hint):
        btn = QPushButton(icon)
        btn.setFixedSize(70, 50) 
        btn.setFont(QFont("Segoe UI Emoji", 15))
        btn.setToolTip(hint)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn.setProperty("tab_index", index)
        
        btn.clicked.connect(lambda: self.change_tab(index))
        
        self.sidebar_layout.addWidget(btn)
        self.nav_buttons.append(btn)

    def change_tab(self, index):
        self.content_stack.setCurrentIndex(index)
        self.update_sidebar_style(index)

    def update_sidebar_style(self, active_index):
        active_style = """
            QPushButton {
                background-color: #ffffff; color: #0063b1;
                border-left: 4px solid #0063b1; border-radius: 0px;
            }
        """
        normal_style = """
            QPushButton {
                background-color: transparent; color: #555;
                border-left: 4px solid transparent; border-radius: 0px;
            }
            QPushButton:hover { background-color: #e2e2e2; }
        """

        for btn in self.nav_buttons:
            if btn.property("tab_index") == active_index:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet(normal_style)