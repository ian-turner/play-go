#!/usr/bin/env python3
"""
Explore GNU Go GTP commands for scoring and territory.
"""
import sys
sys.path.insert(0, '.')

from gtp import GnuGoGTP

def main():
    engine = GnuGoGTP(level=5, boardsize=9, komi=6.5)
    try:
        # Play a few moves to have something to score
        engine.play('black', 'D4')
        engine.play('white', 'F3')
        engine.play('black', 'E5')
        engine.play('white', 'E4')
        engine.play('black', 'D5')
        engine.play('white', 'F5')
        engine.play('black', 'E6')
        engine.play('white', 'D6')
        engine.play('black', 'C5')
        engine.play('white', 'G5')
        # Pass twice to end game? Actually need two passes.
        engine.play('black', 'pass')
        engine.play('white', 'pass')
        
        print("Board:")
        print(engine.showboard())
        print("\nFinal score:", engine.final_score())
        print("\nEstimate score:", engine.send_command('estimate_score'))
        # final_status with arguments
        for status in ['alive', 'dead', 'seki', 'white_territory', 'black_territory']:
            try:
                lines = engine.send_command(f'final_status {status}')
                print(f"final_status {status}: {lines}")
            except Exception as e:
                print(f"final_status {status}: {e}")
        # final_status_list
        try:
            lines = engine.send_command('final_status_list')
            print(f"final_status_list: {lines}")
        except Exception as e:
            print(f"final_status_list: {e}")
        # unconditional_status
        try:
            lines = engine.send_command('unconditional_status')
            print(f"unconditional_status: {lines}")
        except Exception as e:
            print(f"unconditional_status: {e}")
        # dragon_status
        try:
            lines = engine.send_command('dragon_status')
            print(f"dragon_status: {lines}")
        except Exception as e:
            print(f"dragon_status: {e}")
        # worm_stones
        try:
            lines = engine.send_command('worm_stones')
            print(f"worm_stones: {lines}")
        except Exception as e:
            print(f"worm_stones: {e}")
        # experiment with experimental_score
        try:
            lines = engine.send_command('experimental_score')
            print(f"experimental_score: {lines}")
        except Exception as e:
            print(f"experimental_score: {e}")
        # new_score
        try:
            lines = engine.send_command('new_score')
            print(f"new_score: {lines}")
        except Exception as e:
            print(f"new_score: {e}")
    finally:
        engine.quit()

if __name__ == '__main__':
    main()