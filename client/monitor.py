import socket
import json
import time
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont

pg.setConfigOptions(antialias=True)

class MetricCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, title, metric_id, color):
        super().__init__()
        self.title, self.metric_id = title, metric_id
        self.accent_color = color
        self.is_active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(85)
        
        layout = QVBoxLayout(self)
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        self.value_label = QLabel("0%")
        self.value_label.setFont(QFont("Sans Serif", 15))
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.update_style()

    def mousePressEvent(self, event):
        self.clicked.emit(self.metric_id)

    def update_style(self):
        bg = "#e8f2ff" if self.is_active else "#f8f9fa"
        border = "#0063b1" if self.is_active else "#dee2e6"
        
        self.setStyleSheet(f"""
            MetricCard {{ 
                background-color: {bg}; 
                border: 2px solid {border}; 
                border-radius: 8px; 
            }} 
            QLabel {{ color: #212529; }} 
            QLabel#ValueLabel {{ color: {self.accent_color}; font-weight: bold; }}
        """)
        self.value_label.setObjectName("ValueLabel")

    def update_value(self, value_text):
        self.value_label.setText(value_text)

class MonitorWidget(QWidget):
    def __init__(self, ip, port):
        super().__init__()
        self.setWindowTitle("TeleNode Performance Monitor")
        self.agent_ip, self.agent_port = ip, port
        self.current_view = "CPU"
        self.history = {k: [0] * 60 for k in ["CPU", "RAM", "Disk", "Network"]}
        self.last_net_total = 0
        self.x_axis = list(range(60))
        
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_data)
        self.timer.start(1000)

    def init_ui(self):
        main_layout = QHBoxLayout(self) 
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        self.header = QLabel("TeleNode Resource Monitor")

        colors = {"CPU": "#0063b1", "RAM": "#881798", "Disk": "#7a7574", "Network": "#d13438"}

        sidebar = QVBoxLayout()
        self.cards = {
            "CPU": MetricCard("CPU", "CPU", colors["CPU"]),
            "RAM": MetricCard("Memory", "RAM", colors["RAM"]),
            "Disk": MetricCard("Disk", "Disk", colors["Disk"]),
            "Network": MetricCard("Ethernet", "Network", colors["Network"])
        }
        for card in self.cards.values():
            card.clicked.connect(self.switch_metric)
            sidebar.addWidget(card)
        sidebar.addStretch()
        self.cards["CPU"].is_active = True
        self.cards["CPU"].update_style()

        graph_area = QVBoxLayout()
        self.header = QLabel("CPU Utilization")
        self.header.setFont(QFont("Sans Serif", 18, QFont.Weight.Light))
        self.header.setStyleSheet("color: #1c1c1c; margin-bottom: 10px;")

        self.graph = pg.PlotWidget()
        self.graph.setBackground('w')
        self.graph.showGrid(x=True, y=True, alpha=0.1)
        self.graph.setYRange(0, 100, padding=0)
        self.graph.setXRange(0, 59, padding=0)
        self.graph.setMouseEnabled(x=False, y=False)
        self.graph.getPlotItem().hideButtons()
        
        self.plot_item = self.graph.plot(self.x_axis, self.history["CPU"], 
                                         pen=pg.mkPen(color=colors["CPU"], width=2.5))
        
        graph_area.addWidget(self.header)
        graph_area.addWidget(self.graph)

        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(graph_area, 4)

    def switch_metric(self, m_id):
        self.current_view = m_id
        for k, card in self.cards.items():
            card.is_active = (k == m_id)
            card.update_style()
        colors = {
            "CPU": "#0063b1",
            "RAM": "#881798",
            "Disk": "#7a7574",
            "Network": "#d13438"
        }
        self.plot_item.setPen(pg.mkPen(color=colors.get(m_id, "#0063b1"), width=2.5))
        self.header.setText(f"{m_id}")

    def fetch_data(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.7)
                s.connect((self.agent_ip, self.agent_port))
                s.sendall(json.dumps({"action": "get_metrics"}).encode())
                res = json.loads(s.recv(1024).decode())
                if res["status"] != "success": return
                d = res["data"]

            net_total = d["net_sent"] + d["net_recv"]
            net_speed = (net_total - self.last_net_total) / 1024 if self.last_net_total > 0 else 0
            self.last_net_total = net_total

            vals = {"CPU": d["cpu_percent"], "RAM": d["ram_percent"], "Disk": d["disk_percent"], "Network": min(100, (net_speed/1024)*100)}
            labels = {"CPU": f"{vals['CPU']}%", "RAM": f"{vals['RAM']}%", "Disk": f"{vals['Disk']}%", "Network": f"{int(net_speed)} KB/s"}

            for k in self.history:
                self.history[k].pop(0); self.history[k].append(vals[k])
                self.cards[k].update_value(labels[k])

            self.plot_item.setData(self.x_axis, self.history[self.current_view])
            self.header.setText(f"{self.current_view}")
            self.header.setStyleSheet("color: #1c1c1c;")
        except:
            self.header.setText("⚠️ Mất kết nối tới Agent...")
            self.header.setStyleSheet("color: #d83b01;")