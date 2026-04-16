"""
Flask web app for Go game.
"""
import logging
import os
from flask import Flask, request, jsonify, send_from_directory
from game_manager import game_manager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
logger.debug(f"Static folder: {app.static_folder}, absolute: {os.path.abspath(app.static_folder)}")

@app.route('/')
def index():
    """Serve the main frontend page."""
    logger.debug(f"Serving index from {app.static_folder}")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/game', methods=['POST'])
def create_game():
    """Create a new game."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    board_size = data.get('board_size', 9)
    difficulty = data.get('difficulty', 5)
    player_color = data.get('player_color', 'black')
    komi = data.get('komi', 6.5)
    
    # Validate
    if board_size not in (9, 13, 19):
        return jsonify({'error': 'Board size must be 9, 13, or 19'}), 400
    if difficulty < 1 or difficulty > 10:
        return jsonify({'error': 'Difficulty must be between 1 and 10'}), 400
    if player_color not in ('black', 'white'):
        return jsonify({'error': 'Player color must be black or white'}), 400
    
    try:
        game_id = game_manager.create_game(
            board_size=board_size,
            difficulty=difficulty,
            player_color=player_color,
            komi=komi
        )
        session = game_manager.get_game(game_id)
        state = session.get_state()
        return jsonify(state), 201
    except Exception as e:
        logger.error(f"Error creating game: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/game/<game_id>', methods=['GET'])
def get_game(game_id):
    """Get game state."""
    session = game_manager.get_game(game_id)
    if not session:
        return jsonify({'error': 'Game not found'}), 404
    
    state = session.get_state()
    return jsonify(state)

@app.route('/api/game/<game_id>/move', methods=['POST'])
def make_move(game_id):
    """Make a move."""
    session = game_manager.get_game(game_id)
    if not session:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    vertex = data.get('vertex')
    if not vertex:
        return jsonify({'error': 'Missing vertex'}), 400
    
    result = session.make_move(vertex)
    if not result.get('success'):
        return jsonify({'error': result.get('error', 'Move failed')}), 400
    
    # Include game state in response
    result['game_state'] = session.get_state()
    return jsonify(result)

@app.route('/api/game/<game_id>/pass', methods=['POST'])
def pass_move(game_id):
    """Pass turn."""
    session = game_manager.get_game(game_id)
    if not session:
        return jsonify({'error': 'Game not found'}), 404
    
    result = session.pass_turn()
    if not result.get('success'):
        return jsonify({'error': result.get('error', 'Pass failed')}), 400
    
    result['game_state'] = session.get_state()
    return jsonify(result)

@app.route('/api/game/<game_id>/resign', methods=['POST'])
def resign(game_id):
    """Resign game."""
    session = game_manager.get_game(game_id)
    if not session:
        return jsonify({'error': 'Game not found'}), 404
    
    session.resign()
    state = session.get_state()
    return jsonify(state)

@app.route('/api/game/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    """Delete game."""
    if game_manager.delete_game(game_id):
        return jsonify({'message': 'Game deleted'}), 200
    else:
        return jsonify({'error': 'Game not found'}), 404

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)