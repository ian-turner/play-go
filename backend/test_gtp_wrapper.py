#!/usr/bin/env python3
"""Test GTP wrapper."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from gtp import GnuGoGTP, GTPError

def test_basic():
    print("Starting GNU Go...")
    engine = GnuGoGTP(level=5, boardsize=9, komi=6.5)
    try:
        print("Playing black D4...")
        engine.play('black', 'D4')
        print("Generating white move...")
        move = engine.genmove('white')
        print(f"White plays: {move}")
        board = engine.showboard()
        print("Board:")
        print(board)
        score = engine.final_score()
        print(f"Final score: {score}")
        print("Clearing board...")
        engine.clear_board()
        print("Testing invalid move...")
        try:
            engine.play('black', 'Z99')
        except GTPError as e:
            print(f"Expected error caught: {e}")
        print("Success!")
    finally:
        engine.quit()

if __name__ == '__main__':
    test_basic()