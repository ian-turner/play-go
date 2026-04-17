"""
Game session management.
"""
import uuid
import logging
from typing import Optional, Dict
from gtp import GnuGoGTP
from utils import get_stone_lists

logger = logging.getLogger(__name__)

class GameSession:
    """Represents a single game session."""
    
    def __init__(self, game_id: str, board_size: int = 9, difficulty: int = 5, 
                 player_color: str = 'black', komi: float = 6.5):
        self.game_id = game_id
        self.board_size = board_size
        self.difficulty = difficulty
        self.player_color = player_color
        self.computer_color = 'white' if player_color == 'black' else 'black'
        self.komi = komi
        self.engine = GnuGoGTP(level=difficulty, boardsize=board_size, komi=komi)
        self.game_over = False
        self.result = None
        self.scoring_data = None
        self.move_history = []
        self.captures_black = 0
        self.captures_white = 0
        
        # If player is white, computer makes first move
        if player_color == 'white':
            self._make_computer_move()
    
    def _update_captures(self) -> None:
        """Update capture counts from engine."""
        self.captures_black = self.engine.get_captures('black')
        self.captures_white = self.engine.get_captures('white')
    
    def _make_computer_move(self) -> Optional[str]:
        """Generate computer move, update board, return vertex or None if game over."""
        if self.game_over:
            return None
        try:
            vertex = self.engine.genmove(self.computer_color)
            self._update_captures()
        except Exception as e:
            logger.error(f"Error generating computer move: {e}")
            self.game_over = True
            self.result = f"Error: {e}"
            return None
        
        self.move_history.append(('computer', self.computer_color, vertex))
        
        # Check if move is pass or resign
        if vertex.lower() == 'pass':
            # Could be two passes in a row? We'll handle later
            pass
        elif vertex.lower() == 'resign':
            self.game_over = True
            self.result = f"{self.player_color} wins by resignation"
        else:
            # Normal move
            pass
        
        # Update game over status by checking final score? Not reliable.
        # We'll rely on two passes detection elsewhere.
        return vertex
    
    def make_move(self, vertex: str) -> dict:
        """
        Player makes a move.
        
        Args:
            vertex: GTP vertex (e.g., 'D4'), 'pass', or 'resign'
        
        Returns:
            dict with keys:
                - success: bool
                - computer_move: vertex or None
                - board_state: dict of stones
                - game_over: bool
                - result: str if game over
                - error: str if error
        """
        if self.game_over:
            return {
                'success': False,
                'error': 'Game is over',
                'game_over': True,
                'result': self.result
            }
        
        # Validate vertex format
        if vertex.lower() not in ('pass', 'resign'):
            # Basic validation
            if len(vertex) < 2 or not vertex[0].isalpha() or not vertex[1:].isdigit():
                return {'success': False, 'error': 'Invalid vertex format'}
        
        try:
            self.engine.play(self.player_color, vertex)
            self._update_captures()
        except Exception as e:
            logger.error(f"Error playing move: {e}")
            return {'success': False, 'error': str(e)}
        
        self.move_history.append(('player', self.player_color, vertex))
        
        # Check for resignation
        if vertex.lower() == 'resign':
            self.game_over = True
            self.result = f"{self.computer_color} wins by resignation"
            board_state = get_stone_lists(self.engine, self.board_size)
            return {
                'success': True,
                'computer_move': None,
                'board_state': board_state,
                'game_over': True,
                'result': self.result,
                'captures_black': self.captures_black,
                'captures_white': self.captures_white
            }
        
        # Generate computer response if not pass? Actually even after pass, we might let computer pass.
        computer_vertex = None
        if not self.game_over:
            computer_vertex = self._make_computer_move()
        
        board_state = get_stone_lists(self.engine, self.board_size)
        
        # Check for two passes in a row (simple detection)
        if (vertex.lower() == 'pass' and computer_vertex and computer_vertex.lower() == 'pass'):
            self.game_over = True
            try:
                score = self.engine.final_score()
                self.result = f"Game ended. Score: {score}"
                self.scoring_data = self.engine.get_scoring()
            except Exception:
                self.result = "Game ended by two passes."
                self.scoring_data = {}
        
        return {
            'success': True,
            'computer_move': computer_vertex,
            'board_state': board_state,
            'game_over': self.game_over,
            'result': self.result,
            'captures_black': self.captures_black,
            'captures_white': self.captures_white
        }
    
    def get_state(self) -> dict:
        """Return current game state."""
        board_state = get_stone_lists(self.engine, self.board_size)
        state = {
            'game_id': self.game_id,
            'board_size': self.board_size,
            'komi': self.komi,
            'difficulty': self.difficulty,
            'player_color': self.player_color,
            'computer_color': self.computer_color,
            'board_state': board_state,
            'game_over': self.game_over,
            'result': self.result,
            'move_count': len(self.move_history),
            'captures_black': self.captures_black,
            'captures_white': self.captures_white
        }
        if self.game_over and self.scoring_data is not None:
            state['scoring'] = self.scoring_data
        return state
    
    def resign(self) -> None:
        """Player resigns."""
        self.game_over = True
        self.result = f"{self.computer_color} wins by resignation"
    
    def pass_turn(self) -> dict:
        """Player passes. Returns same as make_move('pass')."""
        return self.make_move('pass')
    
    def destroy(self):
        """Clean up resources."""
        self.engine.quit()


class GameManager:
    """Manages active game sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
    
    def create_game(self, board_size: int = 9, difficulty: int = 5, 
                    player_color: str = 'black', komi: float = 6.5) -> str:
        """Create a new game session and return its ID."""
        game_id = str(uuid.uuid4())
        session = GameSession(game_id, board_size, difficulty, player_color, komi)
        self.sessions[game_id] = session
        logger.info(f"Created game {game_id}")
        return game_id
    
    def get_game(self, game_id: str) -> Optional[GameSession]:
        """Retrieve game session by ID."""
        return self.sessions.get(game_id)
    
    def delete_game(self, game_id: str) -> bool:
        """Delete game session."""
        session = self.sessions.pop(game_id, None)
        if session:
            session.destroy()
            logger.info(f"Deleted game {game_id}")
            return True
        return False
    
    def cleanup(self):
        """Clean up all sessions."""
        for session in self.sessions.values():
            session.destroy()
        self.sessions.clear()


# Global instance
game_manager = GameManager()