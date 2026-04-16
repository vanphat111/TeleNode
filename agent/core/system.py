import psutil
import platform
import time
import os
import subprocess
import pexpect
from datetime import datetime

class SystemCore:
    def __init__(self):
        self.os_type = platform.system()

    def get_basic_info(self):
        try:
            return {
                "hostname": platform.node(),
                "os": self.os_type,
                "cpu": f"{psutil.cpu_percent(interval=1)}%",
                "ram": f"{psutil.virtual_memory().percent}%",
                "disk": f"{psutil.disk_usage('/').percent}%",
                "boot": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            }
        except:
            return {"hostname": "N/A", "os": self.os_type, "cpu": "0%", "ram": "0%", "disk": "0%", "boot": "N/A"}

    def get_dynamic_status(self):
        """Dữ liệu cho App Client vẽ biểu đồ"""
        return {
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": psutil.virtual_memory().percent,
            "net_sent": psutil.net_io_counters().bytes_sent,
            "net_recv": psutil.net_io_counters().bytes_recv,
        }

    def execute_shell(self, command):
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=10)
            return output.decode('utf-8', errors='replace')
        except subprocess.CalledProcessError as e:
            return e.output.decode('utf-8', errors='replace')
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"

    def execute_interactive_shell(self, command, password):
        try:
            child = pexpect.spawn(f"sh -c '{command}'", timeout=15)
            index = child.expect(['[pP]assword', pexpect.EOF, pexpect.TIMEOUT])
            
            if index == 0:
                child.sendline(password)
                child.expect(pexpect.EOF)
                return child.before.decode('utf-8', errors='replace')
            elif index == 1:
                return child.before.decode('utf-8', errors='replace')
            else:
                return "❌ Lệnh bị treo hoặc Timeout."
        except Exception as e:
            return f"❌ Lỗi Pexpect: {str(e)}"

    def power_control(self, action):
        if self.os_type == "Windows":
            return "shutdown /s /t 1" if action == "shutdown" else "shutdown /r /t 1"
        return "shutdown -h now" if action == "shutdown" else "reboot"