# main.py
import tkinter as tk
from game_logic import GameLogic
from network import Network
from ui import UI

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gekitai Multiplayer")
        self.root.configure(bg="#2C2C2C")
        
        self.game = GameLogic()
        self.network = Network()
        self.my_player = None
        
        self.frame_menu = tk.Frame(root, bg="#2C2C2C")
        self.frame_game = tk.Frame(root, bg="#2C2C2C")
        
        self._show_menu()

    def _show_menu(self):
        self.frame_menu.pack(pady=50)
        tk.Label(self.frame_menu, text="Gekitai", font=("Arial", 24), bg="#2C2C2C", fg="white").pack(pady=20)
        tk.Button(self.frame_menu, text="Criar Sala (Servidor)", font=("Arial", 14), command=self._setup_server).pack(pady=10)
        tk.Button(self.frame_menu, text="Entrar na Sala (Cliente)", font=("Arial", 14), command=self._setup_client).pack(pady=10)

    def _setup_server(self):
        self.my_player = "player1"
        self.frame_menu.destroy()
        self._init_game_ui()
        self.network.set_callback(self._on_network_message)
        self.network.start_server()
        self.ui.status_label.config(text="Aguardando jogador...")

    def _setup_client(self):
        self.my_player = "player2"
        self.frame_menu.destroy()
        self._init_game_ui()
        self.network.set_callback(self._on_network_message)
        self.network.connect_to_server()

    def _init_game_ui(self):
        self.frame_game.pack()
        self.ui = UI(self.frame_game, self._on_board_click)
        self.ui.draw(self.game.get_state())

    def _on_board_click(self, row, col):
        if self.game.current_turn == self.my_player and not self.game.winner:
            # Tenta realizar a jogada localmente para validação rápida
            if self.game.place_piece(row, col, self.my_player):
                self.ui.draw(self.game.get_state())
                # Envia a jogada para o outro jogador
                self.network.send_message({"action": "move", "row": row, "col": col, "player": self.my_player})

    def _on_network_message(self, msg):
        if msg["action"] == "move":
            player = msg["player"]
            row, col = msg["row"], msg["col"]
            self.game.place_piece(row, col, player)
            self.ui.draw(self.game.get_state())

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
