"""
GTP wrapper for GNU Go.
"""
import subprocess
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

class GTPError(Exception):
    """Raised when GTP command returns error."""
    pass

class GnuGoGTP:
    """Interface to GNU Go via GTP protocol."""
    
    def __init__(self, level: int = 10, boardsize: int = 19, komi: float = 6.5):
        """
        Start GNU Go process with GTP mode.
        
        Args:
            level: Strength level (1-10)
            boardsize: Board size (typically 9, 13, 19)
            komi: Komi value
        """
        self.process = subprocess.Popen(
            ['gnugo', '--mode', 'gtp', '--level', str(level)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self._send_command(f'boardsize {boardsize}')
        self._send_command('clear_board')
        self._send_command(f'komi {komi}')
        logger.info(f"GNU Go GTP started with level {level}, boardsize {boardsize}, komi {komi}")
    
    def _send_command(self, command: str) -> Tuple[str, List[str]]:
        """
        Send a GTP command and return response.
        
        Returns:
            (status, lines) where status is '=' or '?' and lines are response lines.
        """
        logger.debug(f"Sending GTP command: {command}")
        self.process.stdin.write(command + '\n')
        self.process.stdin.flush()
        
        # Read response lines until blank line
        lines = []
        while True:
            line = self.process.stdout.readline()
            if line == '\n':
                break
            lines.append(line.rstrip())
        
        # Parse first line for status
        if not lines:
            raise GTPError("Empty response from GNU Go")
        
        first = lines[0]
        if first.startswith('='):
            status = '='
            # Remove status and possible space
            content = first[1:].lstrip()
            if content:
                # If there's content on same line, treat as additional line
                lines[0] = content
            else:
                # Remove empty first line
                lines.pop(0)
        elif first.startswith('?'):
            status = '?'
            error_msg = first[1:].lstrip()
            raise GTPError(f"GTP error: {error_msg}")
        else:
            # Some responses might not follow spec? Assume success.
            status = '='
        
        logger.debug(f"GTP response status: {status}, lines: {lines}")
        return status, lines
    
    def send_command(self, command: str) -> List[str]:
        """Send command and return response lines (without status)."""
        status, lines = self._send_command(command)
        return lines
    
    def play(self, color: str, vertex: str) -> None:
        """Play a stone at vertex (e.g., 'black D4')."""
        self.send_command(f'play {color} {vertex}')
    
    def genmove(self, color: str) -> str:
        """Generate a move for color, returns vertex (e.g., 'E6') or 'pass' or 'resign'."""
        lines = self.send_command(f'genmove {color}')
        if not lines:
            raise GTPError("No response from genmove")
        return lines[0].strip()
    
    def list_stones(self, color: str) -> List[str]:
        """List vertices of stones of given color.
        Returns list of vertex strings (e.g., ['D4', 'E5'])."""
        lines = self.send_command(f'list_stones {color}')
        if not lines:
            return []
        # lines[0] contains space-separated vertices
        vertices = lines[0].split()
        return vertices

    def get_captures(self, color: str) -> int:
        """Get number of stones captured by given color.
        Returns integer count."""
        lines = self.send_command(f'captures {color}')
        if not lines:
            return 0
        # lines[0] should be like '= 5' or just '5'
        # The _send_command strips the '=' prefix, so we get '5'
        try:
            return int(lines[0].strip())
        except ValueError:
            return 0
    
    def showboard(self) -> str:
        """Return board representation as string."""
        lines = self.send_command('showboard')
        return '\n'.join(lines)
    
    def final_score(self) -> str:
        """Get final score (e.g., 'B+3.5')."""
        lines = self.send_command('final_score')
        if not lines:
            return ''
        return lines[0].strip()
    
    def get_scoring(self) -> dict:
        """
        Get detailed scoring information after game ended.
        
        Returns dict with keys:
        - score: final score string
        - black_territory: list of vertices
        - white_territory: list of vertices
        - alive: list of vertices (stones alive)
        - dead: list of vertices (dead stones)
        - seki: list of vertices (seki stones)
        """
        # Ensure game is over? Not required but commands may fail.
        result = {}
        result['score'] = self.final_score()
        for status in ['black_territory', 'white_territory', 'alive', 'dead', 'seki']:
            try:
                lines = self.send_command(f'final_status_list {status}')
                # lines[0] contains space-separated vertices
                if lines:
                    vertices = lines[0].split()
                else:
                    vertices = []
                result[status] = vertices
            except Exception:
                result[status] = []
        return result
    
    def set_boardsize(self, size: int) -> None:
        """Change board size (must be called before clear_board)."""
        self.send_command(f'boardsize {size}')
    
    def clear_board(self) -> None:
        """Clear the board."""
        self.send_command('clear_board')
    
    def set_komi(self, komi: float) -> None:
        """Set komi."""
        self.send_command(f'komi {komi}')
    
    def quit(self) -> None:
        """Terminate GNU Go process."""
        try:
            self.send_command('quit')
        except (GTPError, BrokenPipeError):
            pass
        self.process.terminate()
        self.process.wait()
    
    def __del__(self):
        """Ensure process is terminated on garbage collection."""
        if self.process.poll() is None:
            self.quit()