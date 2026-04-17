#!/usr/bin/env python3
"""
Test scoring output after two passes.
"""
import sys
sys.path.insert(0, '.')

from game_manager import GameSession

def test_scoring():
    session = GameSession('test', board_size=9, difficulty=5, player_color='black', komi=6.5)
    try:
        # Manually pass both players (bypass computer move generation)
        session.engine.play('black', 'pass')
        session.engine.play('white', 'pass')
        session.game_over = True
        session.scoring_data = session.engine.get_scoring()
        state = session.get_state()
        print("Game over:", state['game_over'])
        print("Result:", state['result'])
        if 'scoring' in state:
            scoring = state['scoring']
            print("Score:", scoring.get('score'))
            print("Black territory count:", len(scoring.get('black_territory', [])))
            print("White territory count:", len(scoring.get('white_territory', [])))
            print("Alive stones:", scoring.get('alive'))
            print("Dead stones:", scoring.get('dead'))
            print("Seki stones:", scoring.get('seki'))
        else:
            print("No scoring data")
    finally:
        session.destroy()

if __name__ == '__main__':
    test_scoring()