// Go Game Web App
class GoGame {
    constructor() {
        this.canvas = document.getElementById('go-board');
        this.ctx = this.canvas.getContext('2d');
        this.boardSize = 19;
        this.cellSize = this.canvas.width / (this.boardSize + 1);
        this.stoneRadius = this.cellSize * 0.45;
        this.gameId = null;
        this.playerColor = 'black';
        this.computerColor = 'white';
        this.boardState = { black: [], white: [] };
        this.gameActive = false;
        this.lastMove = null;
        this.moveCount = 0;
        
        this.setupEventListeners();
        this.drawEmptyBoard();
        this.updateUI();
    }
    
    setupEventListeners() {
        // Canvas click for placing stones
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        
        // New game button
        document.getElementById('new-game-btn').addEventListener('click', () => this.startNewGame());
        
        // Pass button
        document.getElementById('pass-btn').addEventListener('click', () => this.passTurn());
        
        // Resign button
        document.getElementById('resign-btn').addEventListener('click', () => this.resignGame());
        
        // Board size selector
        document.getElementById('board-size').addEventListener('change', (e) => {
            this.boardSize = parseInt(e.target.value);
            this.cellSize = this.canvas.width / (this.boardSize + 1);
            this.stoneRadius = this.cellSize * 0.45;
            this.drawEmptyBoard();
            // If game active, need to reload board state? Actually board size change requires new game
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
    }
    
    // Convert canvas coordinates to board intersection (0-indexed)
    getBoardPosition(x, y) {
        const rect = this.canvas.getBoundingClientRect();
        const clickX = x - rect.left;
        const clickY = y - rect.top;
        
        // Find nearest intersection
        const boardX = Math.round(clickX / this.cellSize) - 1;
        const boardY = Math.round(clickY / this.cellSize) - 1;
        
        // Ensure within bounds
        if (boardX >= 0 && boardX < this.boardSize && boardY >= 0 && boardY < this.boardSize) {
            return { x: boardX, y: boardY };
        }
        return null;
    }
    
    // Convert board coordinates to GTP vertex (e.g., D4)
    boardToVertex(x, y) {
        // GTP uses letters A-T skipping I, row numbers from bottom
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
    
    handleCanvasClick(event) {
        if (!this.gameActive) {
            alert('Please start a new game first.');
            return;
        }
        
        const pos = this.getBoardPosition(event.clientX, event.clientY);
        if (!pos) return;
        
        // Check if intersection already occupied
        const vertex = this.boardToVertex(pos.x, pos.y);
        const occupied = this.boardState.black.includes(vertex) || this.boardState.white.includes(vertex);
        if (occupied) {
            alert('Intersection already occupied.');
            return;
        }
        
        this.makeMove(vertex);
    }
    
    async startNewGame() {
        const boardSize = parseInt(document.getElementById('board-size').value);
        const difficulty = parseInt(document.getElementById('difficulty').value);
        const playerColor = document.querySelector('input[name="player-color"]:checked').value;
        
        // Update local state
        this.boardSize = boardSize;
        this.playerColor = playerColor;
        this.computerColor = playerColor === 'black' ? 'white' : 'black';
        this.cellSize = this.canvas.width / (this.boardSize + 1);
        this.stoneRadius = this.cellSize * 0.45;
        this.boardState = { black: [], white: [] };
        this.gameActive = false;
        this.lastMove = null;
        this.moveCount = 0;
        
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
        
        if (!confirm('Are you sure you want to pass?')) return;
        
        await this.makeMove('pass');
    }
    
    async resignGame() {
        if (!this.gameActive || !this.gameId) return;
        
        if (!confirm('Are you sure you want to resign?')) return;
        
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
    
    drawEmptyBoard() {
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const cell = this.cellSize;
        const offset = cell; // margin
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw board background
        ctx.fillStyle = '#dcb35c';
        ctx.fillRect(0, 0, width, height);
        
        // Draw grid lines
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 1;
        
        // Vertical lines
        for (let i = 0; i < this.boardSize; i++) {
            ctx.beginPath();
            ctx.moveTo(offset + i * cell, offset);
            ctx.lineTo(offset + i * cell, offset + (this.boardSize - 1) * cell);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let i = 0; i < this.boardSize; i++) {
            ctx.beginPath();
            ctx.moveTo(offset, offset + i * cell);
            ctx.lineTo(offset + (this.boardSize - 1) * cell, offset + i * cell);
            ctx.stroke();
        }
        
        // Draw star points (hoshi)
        ctx.fillStyle = '#000000';
        const starPoints = this.getStarPoints();
        const starRadius = cell * 0.1;
        
        starPoints.forEach(point => {
            ctx.beginPath();
            ctx.arc(offset + point.x * cell, offset + point.y * cell, starRadius, 0, Math.PI * 2);
            ctx.fill();
        });
        
        // Draw coordinate labels (optional)
        this.drawCoordinateLabels();
    }
    
    getStarPoints() {
        // Standard star point positions for 9x9, 13x13, 19x19
        const points = [];
        const size = this.boardSize;
        
        if (size === 9) {
            const coords = [2, 6];
            for (const x of coords) {
                for (const y of coords) {
                    points.push({ x, y });
                }
            }
            // Center point
            points.push({ x: 4, y: 4 });
        } else if (size === 13) {
            const coords = [3, 9];
            for (const x of coords) {
                for (const y of coords) {
                    points.push({ x, y });
                }
            }
            // Center point
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
    
    drawCoordinateLabels() {
        const ctx = this.ctx;
        const cell = this.cellSize;
        const offset = cell;
        const letters = 'ABCDEFGHJKLMNOPQRST';
        
        ctx.fillStyle = '#000000';
        ctx.font = `${cell * 0.4}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Column letters (top and bottom)
        for (let i = 0; i < this.boardSize; i++) {
            const letter = letters[i];
            // Top
            ctx.fillText(letter, offset + i * cell, offset - cell * 0.6);
            // Bottom
            ctx.fillText(letter, offset + i * cell, offset + (this.boardSize - 1) * cell + cell * 0.6);
        }
        
        // Row numbers (left and right)
        for (let i = 0; i < this.boardSize; i++) {
            const number = this.boardSize - i;
            // Left
            ctx.fillText(number, offset - cell * 0.6, offset + i * cell);
            // Right
            ctx.fillText(number, offset + (this.boardSize - 1) * cell + cell * 0.6, offset + i * cell);
        }
    }
    
    drawBoard() {
        this.drawEmptyBoard();
        
        // Draw stones
        this.boardState.black.forEach(vertex => {
            const pos = this.vertexToBoard(vertex);
            if (pos) this.drawStone(pos.x, pos.y, 'black');
        });
        
        this.boardState.white.forEach(vertex => {
            const pos = this.vertexToBoard(vertex);
            if (pos) this.drawStone(pos.x, pos.y, 'white');
        });
        
        // Highlight last move (if any)
        if (this.lastMove) {
            const pos = this.vertexToBoard(this.lastMove);
            if (pos) this.highlightIntersection(pos.x, pos.y);
        }
    }
    
    drawStone(x, y, color) {
        const ctx = this.ctx;
        const cell = this.cellSize;
        const offset = cell;
        const radius = this.stoneRadius;
        
        ctx.save();
        
        // Stone shadow
        ctx.beginPath();
        ctx.arc(offset + x * cell, offset + y * cell, radius, 0, Math.PI * 2);
        ctx.fillStyle = color === 'black' ? '#000000' : '#ffffff';
        ctx.fill();
        
        // Stone highlight
        if (color === 'black') {
            ctx.beginPath();
            ctx.arc(offset + x * cell - radius * 0.3, offset + y * cell - radius * 0.3, radius * 0.3, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.fill();
        } else {
            ctx.beginPath();
            ctx.arc(offset + x * cell - radius * 0.3, offset + y * cell - radius * 0.3, radius * 0.3, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            ctx.fill();
        }
        
        ctx.restore();
    }
    
    highlightIntersection(x, y) {
        const ctx = this.ctx;
        const cell = this.cellSize;
        const offset = cell;
        
        ctx.save();
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(offset + x * cell, offset + y * cell, this.stoneRadius * 0.7, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
    }
    
    updateUI() {
        // Update player/computer colors
        document.getElementById('player-color').textContent = this.playerColor;
        document.getElementById('player-color').className = `stone ${this.playerColor}-stone`;
        document.getElementById('computer-color').textContent = this.computerColor;
        document.getElementById('computer-color').className = `stone ${this.computerColor}-stone`;
        
        // Update game status
        const gameStatus = document.getElementById('game-status');
        gameStatus.textContent = this.gameActive ? 'Active' : 'Ended';
        gameStatus.className = this.gameActive ? 'status-active' : 'status-ended';
        
        // Update move count
        document.getElementById('move-count').textContent = this.moveCount;
        
        // Update last move
        document.getElementById('last-move').textContent = this.lastMove || 'None';
        
        // Update game ID
        document.getElementById('game-id').textContent = this.gameId || '-';
        
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
        // Update radio button visual
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