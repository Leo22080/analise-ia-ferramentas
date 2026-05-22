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
        return this.hits === this.size;
    }
}

// ================================
// CLASSE BOARD (TABULEIRO)
// ================================

class Board {
    constructor(size) {
        this.size = size;
        this.grid = Array.from({ length: size }, () => Array(size).fill(null));
        this.ships = [];
        this.attackedPositions = new Set();
    }

    placeShips() {
        SHIP_SIZES.forEach(size => {
            let placed = false;
            while (!placed) {
                const ship = new Ship(size);
                placed = this.placeShip(ship);
            }
        });
    }

    placeShip(ship) {
        const isHorizontal = Math.random() > 0.5;
        let x = Math.floor(Math.random() * this.size);
        let y = Math.floor(Math.random() * this.size);

        const positions = [];
        for (let i = 0; i < ship.size; i++) {
            const currX = isHorizontal ? x : x + i;
            const currY = isHorizontal ? y + i : y;
            positions.push({ x: currX, y: currY });
        }

        if (!this.isValidPlacement(positions)) return false;

        positions.forEach(pos => {
            this.grid[pos.x][pos.y] = ship;
            ship.positions.push(pos);
        });
        this.ships.push(ship);
        return true;
    }

    isValidPlacement(positions) {
        for (const pos of positions) {
            if (pos.x >= this.size || pos.y >= this.size || pos.x < 0 || pos.y < 0) return false;
            if (this.grid[pos.x][pos.y] !== null) return false;
        }
        return true;
    }

    receiveAttack(x, y) {
        const key = `${x},${y}`;
        if (this.attackedPositions.has(key)) return "already_attacked";
        
        this.attackedPositions.add(key);
        const target = this.grid[x][y];
        
        if (target) {
            target.hit();
            return target.isSunk() ? "sunk" : "hit"; // Retorna "sunk" se afundou
        }
        return "miss";
    }

    allShipsSunk() {
        return this.ships.every(ship => ship.isSunk());
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
        this.isPlayerTurn = true;
        this.gameOver = false;

        // REFATORAÇÃO: Estado da IA Inimiga
        this.enemyMode = 'hunt'; // 'hunt' (aleatório) ou 'target' (caçando)
        this.enemyTargetQueue = []; // Fila de coordenadas a atirar
        this.enemyHitStack = []; // Histórico de acertos no navio atual
    }

    init() {
        // Como o HTML já está no arquivo index.html, apenas criamos o UI do tabuleiro
        createBoardUI("player-board", this.playerBoard, true);
        createBoardUI("enemy-board", this.enemyBoard, false);
        addBoardEvents(this);
        setStatus("Sua vez! Clique no tabuleiro inimigo para atacar.");
    }

    // REFATORAÇÃO: Tiros extras para o jogador
    playerAttack(x, y) {
        if (!this.isPlayerTurn || this.gameOver) return;

        const result = this.enemyBoard.receiveAttack(x, y);
        if (result === "already_attacked") return;

        const cell = document.querySelector(`#enemy-board [data-x="${x}"][data-y="${y}"]`);
        updateCell(cell, result === "sunk" ? "hit" : result);

        if (this.checkWinner()) return;

        // LÓGICA DE TURNO EXTRA: Se acertou, mantém o turno. Se errou, passa.
        if (result === "hit" || result === "sunk") {
            setStatus("💥 Acertou! Jogue novamente.");
        } else {
            this.isPlayerTurn = false;
            setStatus("Turno do inimigo...");
            setTimeout(() => this.enemyAttack(), 1000);
        }
    }

    // REFATORAÇÃO: IA Inteligente + Tiros extras para o inimigo
    enemyAttack() {
        if (this.gameOver) return;
        let x, y, result;
        
        // --- LÓGICA DA IA ---
        if (this.enemyMode === 'target' && this.enemyTargetQueue.length > 0) {
            // Modo Caça: Puxa a próxima coordenada da fila
            const target = this.enemyTargetQueue.shift();
            x = target.x;
            y = target.y;
            result = this.playerBoard.receiveAttack(x, y);
            
            if (result === "already_attacked") {
                if (this.enemyTargetQueue.length === 0) this.resetEnemyHunt();
                setTimeout(() => this.enemyAttack(), 0); 
                return;
            }
        } else {
            // Modo Aleatório: Escolher posição que ainda não foi atacada
            this.resetEnemyHunt();
            do {
                x = Math.floor(Math.random() * BOARD_SIZE);
                y = Math.floor(Math.random() * BOARD_SIZE);
                result = this.playerBoard.receiveAttack(x, y);
            } while (result === "already_attacked");
        }

        const cell = document.querySelector(`#player-board [data-x="${x}"][data-y="${y}"]`);
        updateCell(cell, result === "sunk" ? "hit" : result);

        if (this.checkWinner()) return;

        // --- PROCESSAMENTO DA IA E TURNO EXTRA ---
        if (result === "hit") {
            this.enemyMode = 'target';
            this.enemyHitStack.push({ x, y });
            this.processEnemyHit(x, y);
            setStatus("💥 Inimigo acertou! Ele joga novamente...");
            setTimeout(() => this.enemyAttack(), 1000);
            
        } else if (result === "sunk") {
            this.resetEnemyHunt();
            setStatus("💥 Inimigo afundou um navio! Ele joga novamente...");
            setTimeout(() => this.enemyAttack(), 1000);
            
        } else {
            this.isPlayerTurn = true;
            setStatus("Sua vez! Clique no tabuleiro inimigo para atacar.");
        }
    }

    // REFATORAÇÃO: Processa o acerto da IA para encontrar a direção do navio
    processEnemyHit(x, y) {
        const directions = [
            { dx: -1, dy: 0 }, // Cima
            { dx: 1, dy: 0 },  // Baixo
            { dx: 0, dy: -1 }, // Esquerda
            { dx: 0, dy: 1 }   // Direita
        ];

        if (this.enemyHitStack.length === 1) {
            // Primeiro acerto: adiciona as 4 posições adjacentes
            for (let d of directions) {
                this.enqueueTarget(x + d.dx, y + d.dy);
            }
        } else {
            // Acertos subsequentes: descobre a direção e continua nela
            const prevHit = this.enemyHitStack[this.enemyHitStack.length - 2];
            const dx = x - prevHit.x;
            const dy = y - prevHit.y;

            this.enqueueTarget(x + dx, y + dy); // Continua na mesma direção

            // Se for o 2º acerto, testa o sentido oposto a partir do primeiro acerto
            if (this.enemyHitStack.length === 2) {
                this.enqueueTarget(prevHit.x - dx, prevHit.y - dy);
            }
        }
    }

    // REFATORAÇÃO: Adiciona alvos válidos à fila da IA
    enqueueTarget(x, y) {
        const key = `${x},${y}`;
        if (x >= 0 && x < BOARD_SIZE && y >= 0 && y < BOARD_SIZE && !this.playerBoard.attackedPositions.has(key)) {
            if (!this.enemyTargetQueue.some(t => t.x === x && t.y === y)) {
                this.enemyTargetQueue.push({ x, y });
            }
        }
    }

    // REFATORAÇÃO: Reseta a IA para o modo aleatório
    resetEnemyHunt() {
        this.enemyMode = 'hunt';
        this.enemyTargetQueue = [];
        this.enemyHitStack = [];
    }

    checkWinner() {
        if (this.enemyBoard.allShipsSunk()) {
            setStatus("🎉 Você venceu! Todos os navios inimigos foram afundados!");
            this.gameOver = true;
            return true;
        }
        if (this.playerBoard.allShipsSunk()) {
            setStatus("💀 Você perdeu! Todos os seus navios foram afundados!");
            this.gameOver = true;
            return true;
        }
        return false;
    }
}

// ================================
// FUNÇÕES DE INTERFACE (UI)
// ================================

function createBoardUI(containerId, board, showShips) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    for (let x = 0; x < BOARD_SIZE; x++) {
        for (let y = 0; y < BOARD_SIZE; y++) {
            const cell = document.createElement("div");
            cell.classList.add("cell");
            cell.dataset.x = x;
            cell.dataset.y = y;
            
            if (showShips && board.grid[x][y] !== null) {
                cell.classList.add("ship");
            }
            
            container.appendChild(cell);
        }
    }
}

function updateCell(cellElement, result) {
    if (!cellElement) return;
    if (result === "hit") {
        cellElement.classList.add("hit");
        cellElement.textContent = "💥";
    } else if (result === "miss") {
        cellElement.classList.add("miss");
        cellElement.textContent = "💧";
    }
}

function setStatus(message) {
    const statusDiv = document.getElementById("status");
    if (statusDiv) statusDiv.innerText = message;
}

// ================================
// EVENTOS
// ================================

function addBoardEvents(game) {
    const enemyBoard = document.getElementById("enemy-board");
    enemyBoard.addEventListener("click", (e) => {
        const cell = e.target;
        if (!cell.classList.contains("cell")) return;
        
        const x = parseInt(cell.dataset.x);
        const y = parseInt(cell.dataset.y);
        game.playerAttack(x, y);
    });
}

// ================================
// INICIALIZAÇÃO DO JOGO
// ================================

const game = new Game();
game.init();
