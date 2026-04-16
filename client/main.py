import sys
from PyQt6.QtWidgets import QApplication
# Import từ các file mày đã tách ra
from login import LoginWindow
from shell import AppShell

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. Khởi tạo màn hình Login
    login_screen = LoginWindow()
    main_dashboard = None # Biến này giữ cho App không bị tắt đột ngột

    def handle_login_success(ip, port, user): # Nhận thêm user ở đây
        global main_dashboard
        main_dashboard = AppShell(ip, port, user) # Truyền vào AppShell
        main_dashboard.show()
        login_screen.close()

    # Kết nối tín hiệu từ LoginWindow sang hàm xử lý chuyển màn hình
    # Tín hiệu này được phát ra khi mày bấm nút 'Connect'
    login_screen.connection_submitted.connect(handle_login_success)
    
    # Hiện màn hình login đầu tiên khi chạy app
    login_screen.show()
    
    sys.exit(app.exec())