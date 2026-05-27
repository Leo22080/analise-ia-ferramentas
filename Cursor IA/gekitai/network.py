"""TCP networking helpers for multiplayer moves."""

from __future__ import annotations

import json
import socket
from typing import Optional


class NetworkManager:
    def __init__(self) -> None:
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self._recv_buffer = ""

    def start_server(self, host: str = "0.0.0.0", port: int = 5000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        conn, addr = self.server_socket.accept()
        self.client_socket = conn
        return addr

    def connect_to_server(self, host: str = "127.0.0.1", port: int = 5000) -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self.client_socket = sock
        return True

    def send_move(self, data: dict) -> None:
        if self.client_socket is None:
            raise ConnectionError("Socket is not connected.")
        payload = json.dumps(data) + "\n"
        self.client_socket.sendall(payload.encode("utf-8"))

    def receive_move(self):
        if self.client_socket is None:
            raise ConnectionError("Socket is not connected.")

        while "\n" not in self._recv_buffer:
            chunk = self.client_socket.recv(4096)
            if not chunk:
                return None
            self._recv_buffer += chunk.decode("utf-8")

        message, self._recv_buffer = self._recv_buffer.split("\n", 1)
        if not message.strip():
            return None
        return json.loads(message)

    def close(self) -> None:
        if self.client_socket is not None:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.client_socket.close()
            self.client_socket = None

        if self.server_socket is not None:
            self.server_socket.close()
            self.server_socket = None


_network = NetworkManager()


def start_server(host: str = "0.0.0.0", port: int = 5000):
    return _network.start_server(host=host, port=port)


def connect_to_server(host: str = "127.0.0.1", port: int = 5000) -> bool:
    return _network.connect_to_server(host=host, port=port)


def send_move(data: dict) -> None:
    _network.send_move(data)


def receive_move():
    return _network.receive_move()


def close_connection() -> None:
    _network.close()
