"""Tkinter UI for the multiplayer Gekitai-like game."""

from __future__ import annotations

import tkinter as tk


class GameUI:
    BOARD_SIZE = 6

    def __init__(self, root: tk.Tk, on_move):
        self.root = root
        self.on_move = on_move

        self.cell_size = 80
        self.piece_padding = 8
        self.board_px = self.BOARD_SIZE * self.cell_size
        self.side_width = 140
        self.canvas_width = self.board_px + (self.side_width * 2)
        self.canvas_height = self.board_px

        self.board_left = (self.canvas_width - self.board_px) // 2
        self.board_top = (self.canvas_height - self.board_px) // 2

        self.colors = {
            "board": "#2f6f3f",
            "grid": "#204d2b",
            "player1": "#f2c14e",
            "player2": "#7fb3ff",
            "background": "#16231a",
        }

        self.board_state = {
            "board": [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)],
            "reserves": {"player1": 8, "player2": 8},
            "current_player": "player1",
            "winner": None,
        }

        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.colors["background"],
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_click)

        self.draw_board()
        self.draw_pieces(self.board_state["board"])
        self.draw_reserves()

    def _on_click(self, event) -> None:
        x, y = event.x, event.y
        if not (
            self.board_left <= x < self.board_left + self.board_px
            and self.board_top <= y < self.board_top + self.board_px
        ):
            return

        col = (x - self.board_left) // self.cell_size
        row = (y - self.board_top) // self.cell_size
        self.on_move(int(row), int(col))

    def draw_board(self) -> None:
        self.canvas.delete("board")
        self.canvas.create_rectangle(
            self.board_left,
            self.board_top,
            self.board_left + self.board_px,
            self.board_top + self.board_px,
            fill=self.colors["board"],
            outline=self.colors["grid"],
            width=2,
            tags="board",
        )

        for i in range(self.BOARD_SIZE + 1):
            x = self.board_left + (i * self.cell_size)
            y = self.board_top + (i * self.cell_size)
            self.canvas.create_line(
                x,
                self.board_top,
                x,
                self.board_top + self.board_px,
                fill=self.colors["grid"],
                width=2,
                tags="board",
            )
            self.canvas.create_line(
                self.board_left,
                y,
                self.board_left + self.board_px,
                y,
                fill=self.colors["grid"],
                width=2,
                tags="board",
            )

    def draw_pieces(self, board) -> None:
        self.canvas.delete("pieces")
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                owner = board[row][col]
                if owner is None:
                    continue
                x1 = self.board_left + col * self.cell_size + self.piece_padding
                y1 = self.board_top + row * self.cell_size + self.piece_padding
                x2 = self.board_left + (col + 1) * self.cell_size - self.piece_padding
                y2 = self.board_top + (row + 1) * self.cell_size - self.piece_padding
                self.canvas.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.colors[owner],
                    outline="",
                    tags="pieces",
                )

    def draw_reserves(self) -> None:
        self.canvas.delete("reserves")
        reserves = self.board_state["reserves"]

        diameter = self.cell_size - (self.piece_padding * 2)
        available_height = self.board_px - diameter
        step = available_height / 7

        left_center_x = self.board_left - (self.side_width // 2)
        right_center_x = self.board_left + self.board_px + (self.side_width // 2)
        first_center_y = self.board_top + diameter / 2

        self.canvas.create_text(
            left_center_x,
            self.board_top - 18,
            text="player1",
            fill=self.colors["player1"],
            font=("Arial", 12, "bold"),
            tags="reserves",
        )
        self.canvas.create_text(
            right_center_x,
            self.board_top - 18,
            text="player2",
            fill=self.colors["player2"],
            font=("Arial", 12, "bold"),
            tags="reserves",
        )

        for idx in range(8):
            center_y = first_center_y + (idx * step)
            for player, center_x in (("player1", left_center_x), ("player2", right_center_x)):
                if idx >= reserves[player]:
                    continue
                x1 = center_x - diameter / 2
                y1 = center_y - diameter / 2
                x2 = center_x + diameter / 2
                y2 = center_y + diameter / 2
                self.canvas.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.colors[player],
                    outline="",
                    tags="reserves",
                )

    def render(self, board_state: dict) -> None:
        self.board_state = board_state
        self.draw_board()
        self.draw_pieces(board_state["board"])
        self.draw_reserves()
