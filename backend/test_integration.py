#!/usr/bin/env python3
"""
Integration test for Flask API with GNU Go.
"""
import subprocess
import time
import requests
import json
import sys
import os

def start_server():
    """Start Flask server in background, return process."""
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(__file__)
    proc = subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=os.path.dirname(__file__),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait for server to start
    time.sleep(3)
    return proc

def test_api():
    base_url = 'http://localhost:5001'
    
    # Test 1: Create game
    print('Creating game...')
    resp = requests.post(f'{base_url}/api/game', json={
        'board_size': 9,
        'difficulty': 5,
        'player_color': 'black'
    })
    assert resp.status_code == 201, f'Create game failed: {resp.status_code} {resp.text}'
    game = resp.json()
    game_id = game['game_id']
    print(f'Game created: {game_id}')
    
    # Test 2: Get game state
    resp = requests.get(f'{base_url}/api/game/{game_id}')
    assert resp.status_code == 200
    print('Game state retrieved')
    
    # Test 3: Make a move
    resp = requests.post(f'{base_url}/api/game/{game_id}/move', json={
        'vertex': 'D4'
    })
    assert resp.status_code == 200, f'Move failed: {resp.status_code} {resp.text}'
    move_result = resp.json()
    print(f'Move result: {move_result}')
    assert move_result['success'] == True
    if move_result.get('computer_move'):
        print(f'Computer responded: {move_result["computer_move"]}')
    
    # Test 4: Pass
    resp = requests.post(f'{base_url}/api/game/{game_id}/pass')
    assert resp.status_code == 200
    print('Pass successful')
    
    # Test 5: Delete game
    resp = requests.delete(f'{base_url}/api/game/{game_id}')
    assert resp.status_code == 200
    print('Game deleted')
    
    print('All tests passed!')
    return True

def main():
    server = start_server()
    try:
        # Give server extra time to start
        time.sleep(2)
        test_api()
    except Exception as e:
        print(f'Test failed: {e}')
        # Read server output for debugging
        stdout, stderr = server.communicate(timeout=2)
        print('Server stdout:', stdout.decode())
        print('Server stderr:', stderr.decode())
        sys.exit(1)
    finally:
        server.terminate()
        server.wait()

if __name__ == '__main__':
    main()