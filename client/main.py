import sys
from PyQt6.QtWidgets import QApplication
from login import LoginWindow
from shell import AppShell

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    login_screen = LoginWindow()
    main_dashboard = None

    def handle_login_success(ip, port, user):
        global main_dashboard
        main_dashboard = AppShell(ip, port, user)
        main_dashboard.show()
        login_screen.close()

    login_screen.connection_submitted.connect(handle_login_success)

    login_screen.show()
    
    sys.exit(app.exec())