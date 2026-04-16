# Go Game Web App

A simple web application to play Go against the GNU Go engine.

## Features

- Play against GNU Go engine with adjustable difficulty (1-10)
- Choose board size (9x9, 13x13, 19x19)
- Choose to play as black or white
- Visual board with coordinate labels
- Move log and game status display
- Pass and resign options

## Requirements

- Python 3.8+
- GNU Go (installed via Homebrew on macOS)
- Flask (installed via pip)

## Installation

1. Install GNU Go on macOS:
   ```bash
   brew install gnu-go
   ```
   On Linux, use your package manager (`apt install gnugo`).

2. Clone or download this repository.

3. Set up Python virtual environment and install dependencies:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the Flask server:
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5001
   ```

3. Configure game settings (board size, difficulty, color) and click "New Game".

4. Click on the board to place stones. The computer will respond automatically.

## API Endpoints

The backend provides a REST API:

- `POST /api/game` – Create new game
- `GET /api/game/<game_id>` – Get game state
- `POST /api/game/<game_id>/move` – Make a move
- `POST /api/game/<game_id>/pass` – Pass turn
- `POST /api/game/<game_id>/resign` – Resign game
- `DELETE /api/game/<game_id>` – Delete game

## Project Structure

- `backend/` – Flask application and GTP wrapper
  - `app.py` – Main Flask application
  - `game_manager.py` – Game session management
  - `gtp.py` – GNU Go GTP interface
  - `utils.py` – Coordinate conversion utilities
- `frontend/` – Static web files
  - `index.html` – Main HTML page
  - `style.css` – Styles
  - `app.js` – Frontend JavaScript logic

## Limitations

- No undo functionality
- No persistent storage (games lost on server restart)
- Single player vs computer only
- No scoring interface beyond final score estimate

## Credits

Built with assistance from OpenAI's opencode (DeepSeek Reasoner).

## License

MIT