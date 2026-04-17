#!/usr/bin/env python3
"""
Test scoring and territory extraction from GNU Go.
"""
import sys
sys.path.insert(0, '.')

from gtp import GnuGoGTP

def test_scoring():
    engine = GnuGoGTP(level=5, boardsize=9, komi=6.5)
    try:
        # Create a simple board with some dead stones
        # Black stone at D4, white surrounds
        engine.play('black', 'D4')
        engine.play('white', 'E4')
        engine.play('white', 'D5')
        engine.play('white', 'C4')
        engine.play('white', 'D3')
        # Pass twice to end game
        engine.play('black', 'pass')
        engine.play('white', 'pass')
        
        print("Board:")
        print(engine.showboard())
        print("\nFinal score:", engine.final_score())
        
        # Try final_status_list with status
        for status in ['alive', 'dead', 'seki', 'white_territory', 'black_territory']:
            try:
                lines = engine.send_command(f'final_status_list {status}')
                print(f"final_status_list {status}: {lines}")
            except Exception as e:
                print(f"final_status_list {status}: {e}")
        
        # Get list of all vertices
        vertices = []
        for x in range(9):
            for y in range(9):
                # Convert to GTP vertex
                letters = 'ABCDEFGHJKLMNOPQRST'
                col = letters[x]
                row = 9 - y
                vertex = f"{col}{row}"
                vertices.append(vertex)
        
        # Query status of each vertex (slow but for testing)
        print("\nSample vertex statuses:")
        for vertex in vertices[:10]:  # first 10
            try:
                lines = engine.send_command(f'final_status {vertex}')
                print(f"{vertex}: {lines[0] if lines else '?'}")
            except Exception as e:
                print(f"{vertex}: error {e}")
        
        # Try unconditional_status
        try:
            lines = engine.send_command('unconditional_status')
            print(f"\nunconditional_status: {lines}")
        except Exception as e:
            print(f"\nunconditional_status: {e}")
            
        # Try dragon_status
        try:
            lines = engine.send_command('dragon_status')
            print(f"dragon_status: {lines}")
        except Exception as e:
            print(f"dragon_status: {e}")
            
        # Try worm_stones
        try:
            lines = engine.send_command('worm_stones')
            print(f"worm_stones: {lines}")
        except Exception as e:
            print(f"worm_stones: {e}")
            
    finally:
        engine.quit()

if __name__ == '__main__':
    test_scoring()