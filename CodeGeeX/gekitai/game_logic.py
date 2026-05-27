## game_logic.py
import copy

BOARD_SIZE = 6
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]

class GameLogic:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.reserves = {"player1": 8, "player2": 8}
        self.current_turn = "player1"
        self.winner = None

    def place_piece(self, row, col, player):
        if self.winner or self.current_turn != player:
            return False
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE) or self.board[row][col] is not None:
            return False
        if self.reserves[player] <= 0:
            return False

        # Coloca a peça
        self.board[row][col] = player
        self.reserves[player] -= 1

        # Empurra peças nas 8 direções (apenas 1 casa, sem efeito em cadeia)
        for dr, dc in DIRECTIONS:
            nr, nc = row + dr, col + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] is not None:
                pushed_player = self.board[nr][nc]
                tr, tc = nr + dr, nc + dc
                # Se a casa alvo estiver vazia, a peça é empurrada
                if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and self.board[tr][tc] is None:
                    self.board[tr][tc] = pushed_player
                    self.board[nr][nc] = None
                # Se a casa alvo estiver fora do tabuleiro, a peça cai no vazio (é removida)
                elif not (0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE):
                    # A peça volta para a reserva do dono!
                    self.reserves[pushed_player] += 1
                    self.board[nr][nc] = None

        # Verifica vitória
        self._check_winner()
        
        # Troca o turno se não houver vencedor
        if not self.winner:
            self.current_turn = "player2" if self.current_turn == "player1" else "player1"
        
        return True

    def _check_winner(self):
        # Condição 1: Alinhar 3 peças
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                player = self.board[r][c]
                if player:
                    # Checa horizontal, vertical e diagonais
                    if c + 2 < BOARD_SIZE and self.board[r][c+1] == player and self.board[r][c+2] == player:
                        self.winner = player; return
                    if r + 2 < BOARD_SIZE and self.board[r+1][c] == player and self.board[r+2][c] == player:
                        self.winner = player; return
                    if r + 2 < BOARD_SIZE and c + 2 < BOARD_SIZE and self.board[r+1][c+1] == player and self.board[r+2][c+2] == player:
                        self.winner = player; return
                    if r + 2 < BOARD_SIZE and c - 2 >= 0 and self.board[r+1][c-1] == player and self.board[r+2][c-2] == player:
                        self.winner = player; return

        # Condição 2: Oponente colocou todas as 8 peças no tabuleiro (reserva = 0)
        for p in ["player1", "player2"]:
            if self.reserves[p] == 0:
                count = sum(row.count(p) for row in self.board)
                if count == 8:
                    self.winner = p; return

    def get_state(self):
        return {
            "board": copy.deepcopy(self.board),
            "reserves": dict(self.reserves),
            "current_turn": self.current_turn,
            "winner": self.winner
        }

    def set_state(self, state):
        self.board = state["board"]
        self.reserves = state["reserves"]
        self.current_turn = state["current_turn"]
        self.winner = state["winner"]
