"""
Utility functions for Go board coordinates.
"""
import string

def index_to_vertex(x: int, y: int, boardsize: int) -> str:
    """
    Convert zero-indexed coordinates to GTP vertex.
    x is column (0 left), y is row (0 bottom).
    Returns vertex like 'D4'.
    """
    # GTP uses letters A-T skipping I
    letters = 'ABCDEFGHJKLMNOPQRST'
    if x < 0 or x >= boardsize or y < 0 or y >= boardsize:
        raise ValueError(f"Coordinates ({x},{y}) out of bounds for size {boardsize}")
    # Row number is from bottom (1-indexed)
    row = boardsize - y
    col_letter = letters[x]
    return f"{col_letter}{row}"

def vertex_to_index(vertex: str, boardsize: int) -> tuple[int, int]:
    """
    Convert GTP vertex to zero-indexed coordinates (x, y).
    x is column (0 left), y is row (0 bottom).
    """
    # vertex format like 'D4' or 'pass' or 'resign'
    if vertex.lower() in ('pass', 'resign'):
        raise ValueError(f"Vertex '{vertex}' is not a coordinate")
    
    col_letter = vertex[0].upper()
    row_str = vertex[1:]
    try:
        row = int(row_str)
    except ValueError:
        raise ValueError(f"Invalid vertex: {vertex}")
    
    letters = 'ABCDEFGHJKLMNOPQRST'
    if col_letter not in letters:
        raise ValueError(f"Invalid column letter: {col_letter}")
    x = letters.index(col_letter)
    if x >= boardsize:
        raise ValueError(f"Column {col_letter} out of bounds for size {boardsize}")
    
    # Row number is from bottom
    y = boardsize - row
    if y < 0 or y >= boardsize:
        raise ValueError(f"Row {row} out of bounds for size {boardsize}")
    
    return x, y

def get_stone_lists(engine, boardsize: int) -> dict:
    """
    Query engine for lists of black and white stones.
    Returns dict with keys 'black' and 'white', each a list of vertices.
    """
    black = engine.list_stones('black')
    white = engine.list_stones('white')
    return {'black': black, 'white': white}