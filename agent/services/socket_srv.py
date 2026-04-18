import socket
import json
import threading
import subprocess

def handle_client(client_socket, addr, sys_core):
    print(f"[+] Client kết nối: {addr}")
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data: break
            
            try:
                request = json.loads(data)
                action = request.get("action")

                if action == "get_metrics":
                    response = {"status": "success", "data": sys_core.get_dynamic_status()}
                elif action == "run_cmd":
                    cmd = request.get("command")
                    if cmd:
                        result = sys_core.execute_shell(cmd)
                        response = {"status": "success", "output": result}
                    else:
                        response = {"status": "error", "message": "Lệnh trống"}
                elif action == "list_dir":
                    path = request.get("path")
                    response = sys_core.list_directory(path)
                    client_socket.send((json.dumps(response) + "\n").encode('utf-8'))
                
                else:
                    response = {"status": "error", "message": "Lệnh không xác định"}
            except json.JSONDecodeError:
                response = {"status": "error", "message": "JSON sai định dạng"}

            client_socket.send((json.dumps(response) + "\n").encode('utf-8'))
    except Exception as e:
        print(f"[!] Lỗi client {addr}: {e}")
    finally:
        client_socket.close()

def start_socket_server(host, port, sys_core):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"[*] Socket Server lắng nghe tại {host}:{port}")
        while True:
            client_sock, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_sock, addr, sys_core), daemon=True).start()
    except Exception as e:
        print(f"[!] Lỗi Socket Server: {e}")
    finally:
        server.close()