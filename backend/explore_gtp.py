#!/usr/bin/env python3
"""
Explore GNU Go GTP commands for scoring.
"""
import sys
sys.path.insert(0, '.')

from gtp import GnuGoGTP

def main():
    engine = GnuGoGTP(level=5, boardsize=9, komi=6.5)
    try:
        # List available commands
        print("Testing list_commands:")
        lines = engine.send_command('list_commands')
        for line in lines:
            print(line)
        print("\nTesting known scoring commands:")
        # Try final_score
        print("final_score:", engine.final_score())
        # Try territory command (if exists)
        try:
            lines = engine.send_command('territory')
            print("territory:", lines)
        except Exception as e:
            print("territory not supported:", e)
        # Try estimate_score
        try:
            lines = engine.send_command('estimate_score')
            print("estimate_score:", lines)
        except Exception as e:
            print("estimate_score not supported:", e)
        # Try initial_influence (maybe)
        try:
            lines = engine.send_command('initial_influence black')
            print("initial_influence black:", lines)
        except Exception as e:
            print("initial_influence not supported:", e)
        # Try dragon_status
        try:
            lines = engine.send_command('dragon_status')
            print("dragon_status:", lines)
        except Exception as e:
            print("dragon_status not supported:", e)
        # Try worm_cutstone (maybe)
        try:
            lines = engine.send_command('worm_cutstone')
            print("worm_cutstone:", lines)
        except Exception as e:
            print("worm_cutstone not supported:", e)
        # Try showscore (maybe)
        try:
            lines = engine.send_command('showscore')
            print("showscore:", lines)
        except Exception as e:
            print("showscore not supported:", e)
    finally:
        engine.quit()

if __name__ == '__main__':
    main()