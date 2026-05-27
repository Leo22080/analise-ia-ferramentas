# network.py
import socket
import threading
import json

class Network:
    def __init__(self):
        self.socket = None
        self.conn = None
        self.is_server = False
        self.callback = None
        self.running = False

    def start_server(self, host='127.0.0.1', port=65432):
        self.is_server = True
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(1)
        threading.Thread(target=self._accept_connections, daemon=True).start()

    def _accept_connections(self):
        try:
            self.conn, addr = self.socket.accept()
            threading.Thread(target=self._receive_loop, daemon=True).start()
        except Exception:
            pass

    def connect_to_server(self, host='127.0.0.1', port=65432):
        self.is_server = False
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.conn = self.socket
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def _receive_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.conn.recv(4096).decode('utf-8')
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if self.callback:
                        msg = json.loads(line)
                        self.callback(msg)
            except Exception:
                break
        self.running = False

    def send_message(self, msg_dict):
        if self.conn:
            try:
                self.conn.sendall((json.dumps(msg_dict) + "\n").encode('utf-8'))
            except Exception:
                pass

    def set_callback(self, callback):
        self.callback = callback

    def close(self):
        self.running = False
        if self.conn:
            try: self.conn.close()
            except: pass
        if self.socket:
            try: self.socket.close()
            except: pass
