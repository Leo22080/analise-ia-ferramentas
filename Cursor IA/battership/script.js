// ================================
// CONFIGURAÇÕES DO JOGO
// ================================

const BOARD_SIZE = 10;
const SHIP_SIZES = [5, 4, 3];

// ================================
// CLASSE SHIP (NAVIO)
// ================================

class Ship {
    constructor(size) {
        this.size = size;
        this.positions = [];
        this.hits = 0;
    }

    hit() {
        this.hits++;
    }

    isSunk() {
        return this.hits >= this.size;
    }
}

// ================================
// CLASSE BOARD (TABULEIRO)
// ================================

class Board {
    constructor(size) {
        this.size = size;
        this.grid = Array.from({ length: size }, () =>
            Array.from({ length: size }, () => null)
        );
        this.ships = [];
        this.attacks = Array.from({ length: size }, () =>
            Array.from({ length: size }, () => null)
        );
    }

    placeShips() {
        for (const shipSize of SHIP_SIZES) {
            const ship = new Ship(shipSize);
            let placed = false;
            let attempts = 0;

            while (!placed && attempts < 100) {
                placed = this.placeShip(ship);
                attempts++;
            }

            if (!placed) {
                throw new Error("Não foi possível posicionar todos os navios.");
            }
        }
    }

    placeShip(ship) {
        const horizontal = Math.random() < 0.5;
        const maxRow = horizontal ? this.size : this.size - ship.size;
        const maxCol = horizontal ? this.size - ship.size : this.size;

        const x = Math.floor(Math.random() * maxCol);
        const y = Math.floor(Math.random() * maxRow);

        const positions = [];
        for (let i = 0; i < ship.size; i++) {
            positions.push({
                x: horizontal ? x + i : x,
                y: horizontal ? y : y + i,
            });
        }

        if (!this.isValidPlacement(positions)) {
            return false;
        }

        for (const pos of positions) {
            this.grid[pos.y][pos.x] = ship;
        }

        ship.positions = positions;
        this.ships.push(ship);
        return true;
    }

    isValidPlacement(positions) {
        for (const { x, y } of positions) {
            if (x < 0 || y < 0 || x >= this.size || y >= this.size) {
                return false;
            }
            if (this.grid[y][x] !== null) {
                return false;
            }
        }
        return true;
    }

    receiveAttack(x, y) {
        if (this.attacks[y][x] !== null) {
            return "already";
        }

        const cell = this.grid[y][x];

        if (cell) {
            cell.hit();
            this.attacks[y][x] = "hit";
            // Retorna "sunk" quando o último tiro afunda o navio (útil para a IA resetar a caça)
            return cell.isSunk() ? "sunk" : "hit";
        }

        this.attacks[y][x] = "miss";
        return "miss";
    }

    allShipsSunk() {
        return this.ships.length > 0 && this.ships.every((ship) => ship.isSunk());
    }
}

// ================================
// IA DO INIMIGO (caça inteligente)
// ================================
// Modo aleatório: tiros em células ainda não atacadas.
// Após acerto: persegue adjacentes; com 2+ acertos na mesma linha,
// continua na direção e testa o sentido oposto (navio atingido no meio).

class EnemyAI {
    constructor() {
        this.attacked = new Set();
        this.huntHits = []; // acertos do navio atualmente em perseguição
    }

    _key(x, y) {
        return `${x},${y}`;
    }

    _inBounds(x, y) {
        return x >= 0 && y >= 0 && x < BOARD_SIZE && y < BOARD_SIZE;
    }

    _isAvailable(x, y) {
        return this._inBounds(x, y) && !this.attacked.has(this._key(x, y));
    }

    /** Escolhe célula aleatória entre as ainda não atacadas */
    _randomTarget() {
        const available = [];
        for (let y = 0; y < BOARD_SIZE; y++) {
            for (let x = 0; x < BOARD_SIZE; x++) {
                if (this._isAvailable(x, y)) available.push({ x, y });
            }
        }
        if (available.length === 0) return null;
        return available[Math.floor(Math.random() * available.length)];
    }

    /** Após o primeiro acerto, tenta uma das quatro células adjacentes */
    _adjacentTarget() {
        const { x, y } = this.huntHits[0];
        const dirs = [
            [0, -1],
            [0, 1],
            [-1, 0],
            [1, 0],
        ];
        const candidates = dirs
            .map(([dx, dy]) => ({ x: x + dx, y: y + dy }))
            .filter((p) => this._isAvailable(p.x, p.y));

        if (candidates.length === 0) return this._randomTarget();
        return candidates[Math.floor(Math.random() * candidates.length)];
    }

    /** Com 2+ acertos alinhados, estende a linha e testa o lado oposto */
    _lineTarget() {
        const dir = this._getDirection();
        if (!dir) return this._adjacentTarget();

        const axis = dir.dx !== 0 ? "x" : "y";
        const sorted = [...this.huntHits].sort((a, b) => a[axis] - b[axis]);
        const first = sorted[0];
        const last = sorted[sorted.length - 1];

        const forward = { x: last.x + dir.dx, y: last.y + dir.dy };
        if (this._isAvailable(forward.x, forward.y)) return forward;

        const backward = { x: first.x - dir.dx, y: first.y - dir.dy };
        if (this._isAvailable(backward.x, backward.y)) return backward;

        return this._adjacentTarget();
    }

    _getDirection() {
        if (this.huntHits.length < 2) return null;

        for (let i = 0; i < this.huntHits.length; i++) {
            for (let j = i + 1; j < this.huntHits.length; j++) {
                const dx = this.huntHits[j].x - this.huntHits[i].x;
                const dy = this.huntHits[j].y - this.huntHits[i].y;
                if (dx === 0 && Math.abs(dy) === 1) return { dx: 0, dy: Math.sign(dy) };
                if (dy === 0 && Math.abs(dx) === 1) return { dx: Math.sign(dx), dy: 0 };
            }
        }
        return null;
    }

    pickTarget() {
        if (this.huntHits.length === 0) return this._randomTarget();
        if (this.huntHits.length === 1) return this._adjacentTarget();
        return this._lineTarget();
    }

    /** Atualiza memória da IA após cada tiro do inimigo */
    registerResult(x, y, result) {
        this.attacked.add(this._key(x, y));

        if (result === "sunk") {
            this.huntHits = [];
            return;
        }

        if (result === "hit") {
            this.huntHits.push({ x, y });
        }
    }
}

// ================================
// CLASSE GAME (JOGO)
// ================================

class Game {
    constructor() {
        this.playerBoard = new Board(BOARD_SIZE);
        this.enemyBoard = new Board(BOARD_SIZE);
        this.playerBoard.placeShips();
        this.enemyBoard.placeShips();
        this.currentTurn = "player";
        this.gameOver = false;
        this.enemyAI = new EnemyAI();
    }

    init() {
        createBoardUI("player-board");
        createBoardUI("enemy-board");
        this.renderPlayerBoard();
        addBoardEvents(this);
        setStatus("Seu turno! Clique no tabuleiro inimigo para atacar.");
    }

    renderPlayerBoard() {
        const container = document.getElementById("player-board");
        const cells = container.querySelectorAll(".cell");

        cells.forEach((cell) => {
            const x = Number(cell.dataset.x);
            const y = Number(cell.dataset.y);
            const hasShip = this.playerBoard.grid[y][x] !== null;
            const attack = this.playerBoard.attacks[y][x];

            cell.className = "cell";
            if (hasShip) cell.classList.add("ship");
            if (attack === "hit") cell.classList.add("hit");
            if (attack === "miss") cell.classList.add("miss");
        });
    }

    /** Tiro extra: turno só muda quando o resultado for "miss" (água) */
    _isExtraShot(result) {
        return result === "hit" || result === "sunk";
    }

    playerAttack(x, y) {
        if (this.gameOver || this.currentTurn !== "player") return;

        const result = this.enemyBoard.receiveAttack(x, y);
        if (result === "already") return;

        const cell = document
            .getElementById("enemy-board")
            .querySelector(`[data-x="${x}"][data-y="${y}"]`);
        updateCell(cell, result);

        if (this.checkWinner()) return;

        if (this._isExtraShot(result)) {
            const msg =
                result === "sunk"
                    ? "Afundou um navio! Jogue novamente."
                    : "Acertou! Jogue novamente.";
            setStatus(msg);
            this.currentTurn = "player";
            return;
        }

        setStatus("Errou! Turno do inimigo...");
        this.currentTurn = "enemy";
        setTimeout(() => this.enemyAttack(), 600);
    }

    enemyAttack() {
        if (this.gameOver || this.currentTurn !== "enemy") return;

        const target = this.enemyAI.pickTarget();
        if (!target) return;

        const { x, y } = target;
        const result = this.playerBoard.receiveAttack(x, y);
        this.enemyAI.registerResult(x, y, result);
        this.renderPlayerBoard();

        if (this.checkWinner()) return;

        if (this._isExtraShot(result)) {
            const msg =
                result === "sunk"
                    ? "O inimigo afundou um navio! Ataca de novo..."
                    : "O inimigo acertou! Ataca de novo...";
            setStatus(msg);
            setTimeout(() => this.enemyAttack(), 600);
            return;
        }

        setStatus("O inimigo errou. Seu turno!");
        this.currentTurn = "player";
    }

    checkWinner() {
        if (this.enemyBoard.allShipsSunk()) {
            this.gameOver = true;
            setStatus("Vitória! Você destruiu toda a frota inimiga!");
            return true;
        }

        if (this.playerBoard.allShipsSunk()) {
            this.gameOver = true;
            setStatus("Derrota! Todos os seus navios foram afundados.");
            return true;
        }

        return false;
    }
}

// ================================
// FUNÇÕES DE INTERFACE (UI)
// ================================

function createBoardUI(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    for (let y = 0; y < BOARD_SIZE; y++) {
        for (let x = 0; x < BOARD_SIZE; x++) {
            const cell = document.createElement("div");
            cell.classList.add("cell");
            cell.dataset.x = x;
            cell.dataset.y = y;
            container.appendChild(cell);
        }
    }
}

function updateCell(cellElement, result) {
    if (result === "hit" || result === "sunk") {
        cellElement.classList.add("hit");
    } else if (result === "miss") {
        cellElement.classList.add("miss");
    }
}

function setStatus(message) {
    document.getElementById("status").textContent = message;
}

// ================================
// EVENTOS
// ================================

function addBoardEvents(game) {
    const enemyBoard = document.getElementById("enemy-board");
    const cells = enemyBoard.querySelectorAll(".cell");

    cells.forEach((cell) => {
        cell.addEventListener("click", () => {
            const x = Number(cell.dataset.x);
            const y = Number(cell.dataset.y);
            game.playerAttack(x, y);
        });
    });
}

// ================================
// INICIALIZAÇÃO DO JOGO
// ================================

const game = new Game();
game.init();
