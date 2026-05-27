"""Entry point for multiplayer Gekitai-like game."""

from __future__ import annotations

import threading
import time
import tkinter as tk
from tkinter import messagebox

from game_logic import GameLogic
from network import (
    close_connection,
    connect_to_server,
    receive_move,
    send_move,
    start_server,
)
from ui import GameUI


class MultiplayerGame:
    def __init__(self, mode: str):
        self.mode = mode
        self.player_id = "player1" if mode == "s" else "player2"
        self.logic = GameLogic()
        self.lock = threading.Lock()
        self.running = True

        self.root = tk.Tk()
        self.root.title(f"Gekitai Multiplayer - You are {self.player_id}")
        self.ui = GameUI(self.root, self.handle_local_move)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh_ui()

        listener = threading.Thread(target=self.listen_network, daemon=True)
        listener.start()

    def get_state(self):
        return {
            "board": [line[:] for line in self.logic.board],
            "reserves": dict(self.logic.reserves),
            "current_player": self.logic.current_player,
            "winner": self.logic.winner,
        }

    def refresh_ui(self) -> None:
        state = self.get_state()
        self.ui.render(state)
        if state["winner"] is not None:
            self.root.title(f"Vencedor: {state['winner']}")
        else:
            self.root.title(
                f"Gekitai Multiplayer - You are {self.player_id} | Turn: {state['current_player']}"
            )

    def handle_local_move(self, row: int, col: int) -> None:
        with self.lock:
            if self.logic.winner is not None:
                return
            if self.logic.current_player != self.player_id:
                return
            if not self.logic.is_valid_move(row, col):
                return

            self.logic.make_move(row, col)
            send_move({"action": "move", "row": row, "col": col})
            winner = self.logic.winner

        self.refresh_ui()
        if winner is not None:
            messagebox.showinfo("Fim de jogo", f"Vencedor: {winner}")

    def listen_network(self) -> None:
        while self.running:
            try:
                data = receive_move()
                if data is None:
                    break
            except OSError:
                break
            except ConnectionError:
                break

            if data.get("action") != "move":
                continue

            row = data.get("row")
            col = data.get("col")
            if not isinstance(row, int) or not isinstance(col, int):
                continue

            with self.lock:
                if self.logic.winner is not None:
                    continue
                if not self.logic.is_valid_move(row, col):
                    continue
                self.logic.make_move(row, col)
                winner = self.logic.winner

            self.root.after(0, self.refresh_ui)
            if winner is not None:
                self.root.after(
                    0,
                    lambda w=winner: messagebox.showinfo("Fim de jogo", f"Vencedor: {w}"),
                )

    def on_close(self) -> None:
        self.running = False
        close_connection()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def wait_for_connection(mode: str, host: str, port: int) -> None:
    if mode == "s":
        print(f"Servidor aguardando em {host}:{port}...")
        addr = start_server(host, port)
        print(f"Cliente conectado: {addr}")
    else:
        while True:
            try:
                connect_to_server(host, port)
                print("Conectado ao servidor.")
                break
            except OSError:
                print("Servidor indisponivel. Tentando novamente em 1s...")
                time.sleep(1)


def main() -> None:
    mode = input("Escolha o modo ('s' servidor / 'c' cliente): ").strip().lower()
    while mode not in {"s", "c"}:
        mode = input("Modo invalido. Use 's' ou 'c': ").strip().lower()

    default_host = "0.0.0.0" if mode == "s" else "127.0.0.1"
    host_input = input(f"Host [{default_host}]: ").strip()
    host = host_input if host_input else default_host

    port_input = input("Porta [5000]: ").strip()
    port = int(port_input) if port_input else 5000

    wait_for_connection(mode, host, port)

    game = MultiplayerGame(mode=mode)
    game.run()


if __name__ == "__main__":
    main()
