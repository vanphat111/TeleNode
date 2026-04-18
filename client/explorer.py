import socket, json, os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView, QLabel
from PyQt6.QtCore import Qt

class FileExplorerWidget(QWidget):
    def __init__(self, ip, port):
        super().__init__()
        self.ip, self.port = ip, port
        self.current_path = os.path.expanduser("~") 
        self.init_ui()
        self.load_path(self.current_path)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.path_label = QLabel(f" Path: {self.current_path}")
        self.path_label.setStyleSheet("""
            background-color: #e0e0e0; 
            color: #000000; 
            padding: 10px; 
            font-family: 'Monospace'; 
            font-weight: bold;
            border-bottom: 1px solid #ccc;
        """)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Size"])
        self.tree.setAlternatingRowColors(False) 
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #0c0c0c; 
                color: #ffffff; 
                border: none;
                font-family: 'Segoe UI', sans-serif;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #222;
            }
            QTreeWidget::item:selected {
                background-color: #333333;
                color: #00ff00;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #333;
            }
        """)
        
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.path_label)
        layout.addWidget(self.tree)

    def load_path(self, path):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((self.ip, self.port))
                s.sendall(json.dumps({"action": "list_dir", "path": path}).encode())
                
                buffer = ""
                while True:
                    chunk = s.recv(4096).decode('utf-8')
                    if not chunk: break
                    buffer += chunk
                    if buffer.endswith('\n'): break 

                first_json = buffer.strip().split('\n')[0]
                res = json.loads(first_json)
                
                if res.get("status") == "success":
                    self.tree.clear()
                    self.current_path = res["current_path"]
                    self.path_label.setText(f" Path: {self.current_path}")
                    
                    if self.current_path != "/" and self.current_path != "":
                        back_node = QTreeWidgetItem(["..", "Parent Directory", "-"])
                        self.tree.addTopLevelItem(back_node)

                    for item in res["data"]:
                        icon = "📁" if item["is_dir"] else "📄"
                        type_str = "Folder" if item["is_dir"] else "File"
                        size = item['size']
                        if item["is_dir"]:
                            size_str = "-"
                        elif size < 1024:
                            size_str = f"{size} B"
                        elif size < 1024**2:
                            size_str = f"{size/1024:.1f} KB"
                        else:
                            size_str = f"{size/1024**2:.1f} MB"
                        
                        node = QTreeWidgetItem([f"{icon} {item['name']}", type_str, size_str])
                        self.tree.addTopLevelItem(node)
                else:
                    print(f"Server Error: {res.get('message')}")
        except Exception as e:
            print(f"Explorer Connection Error: {e}")

    def on_item_double_clicked(self, item, column):
        name_with_icon = item.text(0)
        if name_with_icon == "..":
            new_path = os.path.dirname(self.current_path)
            self.load_path(new_path)
            return

        if item.text(1) == "Folder":
            pure_name = name_with_icon.split(" ", 1)[1]
            new_path = self.current_path.rstrip("/") + "/" + pure_name
            self.load_path(new_path)