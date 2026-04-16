import threading
import time
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
# ---------------------------------------

try:
    from core.system import SystemCore
    from services.tele_bot import start_tele_bot
    from services.socket_srv import start_socket_server
except ImportError as e:
    print(f"❌ Lỗi Import: {e}")
    print("Mày kiểm tra xem đã tạo file __init__.py trong folder core và services chưa!")
    sys.exit(1)

def load_config():
    config_path = os.path.join(BASE_DIR, 'config.json')
    if not os.path.exists(config_path):
        default_config = {
            "tele_token": "8673266135:AAE9CutFWT4wKe1ynsUMaNomFSYCFEdCl4w",
            "admin_id": "8147973193",
            "socket_host": "0.0.0.0",
            "socket_port": 8888
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"❌ Chưa có file config. Tao đã tạo mẫu tại {config_path}.")
        print("👉 Mày mở file đó ra điền Token Bot và Admin ID vào rồi chạy lại nhé!")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    try:
        sys_core = SystemCore()
        
        config = load_config()
        
        t_bot = threading.Thread(
            target=start_tele_bot, 
            args=(config['tele_token'], config['admin_id'], sys_core),
            daemon=True
        )

        t_socket = threading.Thread(
            target=start_socket_server, 
            args=(config['socket_host'], config['socket_port'], sys_core),
            daemon=True
        )

        t_bot.start()
        t_socket.start()

        print(f"✅ UniControl Agent Online (No-GUI Mode)")
        print(f"🖥  Hệ điều hành: {sys_core.os_type}")
        print(f"🌐 Socket đang nghe tại cổng: {config['socket_port']}")
        while True: 
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Đang dừng Agent...")
    except Exception as e:
        print(f"💥 Lỗi hệ thống: {e}")

if __name__ == "__main__":
    main()