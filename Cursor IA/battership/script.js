/**
 * Batalha Naval — Homem vs Máquina
 * Tabuleiro 10x10, frota clássica, jogada extra ao acertar.
 */

const BOARD_SIZE = 10;

/** Frota padrão: nome, tamanho */
const FLEET = [
  { name: "Porta-aviões", size: 5 },
  { name: "Encouraçado", size: 4 },
  { name: "Cruzador", size: 3 },
  { name: "Submarino", size: 3 },
  { name: "Destroyer", size: 2 },
];

/** Estados do jogo */
const GamePhase = {
  PLACING: "placing",
  BATTLE: "battle",
  ENDED: "ended",
};

/** Tipos de célula no modelo interno */
const CellState = {
  EMPTY: "empty",
  SHIP: "ship",
  MISS: "miss",
  HIT: "hit",
  SUNK: "sunk",
};

// ===== Estado global =====
const state = {
  phase: GamePhase.PLACING,
  currentShipIndex: 0,
  horizontal: true,
  playerTurn: true,
  extraTurn: false, // jogada extra pendente (humano)
  playerBoard: null,
  enemyBoard: null,
  playerShips: [],
  enemyShips: [],
};

/** Modos da IA */
const AiMode = {
  HUNT: "hunt",       // alvos aleatórios
  TARGET: "target",   // 4 células ortogonais ao primeiro acerto
  DESTROY: "destroy", // linha na direção: um sentido até água, depois o outro
};

/** IA: estado da máquina de busca */
const aiState = {
  shots: new Set(),
  mode: AiMode.HUNT,
  hits: [], // acertos da embarcação atual (não afundada)
  direction: null, // { dr, dc } após 2º acerto alinhado
  queue: [], // fila dos 4 vizinhos (modo TARGET)
  destroyLeg: "forward", // "forward" | "backward" — sentido ativo no DESTROY
};

// ===== Referências DOM =====
const dom = {
  playerBoard: document.getElementById("player-board"),
  enemyBoard: document.getElementById("enemy-board"),
  status: document.getElementById("status"),
  currentShip: document.getElementById("current-ship"),
  btnHorizontal: document.getElementById("btn-horizontal"),
  btnVertical: document.getElementById("btn-vertical"),
  btnRandom: document.getElementById("btn-random"),
  btnStart: document.getElementById("btn-start"),
  btnRestart: document.getElementById("btn-restart"),
  fleetSetup: document.getElementById("fleet-setup"),
};

// =============================================================================
// INICIALIZAÇÃO DO TABULEIRO
// =============================================================================

/**
 * Cria matriz vazia BOARD_SIZE x BOARD_SIZE.
 * @returns {string[][]}
 */
function createEmptyBoard() {
  return Array.from({ length: BOARD_SIZE }, () =>
    Array(BOARD_SIZE).fill(CellState.EMPTY)
  );
}

/**
 * Inicializa tabuleiros, frota e interface para nova partida.
 */
function initGame() {
  state.phase = GamePhase.PLACING;
  state.currentShipIndex = 0;
  state.horizontal = true;
  state.playerTurn = true;
  state.extraTurn = false;
  state.playerBoard = createEmptyBoard();
  state.enemyBoard = createEmptyBoard();
  state.playerShips = [];
  state.enemyShips = [];

  resetAiState();
  placeEnemyFleetRandomly();

  document.body.classList.add("placing");
  dom.fleetSetup.classList.remove("hidden");
  dom.btnRestart.classList.add("hidden");
  dom.btnStart.disabled = true;
  dom.btnHorizontal.classList.add("active");
  dom.btnVertical.classList.remove("active");

  renderBoard(dom.playerBoard, state.playerBoard, "player");
  renderBoard(dom.enemyBoard, state.enemyBoard, "enemy", false);
  updateShipLabel();
  setStatus("Clique no seu tabuleiro para posicionar as embarcações.");
}

/**
 * Reinicia estado da IA.
 */
function resetAiState() {
  aiState.shots = new Set();
  aiState.mode = AiMode.HUNT;
  aiState.hits = [];
  aiState.direction = null;
  aiState.queue = [];
  aiState.destroyLeg = "forward";
}

// =============================================================================
// POSICIONAMENTO DE EMBARCAÇÕES
// =============================================================================

/**
 * Verifica se embarcação cabe na posição.
 */
function canPlaceShip(board, row, col, size, horizontal) {
  if (horizontal) {
    if (col + size > BOARD_SIZE) return false;
  } else {
    if (row + size > BOARD_SIZE) return false;
  }

  for (let i = 0; i < size; i++) {
    const r = horizontal ? row : row + i;
    const c = horizontal ? col + i : col;
    if (board[r][c] !== CellState.EMPTY) return false;
    // sem encostar em outra embarcação (inclui diagonais)
    for (let dr = -1; dr <= 1; dr++) {
      for (let dc = -1; dc <= 1; dc++) {
        const nr = r + dr;
        const nc = c + dc;
        if (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE) {
          if (board[nr][nc] === CellState.SHIP && !(nr === r && nc === c)) {
            return false;
          }
        }
      }
    }
  }
  return true;
}

/**
 * Coloca embarcação no tabuleiro e registra na lista de navios.
 */
function placeShip(board, ships, row, col, size, horizontal) {
  const cells = [];
  for (let i = 0; i < size; i++) {
    const r = horizontal ? row : row + i;
    const c = horizontal ? col + i : col;
    board[r][c] = CellState.SHIP;
    cells.push({ row: r, col: c });
  }
  ships.push({ cells, hits: 0, sunk: false });
}

/**
 * Posiciona frota inteira aleatoriamente (jogador ou inimigo).
 */
function placeFleetRandomly(board, ships) {
  for (const ship of FLEET) {
    let placed = false;
    let attempts = 0;
    while (!placed && attempts < 500) {
      const horizontal = Math.random() < 0.5;
      const row = Math.floor(Math.random() * BOARD_SIZE);
      const col = Math.floor(Math.random() * BOARD_SIZE);
      if (canPlaceShip(board, row, col, ship.size, horizontal)) {
        placeShip(board, ships, row, col, ship.size, horizontal);
        placed = true;
      }
      attempts++;
    }
  }
}

function placeEnemyFleetRandomly() {
  state.enemyShips = [];
  placeFleetRandomly(state.enemyBoard, state.enemyShips);
}

/**
 * Handler: clique no tabuleiro do jogador na fase de posicionamento.
 */
function onPlayerBoardPlace(row, col) {
  if (state.phase !== GamePhase.PLACING) return;
  const ship = FLEET[state.currentShipIndex];
  if (!canPlaceShip(state.playerBoard, row, col, ship.size, state.horizontal)) {
    setStatus("Não é possível colocar aqui. Tente outra posição.");
    return;
  }

  placeShip(
    state.playerBoard,
    state.playerShips,
    row,
    col,
    ship.size,
    state.horizontal
  );
  state.currentShipIndex++;

  if (state.currentShipIndex >= FLEET.length) {
    dom.btnStart.disabled = false;
    setStatus("Todas as embarcações posicionadas! Clique em Iniciar batalha.");
    updateShipLabel(true);
  } else {
    updateShipLabel();
    setStatus(`"${FLEET[state.currentShipIndex].name}" posicionado. Próxima embarcação.`);
  }

  renderBoard(dom.playerBoard, state.playerBoard, "player");
}

function onPlayerBoardHover(row, col) {
  if (state.phase !== GamePhase.PLACING) return;
  const ship =
    state.currentShipIndex < FLEET.length
      ? FLEET[state.currentShipIndex]
      : null;
  renderBoard(dom.playerBoard, state.playerBoard, "player", true, row, col, ship);
}

// =============================================================================
// RENDERIZAÇÃO
// =============================================================================

function cellKey(row, col) {
  return `${row},${col}`;
}

/**
 * Atualiza visual de um tabuleiro.
 * @param {boolean} showShips - mostrar embarcações (tabuleiro do jogador)
 * @param {boolean} attackable - células de água clicáveis (ataque ao inimigo)
 */
function renderBoard(
  container,
  board,
  owner,
  showShips = true,
  previewRow = null,
  previewCol = null,
  previewShip = null
) {
  container.innerHTML = "";
  const isPlacing = state.phase === GamePhase.PLACING && owner === "player";
  const attackable =
    state.phase === GamePhase.BATTLE &&
    owner === "enemy" &&
    state.playerTurn;

  for (let row = 0; row < BOARD_SIZE; row++) {
    for (let col = 0; col < BOARD_SIZE; col++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.row = row;
      cell.dataset.col = col;
      cell.setAttribute("role", "gridcell");

      const value = board[row][col];
      let preview = false;
      let previewValid = false;

      if (
        isPlacing &&
        previewShip &&
        previewRow !== null &&
        previewCol !== null
      ) {
        preview = isCellInShipPlacement(
          row,
          col,
          previewRow,
          previewCol,
          previewShip.size,
          state.horizontal
        );
        if (preview) {
          previewValid = canPlaceShip(
            board,
            previewRow,
            previewCol,
            previewShip.size,
            state.horizontal
          );
        }
      }

      if (preview) {
        cell.classList.add(
          previewValid ? "cell--preview" : "cell--preview-invalid"
        );
        cell.textContent = previewValid ? "" : "✕";
      } else {
        applyCellVisual(cell, value, showShips);
        if (value === CellState.EMPTY || value === CellState.SHIP) {
          cell.classList.add("cell--water");
        }
        if (
          attackable &&
          value !== CellState.MISS &&
          value !== CellState.HIT &&
          value !== CellState.SUNK
        ) {
          cell.classList.add("cell--attackable");
        }
      }

      if (isPlacing) {
        cell.addEventListener("click", () => onPlayerBoardPlace(row, col));
        cell.addEventListener("mouseenter", () => onPlayerBoardHover(row, col));
      } else if (attackable) {
        const shot =
          value === CellState.MISS ||
          value === CellState.HIT ||
          value === CellState.SUNK;
        if (!shot) {
          cell.addEventListener("click", () => onPlayerAttack(row, col));
        }
      }

      container.appendChild(cell);
    }
  }
}

function isCellInShipPlacement(row, col, startRow, startCol, size, horizontal) {
  for (let i = 0; i < size; i++) {
    const r = horizontal ? startRow : startRow + i;
    const c = horizontal ? startCol : startCol + i;
    if (r === row && c === col) return true;
  }
  return false;
}

function applyCellVisual(cell, value, showShips) {
  cell.classList.remove(
    "cell--water",
    "cell--ship",
    "cell--miss",
    "cell--hit",
    "cell--sunk"
  );

  switch (value) {
    case CellState.SHIP:
      if (showShips) {
        cell.classList.add("cell--ship");
        cell.textContent = "";
      } else {
        cell.classList.add("cell--water");
        cell.textContent = "";
      }
      break;
    case CellState.MISS:
      cell.classList.add("cell--miss");
      cell.textContent = "💨";
      break;
    case CellState.HIT:
      cell.classList.add("cell--hit");
      cell.textContent = "💥";
      break;
    case CellState.SUNK:
      cell.classList.add("cell--sunk");
      cell.textContent = "🔥";
      break;
    default:
      cell.classList.add("cell--water");
      cell.textContent = "";
  }
}

function updateShipLabel(allDone = false) {
  if (allDone) {
    dom.currentShip.textContent = "Frota completa ✓";
    return;
  }
  const ship = FLEET[state.currentShipIndex];
  dom.currentShip.textContent = `${ship.name} (${ship.size})`;
}

function setStatus(message, type = "") {
  dom.status.textContent = "";
  dom.status.innerHTML = message;
  dom.status.classList.remove("status--win", "status--lose");
  if (type === "win") dom.status.classList.add("status--win");
  if (type === "lose") dom.status.classList.add("status--lose");
}

// =============================================================================
// LÓGICA DE DISPARO (compartilhada)
// =============================================================================

/**
 * Registra disparo em (row, col). Retorna { hit, sunk, ship }.
 */
function fireShot(board, ships, row, col) {
  const cell = board[row][col];
  if (cell === CellState.MISS || cell === CellState.HIT || cell === CellState.SUNK) {
    return { alreadyShot: true };
  }

  if (cell === CellState.EMPTY) {
    board[row][col] = CellState.MISS;
    return { hit: false, sunk: false };
  }

  // Acertou embarcação
  board[row][col] = CellState.HIT;
  const ship = ships.find(
    (s) =>
      !s.sunk &&
      s.cells.some((c) => c.row === row && c.col === col)
  );
  if (!ship) return { hit: true, sunk: false };

  ship.hits++;
  const allHit = ship.cells.every(
    (c) =>
      board[c.row][c.col] === CellState.HIT ||
      board[c.row][c.col] === CellState.SUNK
  );

  if (allHit) {
    ship.sunk = true;
    for (const c of ship.cells) {
      board[c.row][c.col] = CellState.SUNK;
    }
    return { hit: true, sunk: true, ship };
  }

  return { hit: true, sunk: false, ship };
}

// =============================================================================
// JOGADAS DO JOGADOR
// =============================================================================

/**
 * Ataque do jogador humano ao tabuleiro inimigo.
 */
function onPlayerAttack(row, col) {
  if (state.phase !== GamePhase.BATTLE || !state.playerTurn) return;

  const key = cellKey(row, col);
  const cell = state.enemyBoard[row][col];
  if (
    cell === CellState.MISS ||
    cell === CellState.HIT ||
    cell === CellState.SUNK
  ) {
    return;
  }

  const result = fireShot(state.enemyBoard, state.enemyShips, row, col);
  if (result.alreadyShot) return;

  renderBoard(dom.enemyBoard, state.enemyBoard, "enemy", false);

  if (checkVictory(state.enemyShips)) {
    endGame(true);
    return;
  }

  if (result.hit) {
    const msg = result.sunk
      ? `💥 Você afundou o ${result.ship ? "navio inimigo" : "navio"}! Jogada extra.`
      : "💥 Acertou! Jogada extra — ataque novamente.";
    setStatus(msg);
    state.extraTurn = true;
    state.playerTurn = true;
    renderBoard(dom.enemyBoard, state.enemyBoard, "enemy", false);
    return;
  }

  setStatus("💨 Errou. Vez da máquina...");
  state.playerTurn = false;
  state.extraTurn = false;
  renderBoard(dom.enemyBoard, state.enemyBoard, "enemy", false);
  dom.enemyBoard.classList.add("board--locked");
  setTimeout(runAiTurn, 600);
}

// =============================================================================
// JOGADAS DA IA
// =============================================================================
//
// 1) HUNT   — tiro aleatório até acertar.
// 2) TARGET — atira nas 4 células ortogonais ao 1º acerto, uma a uma,
//             até achar o 2º acerto (mesma embarcação).
// 3) DESTROY — com direção definida (horizontal/vertical), estende num
//             sentido até água (erro); depois no sentido oposto até água.

/** Vizinhos ortogonais: cima, baixo, esquerda, direita */
const ORTHOGONAL = [
  { dr: -1, dc: 0 },
  { dr: 1, dc: 0 },
  { dr: 0, dc: -1 },
  { dr: 0, dc: 1 },
];

function isValidCoord(row, col) {
  return row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE;
}

function isUnshotCell(row, col) {
  return isValidCoord(row, col) && !aiState.shots.has(cellKey(row, col));
}

/**
 * Escolhe o próximo alvo conforme o modo atual.
 */
function aiChooseTarget() {
  if (aiState.mode === AiMode.HUNT) {
    return aiRandomTarget();
  }

  if (aiState.mode === AiMode.TARGET) {
    return aiNextTargetNeighbor();
  }

  if (aiState.mode === AiMode.DESTROY) {
    return aiNextDestroyTarget();
  }

  return aiRandomTarget();
}

/** Tiro aleatório em célula ainda não atacada. */
function aiRandomTarget() {
  const available = [];
  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      if (isUnshotCell(r, c)) available.push({ row: r, col: c });
    }
  }
  if (available.length === 0) return null;
  return available[Math.floor(Math.random() * available.length)];
}

/**
 * Enfileira as 4 células ao redor do acerto (ordem embaralhada).
 */
function enqueueOrthogonalNeighbors({ row, col }) {
  const neighbors = [];
  for (const { dr, dc } of ORTHOGONAL) {
    const nr = row + dr;
    const nc = col + dc;
    if (isUnshotCell(nr, nc)) {
      neighbors.push({ row: nr, col: nc });
    }
  }
  for (let i = neighbors.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [neighbors[i], neighbors[j]] = [neighbors[j], neighbors[i]];
  }
  aiState.queue = neighbors;
}

/**
 * TARGET: próxima célula da fila dos 4 vizinhos; reabastece se necessário.
 */
function aiNextTargetNeighbor() {
  while (aiState.queue.length > 0) {
    const next = aiState.queue.shift();
    if (isUnshotCell(next.row, next.col)) return next;
  }

  if (aiState.hits.length === 1) {
    enqueueOrthogonalNeighbors(aiState.hits[0]);
    if (aiState.queue.length > 0) return aiState.queue.shift();
  }

  return aiRandomTarget();
}

/**
 * Infere direção horizontal ou vertical a partir de dois acertos alinhados.
 */
function inferDirectionFromHits() {
  const hits = aiState.hits;
  for (let i = 0; i < hits.length; i++) {
    for (let j = i + 1; j < hits.length; j++) {
      const a = hits[i];
      const b = hits[j];
      if (a.row === b.row) {
        aiState.direction = { dr: 0, dc: b.col > a.col ? 1 : -1 };
        return true;
      }
      if (a.col === b.col) {
        aiState.direction = { dr: b.row > a.row ? 1 : -1, dc: 0 };
        return true;
      }
    }
  }
  return false;
}

/**
 * Extremos da linha de acertos na direção da embarcação.
 */
function getLineExtents(hits, dr, dc) {
  if (dr === 0) {
    const row = hits[0].row;
    let minCol = hits[0].col;
    let maxCol = hits[0].col;
    for (const h of hits) {
      minCol = Math.min(minCol, h.col);
      maxCol = Math.max(maxCol, h.col);
    }
    return {
      min: { row, col: minCol },
      max: { row, col: maxCol },
    };
  }
  const col = hits[0].col;
  let minRow = hits[0].row;
  let maxRow = hits[0].row;
  for (const h of hits) {
    minRow = Math.min(minRow, h.row);
    maxRow = Math.max(maxRow, h.row);
  }
  return {
    min: { row: minRow, col },
    max: { row: maxRow, col },
  };
}

/** Próxima célula no sentido "forward" (+direção) a partir do extremo máximo. */
function getForwardTarget() {
  const { dr, dc } = aiState.direction;
  const { max } = getLineExtents(aiState.hits, dr, dc);
  return { row: max.row + dr, col: max.col + dc };
}

/** Próxima célula no sentido "backward" (−direção) a partir do extremo mínimo. */
function getBackwardTarget() {
  const { dr, dc } = aiState.direction;
  const { min } = getLineExtents(aiState.hits, dr, dc);
  return { row: min.row - dr, col: min.col - dc };
}

/**
 * DESTROY: um sentido por vez — forward até água, depois backward até água.
 */
function aiNextDestroyTarget() {
  if (!aiState.direction) {
    inferDirectionFromHits();
  }
  if (!aiState.direction) {
    return aiNextTargetNeighbor();
  }

  if (aiState.destroyLeg === "forward") {
    const next = getForwardTarget();
    if (isUnshotCell(next.row, next.col)) return next;
    aiState.destroyLeg = "backward";
  }

  if (aiState.destroyLeg === "backward") {
    const next = getBackwardTarget();
    if (isUnshotCell(next.row, next.col)) return next;
  }

  return null;
}

/** Entra no modo DESTROY após o 2º acerto na mesma embarcação. */
function enterDestroyMode() {
  aiState.mode = AiMode.DESTROY;
  aiState.queue = [];
  aiState.destroyLeg = "forward";
  inferDirectionFromHits();
}

/** Zera estado da IA ao afundar embarcação. */
function resetAiTargeting() {
  aiState.mode = AiMode.HUNT;
  aiState.hits = [];
  aiState.direction = null;
  aiState.queue = [];
  aiState.destroyLeg = "forward";
}

/**
 * Atualiza a IA após cada disparo.
 */
function updateAiAfterShot(row, col, result) {
  aiState.shots.add(cellKey(row, col));

  if (result.sunk) {
    resetAiTargeting();
    return;
  }

  if (!result.hit) {
    if (aiState.mode === AiMode.DESTROY && aiState.destroyLeg === "forward") {
      aiState.destroyLeg = "backward";
    }
    return;
  }

  const coord = { row, col };
  if (!aiState.hits.some((h) => h.row === row && h.col === col)) {
    aiState.hits.push(coord);
  }

  if (aiState.mode === AiMode.HUNT) {
    aiState.mode = AiMode.TARGET;
    enqueueOrthogonalNeighbors(coord);
    return;
  }

  if (aiState.mode === AiMode.TARGET && aiState.hits.length >= 2) {
    enterDestroyMode();
    return;
  }

  if (aiState.mode === AiMode.DESTROY) {
    inferDirectionFromHits();
  }
}

/**
 * Executa um turno da IA (pode encadear jogadas extras).
 */
function runAiTurn() {
  if (state.phase !== GamePhase.BATTLE || state.playerTurn) {
    dom.enemyBoard.classList.remove("board--locked");
    return;
  }

  const target = aiChooseTarget();
  if (!target) {
    state.playerTurn = true;
    dom.enemyBoard.classList.remove("board--locked");
    setStatus("Sua vez! Clique no tabuleiro inimigo.");
    return;
  }

  const { row, col } = target;
  const result = fireShot(state.playerBoard, state.playerShips, row, col);
  updateAiAfterShot(row, col, result);

  renderBoard(dom.playerBoard, state.playerBoard, "player");

  if (checkVictory(state.playerShips)) {
    dom.enemyBoard.classList.remove("board--locked");
    endGame(false);
    return;
  }

  if (result.hit) {
    const sunkMsg = result.sunk ? " A máquina afundou uma embarcação!" : "";
    setStatus(`🤖 A máquina acertou!${sunkMsg} Jogada extra da IA...`);
    setTimeout(runAiTurn, 500);
    return;
  }

  setStatus("🤖 A máquina errou. Sua vez — clique no tabuleiro inimigo!");
  state.playerTurn = true;
  dom.enemyBoard.classList.remove("board--locked");
  renderBoard(dom.enemyBoard, state.enemyBoard, "enemy", false);
}

// =============================================================================
// VERIFICAÇÃO DE VITÓRIA
// =============================================================================

/**
 * Retorna true se toda a frota estiver afundada.
 */
function checkVictory(ships) {
  return ships.length > 0 && ships.every((s) => s.sunk);
}

function endGame(playerWon) {
  state.phase = GamePhase.ENDED;
  document.body.classList.remove("placing");
  dom.fleetSetup.classList.add("hidden");
  dom.btnRestart.classList.remove("hidden");
  dom.enemyBoard.classList.remove("board--locked");

  renderBoard(dom.playerBoard, state.playerBoard, "player");
  renderBoard(dom.enemyBoard, state.enemyBoard, "enemy", true);

  if (playerWon) {
    setStatus("🎉 Vitória! Você destruiu toda a frota inimiga!", "win");
  } else {
    setStatus("😞 Derrota! A máquina destruiu sua frota.", "lose");
  }
}

// =============================================================================
// INÍCIO DA BATALHA E EVENTOS
// =============================================================================

function startBattle() {
  if (state.currentShipIndex < FLEET.length) return;

  state.phase = GamePhase.BATTLE;
  state.playerTurn = true;
  state.extraTurn = false;
  document.body.classList.remove("placing");
  dom.fleetSetup.classList.add("hidden");

  renderBoard(dom.playerBoard, state.playerBoard, "player");
  renderBoard(dom.enemyBoard, state.enemyBoard, "enemy", false);
  setStatus("Batalha iniciada! Sua vez — ataque o tabuleiro inimigo.");
}

function wireEvents() {
  dom.btnHorizontal.addEventListener("click", () => {
    state.horizontal = true;
    dom.btnHorizontal.classList.add("active");
    dom.btnVertical.classList.remove("active");
  });

  dom.btnVertical.addEventListener("click", () => {
    state.horizontal = false;
    dom.btnVertical.classList.add("active");
    dom.btnHorizontal.classList.remove("active");
  });

  dom.btnRandom.addEventListener("click", () => {
    state.playerBoard = createEmptyBoard();
    state.playerShips = [];
    state.currentShipIndex = FLEET.length;
    placeFleetRandomly(state.playerBoard, state.playerShips);
    dom.btnStart.disabled = false;
    updateShipLabel(true);
    renderBoard(dom.playerBoard, state.playerBoard, "player");
    setStatus("Frota posicionada aleatoriamente. Clique em Iniciar batalha.");
  });

  dom.btnStart.addEventListener("click", startBattle);
  dom.btnRestart.addEventListener("click", initGame);

  dom.playerBoard.addEventListener("mouseleave", () => {
    if (state.phase === GamePhase.PLACING) {
      renderBoard(dom.playerBoard, state.playerBoard, "player");
    }
  });
}

// ===== Boot =====
wireEvents();
initGame();
