"""Core game rules for a 6x6 Gekitai-like game."""

from __future__ import annotations


class GameLogic:
    BOARD_SIZE = 6
    INITIAL_RESERVE = 8
    DIRECTIONS = (
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    )

    def __init__(self) -> None:
        self.players = ("player1", "player2")
        self.board = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.current_player = "player1"
        self.reserves = {"player1": self.INITIAL_RESERVE, "player2": self.INITIAL_RESERVE}
        self.winner = None

    def is_valid_move(self, row: int, col: int) -> bool:
        if self.winner is not None:
            return False
        if not (0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE):
            return False
        if self.board[row][col] is not None:
            return False
        if self.reserves[self.current_player] <= 0:
            return False
        return True

    def make_move(self, row: int, col: int):
        if not self.is_valid_move(row, col):
            raise ValueError("Invalid move.")

        acting_player = self.current_player
        self.board[row][col] = acting_player
        self.reserves[acting_player] -= 1

        pushed, removed = self.push_neighbors(row, col)

        self.winner = self.check_winner(acting_player)
        if self.winner is None:
            self.switch_player()

        return {
            "board": [line[:] for line in self.board],
            "pushed": pushed,
            "removed": removed,
            "current_player": self.current_player,
            "reserves": dict(self.reserves),
            "winner": self.winner,
        }

    def push_neighbors(self, row: int, col: int):
        pushed = []
        removed = []

        planned_moves = []
        for dr, dc in self.DIRECTIONS:
            from_row = row + dr
            from_col = col + dc
            if not (0 <= from_row < self.BOARD_SIZE and 0 <= from_col < self.BOARD_SIZE):
                continue

            piece_owner = self.board[from_row][from_col]
            if piece_owner is None:
                continue

            to_row = from_row + dr
            to_col = from_col + dc
            planned_moves.append((from_row, from_col, to_row, to_col, piece_owner))

        for from_row, from_col, to_row, to_col, piece_owner in planned_moves:
            if self.board[from_row][from_col] != piece_owner:
                continue

            if not (0 <= to_row < self.BOARD_SIZE and 0 <= to_col < self.BOARD_SIZE):
                self.board[from_row][from_col] = None
                self.reserves[piece_owner] += 1
                removed.append((from_row, from_col))
                continue

            if self.board[to_row][to_col] is not None:
                continue

            self.board[from_row][from_col] = None
            self.board[to_row][to_col] = piece_owner
            pushed.append(((from_row, from_col), (to_row, to_col)))

        return pushed, removed

    def switch_player(self) -> None:
        self.current_player = "player2" if self.current_player == "player1" else "player1"

    def check_winner(self, player: str):
        if self._has_three_in_line(player):
            return player

        opponent = "player2" if player == "player1" else "player1"
        if self.reserves[opponent] == 0:
            return player

        return None

    def _has_three_in_line(self, player: str) -> bool:
        vectors = ((1, 0), (0, 1), (1, 1), (1, -1))
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                if self.board[row][col] != player:
                    continue
                for dr, dc in vectors:
                    if self._line_of_three(row, col, dr, dc, player):
                        return True
        return False

    def _line_of_three(self, row: int, col: int, dr: int, dc: int, player: str) -> bool:
        for step in (1, 2):
            nr = row + dr * step
            nc = col + dc * step
            if not (0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE):
                return False
            if self.board[nr][nc] != player:
                return False
        return True
