# ui.py
import tkinter as tk
from game_logic import BOARD_SIZE

class UI:
    def __init__(self, master, on_click_callback):
        self.master = master
        self.on_click_callback = on_click_callback
        
        self.cell_size = 80
        self.padding = 10
        self.piece_size = self.cell_size - 2 * self.padding
        
        self.colors = {
            "board": "#D2B48C",
            "player1": "#FF4444",
            "player2": "#4444FF",
            "bg": "#2C2C2C"
        }
        
        self.canvas_width = self.cell_size * (BOARD_SIZE + 2)
        self.canvas_height = self.cell_size * BOARD_SIZE
        
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg=self.colors["bg"], highlightthickness=0)
        self.canvas.pack(pady=20)
        self.canvas.bind("<Button-1>", self._handle_click)
        
        self.status_label = tk.Label(master, text="", font=("Arial", 16), bg=self.colors["bg"], fg="white")
        self.status_label.pack()

    def _handle_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        # Ignora cliques nas laterais (colunas 0 e 7)
        if 1 <= col <= BOARD_SIZE and 0 <= row < BOARD_SIZE:
            board_col = col - 1
            self.on_click_callback(row, board_col)

    def draw(self, state):
        self.canvas.delete("all")
        self._draw_reserves(state["reserves"], "player1", 0)
        self._draw_reserves(state["reserves"], "player2", BOARD_SIZE + 1)
        self._draw_board(state["board"])
        self._draw_status(state)

    def _draw_board(self, board):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1 = (c + 1) * self.cell_size
                y1 = r * self.cell_size
                self.canvas.create_rectangle(x1, y1, x1 + self.cell_size, y1 + self.cell_size, fill=self.colors["board"], outline="black")
                
                if board[r][c]:
                    self._draw_piece_at(x1, y1, board[r][c])

    def _draw_reserves(self, reserves, player, col_index):
        count = reserves[player]
        if count == 0:
            return
            
        x1 = col_index * self.cell_size
        y_start = 0
        y_end = BOARD_SIZE * self.cell_size
        
        # Cálculo de sobreposição: distribui 'count' peças proporcionalmente no eixo Y
        available_height = y_end - y_start - self.piece_size
        step = available_height / (count - 1) if count > 1 else 0
        
        for i in range(count):
            y1 = y_start + i * step
            self._draw_piece_at(x1, y1, player)

    def _draw_piece_at(self, x1, y1, player):
        px1 = x1 + self.padding
        py1 = y1 + self.padding
        px2 = px1 + self.piece_size
        py2 = py1 + self.piece_size
        self.canvas.create_oval(px1, py1, px2, py2, fill=self.colors[player], outline="black", width=2)

    def _draw_status(self, state):
        turn = state["current_turn"]
        winner = state["winner"]
        if winner:
            text = f"{winner.replace('p', 'P').replace('_', ' ')} Venceu!"
        else:
            text = f"Turno: {turn.replace('p', 'P').replace('_', ' ')}"
        self.status_label.config(text=text)
