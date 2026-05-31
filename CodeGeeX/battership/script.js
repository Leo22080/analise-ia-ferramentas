// ==========================================
// CONFIGURAÇÕES E CONSTANTES
// ==========================================
const BOARD_SIZE = 10;
const SHIPS = [
    { name: 'Porta-Aviões', size: 5 },
    { name: 'Encouraçado', size: 4 },
    { name: 'Cruzador', size: 3 },
    { name: 'Submarino', size: 3 },
    { name: 'Destroyer', size: 2 }
];

// Direções: [linha, coluna]
const DIRECTIONS = [
    [-1, 0], // Cima
    [1, 0],  // Baixo
    [0, -1], // Esquerda
    [0, 1]   // Direita
];

let playerBoard, enemyBoard;
let isPlayerTurn = true;
let gameOver = false;

// Estado da IA
let aiState = {
    mode: 'hunt', // 'hunt' (procurando) ou 'target' (caçando)
    hits: [],     // Acertos no navio atual
    direction: null, // Direção confirmada do navio
    triedDirections: [] // Direções já testadas a partir do primeiro acerto
};

// ==========================================
// INICIALIZAÇÃO DO TABULEIRO
// ==========================================
function startGame() {
    gameOver = false;
    isPlayerTurn = true;
    aiState = {
        mode: 'hunt',
        hits: [],
        direction: null,
        triedDirections: []
    };

    playerBoard = createEmptyGrid();
    enemyBoard = createEmptyGrid();
    
    SHIPS.forEach(ship => {
        placeShipRandomly(playerBoard, ship);
        placeShipRandomly(enemyBoard, ship);
    });

    renderBoard('player-board', playerBoard, true);
    renderBoard('enemy-board', enemyBoard, false);
    
    document.getElementById('status').innerText = "Sua vez! Clique no tabuleiro inimigo.";
    document.getElementById('start-btn').innerText = "Reiniciar Jogo";
}

// Cria uma grade 10x10 vazia
function createEmptyGrid() {
    return Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(0));
}

// Posiciona navios aleatoriamente sem sobreposição
// Posiciona navios aleatoriamente sem sobreposição
function placeShipRandomly(board, ship) {
    let placed = false;
    while (!placed) {
        // Escolhe aleatoriamente entre as 4 direções (Vertical e Horizontal)
        const dir = DIRECTIONS[Math.floor(Math.random() * DIRECTIONS.length)];
        const row = Math.floor(Math.random() * BOARD_SIZE);
        const col = Math.floor(Math.random() * BOARD_SIZE);
        
        if (canPlaceShip(board, row, col, dir, ship.size)) {
            for (let i = 0; i < ship.size; i++) {
                board[row + dir[0] * i][col + dir[1] * i] = ship.size;
            }
            placed = true;
        }
    }
}


// Verifica se é possível colocar o navio na posição dada
// Verifica se é possível colocar o navio na posição dada, garantindo 1 célula de distância de outros navios
function canPlaceShip(board, row, col, dir, size) {
    for (let i = 0; i < size; i++) {
        const r = row + dir[0] * i;
        const c = col + dir[1] * i;
        
        // 1. Verifica se está dentro do tabuleiro
        if (r < 0 || r >= BOARD_SIZE || c < 0 || c >= BOARD_SIZE) return false;
        
        // 2. Verifica se a própria célula já está ocupada
        if (board[r][c] !== 0) return false;

        // 3. Verifica as 8 células ao redor (incluindo diagonais) para garantir o espaçamento
        for (let dr = -1; dr <= 1; dr++) {
            for (let dc = -1; dc <= 1; dc++) {
                if (dr === 0 && dc === 0) continue; // Ignora a própria célula (já verificada acima)
                
                const nr = r + dr;
                const nc = c + dc;
                
                // Verifica se o vizinho está dentro do tabuleiro
                if (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE) {
                    // Se houver qualquer navio nas redondezas, o posicionamento é inválido
                    if (board[nr][nc] !== 0) return false;
                }
            }
        }
    }
    return true;
}


// Renderiza a grade no DOM
function renderBoard(boardId, board, showShips) {
    const boardEl = document.getElementById(boardId);
    boardEl.innerHTML = '';
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = r;
            cell.dataset.col = c;

            if (board[r][c] === 'X') {
                cell.classList.add('hit');
                cell.innerHTML = '💥'; // Emoji de explosão (acerto)
            }
            else if (board[r][c] === 'O') {
                cell.classList.add('miss');
                cell.innerHTML = '💧'; // Emoji de gota (erro)
            }
            else if (board[r][c] === 'S') {
                cell.classList.add('sunk');
                cell.innerHTML = '💥'; // Emoji de explosão (afundado)
            }
            else if (showShips && board[r][c] > 0) {
                cell.classList.add('ship');
            }

            // Apenas o tabuleiro inimigo é clicável
            if (boardId === 'enemy-board') {
                cell.addEventListener('click', handlePlayerMove);
            }
            boardEl.appendChild(cell);
        }
    }
}

// ==========================================
// LÓGICA DO JOGADOR
// ==========================================
function handlePlayerMove(event) {
    if (!isPlayerTurn || gameOver) return;

    const row = parseInt(event.target.dataset.row);
    const col = parseInt(event.target.dataset.col);
    
    // Ignora cliques em células já atacadas
    if (enemyBoard[row][col] === 'X' || enemyBoard[row][col] === 'O' || enemyBoard[row][col] === 'S') return;

    const hit = processAttack(enemyBoard, row, col);
    renderBoard('enemy-board', enemyBoard, false);

    if (hit) {
        document.getElementById('status').innerText = "Você acertou! Jogue novamente.";
        if (checkVictory(enemyBoard)) {
            endGame("Você venceu!");
        }
    } else {
        document.getElementById('status').innerText = "Você errou. Vez da IA.";
        isPlayerTurn = false;
        disableEnemyBoard(true);
        setTimeout(handleAIMove, 1000); // Dá um tempo para a IA "pensar"
    }
}

// ==========================================
// LÓGICA DA IA
// ==========================================
function handleAIMove() {
    if (gameOver) return;

    let target;
    if (aiState.mode === 'hunt') {
        target = getHuntTarget();
    } else {
        target = getTargetModeTarget();
    }

    const hit = processAttack(playerBoard, target.row, target.col);
    renderBoard('player-board', playerBoard, true);

    if (hit) {
        document.getElementById('status').innerText = "A IA acertou! Ela joga novamente.";
        updateAIStateOnHit(target.row, target.col);
        
        if (checkVictory(playerBoard)) {
            endGame("A IA venceu!");
            return;
        }
        setTimeout(handleAIMove, 1000); // IA joga novamente por ter acertado
    } else {
        document.getElementById('status').innerText = "A IA errou. Sua vez!";
        updateAIStateOnMiss();
        isPlayerTurn = true;
        disableEnemyBoard(false);
    }
}

// Modo Caça: Atira aleatoriamente
function getHuntTarget() {
    let row, col;
    do {
        row = Math.floor(Math.random() * BOARD_SIZE);
        col = Math.floor(Math.random() * BOARD_SIZE);
    } while (playerBoard[row][col] === 'X' || playerBoard[row][col] === 'O' || playerBoard[row][col] === 'S');
    return { row, col };
}

// Modo Alvo: Segue a lógica inteligente de caça ao redor e na direção
function getTargetModeTarget() {
    if (aiState.direction) {
        return getNextTargetInDirection();
    } else {
        return getAdjacentTarget();
    }
}

// Tenta encontrar alvos adjacentes ao primeiro acerto
function getAdjacentTarget() {
    const origin = aiState.hits[0];
    const shuffledDirs = [...DIRECTIONS].sort(() => Math.random() - 0.5);

    for (let dir of shuffledDirs) {
        if (aiState.triedDirections.includes(dir.toString())) continue;

        const newRow = origin.row + dir[0];
        const newCol = origin.col + dir[1];

        if (isValidTarget(newRow, newCol)) {
            return { row: newRow, col: newCol, dir: dir };
        } else {
            aiState.triedDirections.push(dir.toString());
        }
    }
    return getHuntTarget();
}

// Continua atirando na direção confirmada, para frente e para trás
function getNextTargetInDirection() {
    const dir = aiState.direction;
    const maxHit = aiState.hits.reduce((max, h) => (h.row * dir[0] + h.col * dir[1]) > (max.row * dir[0] + max.col * dir[1]) ? h : max);
    const posTarget = { row: maxHit.row + dir[0], col: maxHit.col + dir[1] };

    if (isValidTarget(posTarget.row, posTarget.col)) {
        return posTarget;
    }

    const minHit = aiState.hits.reduce((min, h) => (h.row * dir[0] + h.col * dir[1]) < (min.row * dir[0] + min.col * dir[1]) ? h : min);
    const negTarget = { row: minHit.row - dir[0], col: minHit.col - dir[1] };

    if (isValidTarget(negTarget.row, negTarget.col)) {
        return negTarget;
    }

    aiState.mode = 'hunt';
    return getHuntTarget();
}

// Atualiza o estado da IA quando acerta um navio
function updateAIStateOnHit(row, col) {
    if (aiState.mode === 'hunt') {
        aiState.mode = 'target';
        aiState.hits = [{ row, col }];
        aiState.direction = null;
        aiState.triedDirections = [];
    } else {
        aiState.hits.push({ row, col });
        
        if (aiState.hits.length >= 2 && !aiState.direction) {
            const first = aiState.hits[0];
            const second = aiState.hits[1];
            aiState.direction = [Math.sign(second.row - first.row), Math.sign(second.col - first.col)];
            aiState.triedDirections = [];
        }
    }

    if (playerBoard[row][col] === 'S') {
        resetAIState();
    }
}

// Atualiza o estado da IA quando erra
function updateAIStateOnMiss() {
    // A lógica de inversão de direção já é tratada em getNextTargetInDirection
}

// Reseta o estado da IA quando um navio é afundado
function resetAIState() {
    aiState = {
        mode: 'hunt',
        hits: [],
        direction: null,
        triedDirections: []
    };
}

// ==========================================
// FUNÇÕES AUXILIARES
// ==========================================

// Processa um ataque em um tabuleiro e retorna true se acertou
function processAttack(board, row, col) {
    if (board[row][col] > 0) { // Acertou um navio
        board[row][col] = 'X'; // Marca como acerto
        checkAndMarkSunkShips(board);
        return true;
    } else if (board[row][col] === 0) { // Água
        board[row][col] = 'O';
        return false;
    }
    return false;
}

// Verifica e marca navios totalmente afundados com 'S'
function checkAndMarkSunkShips(board) {
    markSunkShipHelper(board);
}

function markSunkShipHelper(board) {
    const visited = Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(false));
    
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            if (board[r][c] === 'X' && !visited[r][c]) {
                const shipCells = [];
                const queue = [{r, c}];
                visited[r][c] = true;
                let isSunk = true;

                while (queue.length > 0) {
                    const curr = queue.shift();
                    shipCells.push(curr);

                    for (let dir of DIRECTIONS) {
                        const nr = curr.r + dir[0];
                        const nc = curr.c + dir[1];

                        if (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && !visited[nr][nc]) {
                            if (board[nr][nc] === 'X') {
                                visited[nr][nc] = true;
                                queue.push({r: nr, c: nc});
                            } else if (board[nr][nc] > 0) {
                                isSunk = false;
                                visited[nr][nc] = true; 
                                queue.push({r: nr, c: nc});
                            }
                        }
                    }
                }

                if (isSunk) {
                    shipCells.forEach(cell => {
                        board[cell.r][cell.c] = 'S';
                    });
                }
            }
        }
    }
}

// Verifica se o alvo é válido (dentro do tabuleiro e não atacado)
function isValidTarget(row, col) {
    return row >= 0 && row < BOARD_SIZE && 
           col >= 0 && col < BOARD_SIZE && 
           playerBoard[row][col] !== 'X' && 
           playerBoard[row][col] !== 'O' && 
           playerBoard[row][col] !== 'S';
}

// Verifica a condição de vitória (se não há mais navios intactos)
function checkVictory(board) {
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            if (board[r][c] > 0) {
                return false;
            }
        }
    }
    return true;
}

// Finaliza o jogo
function endGame(message) {
    gameOver = true;
    document.getElementById('status').innerText = message;
    document.getElementById('start-btn').innerText = "Jogar Novamente";
    disableEnemyBoard(true);
    
    // Se a IA venceu, revela as embarcações inimigas não atingidas
    if (message === "A IA venceu!") {
        renderBoard('enemy-board', enemyBoard, true);
    }
}

// Desabilita o tabuleiro inimigo durante o turno da IA
function disableEnemyBoard(disable) {
    const cells = document.querySelectorAll('#enemy-board .cell');
    cells.forEach(cell => {
        if (disable) cell.classList.add('disabled');
        else cell.classList.remove('disabled');
    });
}
