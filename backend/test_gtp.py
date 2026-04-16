#!/usr/bin/env python3
"""
Test GNU Go GTP interface.
"""
import subprocess
import time
import sys

def test_gtp():
    # Start gnugo in GTP mode with level 5
    proc = subprocess.Popen(
        ['gnugo', '--mode', 'gtp', '--level', '5'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    def send_command(cmd):
        print(f"> {cmd}")
        proc.stdin.write(cmd + '\n')
        proc.stdin.flush()
        # Read response lines until blank line
        lines = []
        while True:
            line = proc.stdout.readline()
            if line == '\n':
                break
            lines.append(line.rstrip())
        response = '\n'.join(lines)
        print(f"< {response}")
        return response
    
    try:
        # Test basic commands
        send_command('boardsize 9')
        send_command('clear_board')
        send_command('komi 6.5')
        send_command('play black D4')
        send_command('genmove white')
        send_command('showboard')
        send_command('quit')
    finally:
        proc.wait()

if __name__ == '__main__':
    test_gtp()