// Go Game Web App - DOM-based rendering
class GoGame {
    constructor() {
        this.boardContainer = document.getElementById('go-board');
        this.boardSize = 19;
        this.gameId = null;
        this.playerColor = 'black';
        this.computerColor = 'white';
        this.boardState = { black: [], white: [] };
        this.gameActive = false;
        this.lastMove = null;
        this.moveCount = 0;
        this.intersections = new Map(); // Map of "x,y" -> intersection element
        this.stones = new Map(); // Map of "x,y" -> stone element
        
        this.setupEventListeners();
        this.createBoardGrid();
        this.updateUI();
    }
    
    setupEventListeners() {
        // Board size selector
        document.getElementById('board-size').addEventListener('change', (e) => {
            this.boardSize = parseInt(e.target.value);
            this.createBoardGrid();
            if (this.gameActive) {
                alert('Board size changed. Please start a new game.');
            }
        });
        
        // Difficulty slider
        const difficultySlider = document.getElementById('difficulty');
        const difficultyValue = document.getElementById('difficulty-value');
        difficultySlider.addEventListener('input', (e) => {
            difficultyValue.textContent = e.target.value;
        });
        
        // Player color radio buttons
        document.querySelectorAll('input[name="player-color"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.playerColor = e.target.value;
                    this.computerColor = this.playerColor === 'black' ? 'white' : 'black';
                    this.updatePlayerDisplay();
                    if (this.gameActive) {
                        alert('Player color changed. Please start a new game.');
                    }
                }
            });
        });
        
        // New game button
        document.getElementById('new-game-btn').addEventListener('click', () => this.startNewGame());
        
        // Pass button
        document.getElementById('pass-btn').addEventListener('click', () => this.passTurn());
        
        // Resign button
        document.getElementById('resign-btn').addEventListener('click', () => this.resignGame());
    }
    
    // Create DOM board grid with intersections
    createBoardGrid() {
        // Clear existing board
        this.boardContainer.innerHTML = '';
        this.intersections.clear();
        this.stones.clear();
        
        const boardSize = this.boardSize;
        const containerSize = Math.min(this.boardContainer.clientWidth, this.boardContainer.clientHeight);
        const cellSize = containerSize / (boardSize + 1);
        
        // Create grid lines
        const gridContainer = document.createElement('div');
        gridContainer.className = 'board-grid';
        
        // Vertical lines
        for (let i = 0; i < boardSize; i++) {
            const line = document.createElement('div');
            line.className = 'grid-line vertical';
            line.style.left = `${(i + 1) * cellSize}px`;
            line.style.width = '1px';
            line.style.height = '100%';
            gridContainer.appendChild(line);
        }
        
        // Horizontal lines
        for (let i = 0; i < boardSize; i++) {
            const line = document.createElement('div');
            line.className = 'grid-line horizontal';
            line.style.top = `${(i + 1) * cellSize}px`;
            line.style.height = '1px';
            line.style.width = '100%';
            gridContainer.appendChild(line);
        }
        
        this.boardContainer.appendChild(gridContainer);
        
        // Create intersections
        const intersectionSize = cellSize * 0.9;
        for (let x = 0; x < boardSize; x++) {
            for (let y = 0; y < boardSize; y++) {
                const intersection = document.createElement('div');
                intersection.className = 'intersection';
                intersection.dataset.x = x;
                intersection.dataset.y = y;
                intersection.style.left = `${(x + 1) * cellSize}px`;
                intersection.style.top = `${(y + 1) * cellSize}px`;
                intersection.style.width = `${intersectionSize}px`;
                intersection.style.height = `${intersectionSize}px`;
                
                intersection.addEventListener('click', (e) => this.handleIntersectionClick(e));
                this.boardContainer.appendChild(intersection);
                this.intersections.set(`${x},${y}`, intersection);
            }
        }
        
        // Create star points
        const starPoints = this.getStarPoints();
        const starSize = cellSize * 0.1;
        starPoints.forEach(point => {
            const star = document.createElement('div');
            star.className = 'star-point';
            star.style.left = `${(point.x + 1) * cellSize}px`;
            star.style.top = `${(point.y + 1) * cellSize}px`;
            star.style.width = `${starSize}px`;
            star.style.height = `${starSize}px`;
            star.style.borderRadius = '50%';
            this.boardContainer.appendChild(star);
        });
        
        // Store cell size for coordinate conversions
        this.cellSize = cellSize;
    }
    
    getStarPoints() {
        const points = [];
        const size = this.boardSize;
        
        if (size === 9) {
            const coords = [2, 6];
            for (const x of coords) {
                for (const y of coords) {
                    points.push({ x, y });
                }
            }
            points.push({ x: 4, y: 4 });
        } else if (size === 13) {
            const coords = [3, 9];
            for (const x of coords) {
                for (const y of coords) {
                    points.push({ x, y });
                }
            }
            points.push({ x: 6, y: 6 });
        } else if (size === 19) {
            const coords = [3, 9, 15];
            for (const x of coords) {
                for (const y of coords) {
                    points.push({ x, y });
                }
            }
        }
        return points;
    }
    
    handleIntersectionClick(event) {
        if (!this.gameActive) {
            alert('Please start a new game first.');
            return;
        }
        
        const intersection = event.currentTarget;
        const x = parseInt(intersection.dataset.x);
        const y = parseInt(intersection.dataset.y);
        
        // Check if intersection already occupied
        const vertex = this.boardToVertex(x, y);
        const occupied = this.boardState.black.includes(vertex) || this.boardState.white.includes(vertex);
        if (occupied) {
            alert('Intersection already occupied.');
            return;
        }
        
        this.makeMove(vertex);
    }
    
    // Convert board coordinates to GTP vertex (e.g., D4)
    boardToVertex(x, y) {
        const letters = 'ABCDEFGHJKLMNOPQRST';
        const colLetter = letters[x];
        const row = this.boardSize - y;
        return `${colLetter}${row}`;
    }
    
    // Convert GTP vertex to board coordinates
    vertexToBoard(vertex) {
        if (vertex.toLowerCase() === 'pass' || vertex.toLowerCase() === 'resign') {
            return null;
        }
        const letters = 'ABCDEFGHJKLMNOPQRST';
        const colLetter = vertex[0].toUpperCase();
        const rowStr = vertex.slice(1);
        const row = parseInt(rowStr);
        const x = letters.indexOf(colLetter);
        const y = this.boardSize - row;
        return { x, y };
    }
    
    async startNewGame() {
        const boardSize = parseInt(document.getElementById('board-size').value);
        const difficulty = parseInt(document.getElementById('difficulty').value);
        const playerColor = document.querySelector('input[name="player-color"]:checked').value;
        
        // Update local state
        this.boardSize = boardSize;
        this.playerColor = playerColor;
        this.computerColor = playerColor === 'black' ? 'white' : 'black';
        this.boardState = { black: [], white: [] };
        this.gameActive = false;
        this.lastMove = null;
        this.moveCount = 0;
        
        // Clear stones from board
        this.stones.forEach(stone => stone.remove());
        this.stones.clear();
        
        // Recreate grid with new size
        this.createBoardGrid();
        
        try {
            const response = await fetch('/api/game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    board_size: boardSize,
                    difficulty: difficulty,
                    player_color: playerColor,
                    komi: 6.5
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create game: ${response.status}`);
            }
            
            const gameState = await response.json();
            this.gameId = gameState.game_id;
            this.boardState = gameState.board_state;
            this.gameActive = !gameState.game_over;
            this.moveCount = gameState.move_count;
            
            this.drawBoard();
            this.updateUI();
            this.addLogEntry('Game started');
            
            // If player is white, computer has already made first move
            if (playerColor === 'white' && gameState.board_state.white.length > 0) {
                this.addLogEntry(`Computer plays ${gameState.board_state.white[0]}`);
            }
        } catch (error) {
            console.error('Error starting new game:', error);
            alert(`Failed to start new game: ${error.message}`);
        }
    }
    
    async makeMove(vertex) {
        if (!this.gameActive || !this.gameId) return;
        
        try {
            const response = await fetch(`/api/game/${this.gameId}/move`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ vertex })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `Move failed with status ${response.status}`);
            }
            
            const result = await response.json();
            this.boardState = result.game_state.board_state;
            this.gameActive = !result.game_state.game_over;
            this.moveCount = result.game_state.move_count;
            this.lastMove = vertex;
            
            this.drawBoard();
            this.updateUI();
            this.addLogEntry(`You play ${vertex}`);
            
            if (result.computer_move) {
                this.addLogEntry(`Computer plays ${result.computer_move}`);
            }
            
            if (result.game_over) {
                this.addLogEntry(`Game over: ${result.game_state.result}`);
                alert(`Game over: ${result.game_state.result}`);
            }
        } catch (error) {
            console.error('Error making move:', error);
            alert(`Move failed: ${error.message}`);
        }
    }
    
    async passTurn() {
        if (!this.gameActive || !this.gameId) return;
        
        await this.makeMove('pass');
    }
    
    async resignGame() {
        if (!this.gameActive || !this.gameId) return;
        
        try {
            const response = await fetch(`/api/game/${this.gameId}/resign`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`Resign failed with status ${response.status}`);
            }
            
            const gameState = await response.json();
            this.boardState = gameState.board_state;
            this.gameActive = false;
            
            this.drawBoard();
            this.updateUI();
            this.addLogEntry('You resigned');
            alert(`Game over: ${gameState.result}`);
        } catch (error) {
            console.error('Error resigning:', error);
            alert(`Resign failed: ${error.message}`);
        }
    }
    
    drawBoard() {
        // Clear existing stones
        this.stones.forEach(stone => stone.remove());
        this.stones.clear();
        
        // Remove last-move highlight from all intersections
        this.intersections.forEach(intersection => {
            intersection.classList.remove('last-move');
        });
        
        // Draw black stones
        this.boardState.black.forEach(vertex => {
            const pos = this.vertexToBoard(vertex);
            if (pos) this.drawStone(pos.x, pos.y, 'black');
        });
        
        // Draw white stones
        this.boardState.white.forEach(vertex => {
            const pos = this.vertexToBoard(vertex);
            if (pos) this.drawStone(pos.x, pos.y, 'white');
        });
        
        // Highlight last move
        if (this.lastMove) {
            const pos = this.vertexToBoard(this.lastMove);
            if (pos) {
                const intersection = this.intersections.get(`${pos.x},${pos.y}`);
                if (intersection) {
                    intersection.classList.add('last-move');
                }
            }
        }
    }
    
    drawStone(x, y, color) {
        const intersection = this.intersections.get(`${x},${y}`);
        if (!intersection) return;
        
        const stone = document.createElement('div');
        stone.className = `stone ${color}`;
        stone.dataset.x = x;
        stone.dataset.y = y;
        
        // Position stone at intersection center
        stone.style.left = intersection.style.left;
        stone.style.top = intersection.style.top;
        
        // Size stone proportionally to cell size
        const diameter = this.cellSize * 0.85;
        stone.style.width = `${diameter}px`;
        stone.style.height = `${diameter}px`;
        
        this.boardContainer.appendChild(stone);
        this.stones.set(`${x},${y}`, stone);
    }
    
    updateUI() {
        // Toggle sidebar sections based on game state
        const settingsSection = document.getElementById('settings-section');
        const actionsSection = document.getElementById('actions-section');
        const gameInfoSection = document.getElementById('game-info-section');
        
        if (this.gameActive) {
            settingsSection.classList.add('hidden');
            actionsSection.classList.remove('hidden');
            gameInfoSection.classList.remove('hidden');
        } else {
            settingsSection.classList.remove('hidden');
            actionsSection.classList.add('hidden');
            gameInfoSection.classList.add('hidden');
        }
        
        // Update player/computer colors
        const playerColorEl = document.getElementById('player-color');
        playerColorEl.textContent = this.playerColor;
        playerColorEl.className = `stone-indicator ${this.playerColor}-stone`;
        
        const computerColorEl = document.getElementById('computer-color');
        computerColorEl.textContent = this.computerColor;
        computerColorEl.className = `stone-indicator ${this.computerColor}-stone`;
        
        // Update game status
        const gameStatus = document.getElementById('game-status');
        gameStatus.textContent = this.gameActive ? 'Active' : 'Ended';
        gameStatus.className = this.gameActive ? 'status-active' : 'status-ended';
        
        // Update move count
        document.getElementById('move-count').textContent = this.moveCount;
        
        // Update last move
        document.getElementById('last-move').textContent = this.lastMove || 'None';
        
        // Enable/disable buttons
        document.getElementById('pass-btn').disabled = !this.gameActive;
        document.getElementById('resign-btn').disabled = !this.gameActive;
    }
    
    addLogEntry(message) {
        const logBox = document.getElementById('move-log');
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
        logBox.appendChild(entry);
        logBox.scrollTop = logBox.scrollHeight;
    }
    
    updatePlayerDisplay() {
        document.querySelectorAll('input[name="player-color"]').forEach(radio => {
            if (radio.value === this.playerColor) {
                radio.checked = true;
            }
        });
    }
}

// Initialize the game when page loads
window.addEventListener('DOMContentLoaded', () => {
    window.goGame = new GoGame();
});