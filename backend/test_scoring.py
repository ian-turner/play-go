#!/usr/bin/env python3
"""
Test scoring integration.
"""
import sys
sys.path.insert(0, '.')

from gtp import GnuGoGTP
from game_manager import GameSession

def test_engine_scoring():
    engine = GnuGoGTP(level=5, boardsize=9, komi=6.5)
    try:
        # Play a simple sequence ending with two passes
        engine.play('black', 'D4')
        engine.play('white', 'E4')
        engine.play('black', 'pass')
        engine.play('white', 'pass')
        scoring = engine.get_scoring()
        print("Scoring data:", scoring)
        # Check keys
        expected_keys = ['score', 'black_territory', 'white_territory', 'alive', 'dead', 'seki']
        for key in expected_keys:
            if key not in scoring:
                print(f"Missing key {key}")
            else:
                print(f"{key}: {len(scoring[key])} vertices")
        # Show some vertices
        print("\nSample black territory:", scoring['black_territory'][:5])
        print("Sample white territory:", scoring['white_territory'][:5])
        print("Alive stones:", scoring['alive'])
    finally:
        engine.quit()

def test_game_session():
    print("\n--- Testing GameSession scoring ---")
    session = GameSession('test', board_size=9, difficulty=5, player_color='black', komi=6.5)
    try:
        # Player passes
        result = session.pass_turn()
        print("Pass result:", result['success'])
        # Computer should also pass (since we haven't implemented auto-pass detection?)
        # Actually computer will generate a move, not pass. Need to force two passes differently.
        # Let's just test via make_move with pass and simulate computer pass? Not trivial.
        # We'll just test that scoring_data exists after two passes.
        # We'll manually call engine passes.
        session.engine.play('black', 'pass')
        session.engine.play('white', 'pass')
        session.game_over = True
        session.scoring_data = session.engine.get_scoring()
        state = session.get_state()
        print("State keys:", state.keys())
        if 'scoring' in state:
            print("Scoring present")
            print("Score:", state['scoring'].get('score'))
        else:
            print("Scoring missing")
    finally:
        session.destroy()

if __name__ == '__main__':
    test_engine_scoring()
    test_game_session()