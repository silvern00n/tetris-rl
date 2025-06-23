import os
import pygame as pg
from pygame.math import Vector2 as vec

# === Game Timing ===
FPS = 65  # Frames per second

# === Colors ===
FIELD_COLOR = (48, 39, 32)  # Color of the Tetris grid background
BG_COLOR = (24, 89, 117)    # General background color

# === Font Configuration ===
# Step 1: Try to get font path from a global variable (e.g., in Colab/Notebook)
FONT_PATH = globals().get('FONT_PATH', None)

# Step 2: If not injected, use local path (Windows-specific example)
if not FONT_PATH:
    FONT_PATH = 'C:\\Users\\USER\\Desktop\\tomer\\school\\Software Engineering\\Programes\\games\\tetris_game\\FREAKSOFNATUREMASSIVE.ttf'

# Step 3: If custom font not found, fall back to system default
if not os.path.exists(FONT_PATH):
    print("⚠️ Custom font not found — using system fallback.")
    FONT_PATH = None

def get_font(size):
    """
    Returns a Pygame font object.
    Tries to use custom font if available, else falls back to a system font.
    """
    if FONT_PATH:
        try:
            return pg.font.Font(FONT_PATH, size)
        except Exception as e:
            print(f"⚠️ Failed to load custom font: {e}. Falling back to system font.")
    return pg.font.SysFont("arial", size)

# === Animation Timing ===
ANIM_TIME_INTERVAL = 300        # Normal drop interval in ms
FAST_ANIM_TIME_INTERVAL = 30    # Fast drop interval (when soft dropping)

# === Board Dimensions ===
TILE_SIZE = 50
FIELD_SIZE = FIELD_W, FIELD_H = 10, 20                         # Default Tetris board size
FIELD_RES = FIELD_W * TILE_SIZE, FIELD_H * TILE_SIZE          # Pixel resolution of the board

FIELD_SCALE_W, FIELD_SCALE_H = 2.5, 1                          # Window scaling factors
WIN_RES = WIN_W, WIN_H = FIELD_RES[0] * FIELD_SCALE_W, FIELD_RES[1] * FIELD_SCALE_H

# === Piece Positions for UI Elements ===
INIT_POS_OFFSET = pg.Vector2(FIELD_W // 12, -1)                 # Offset for piece spawn location
NEXT_POS_OFFSET = vec(FIELD_W * 1.3 - 3.5, FIELD_H * 0.42)      # Offset for "next piece" preview
NEXT_BOX_POS = vec(FIELD_W * 1.3, FIELD_H * 0.42)
HOLD_POS_OFFSET = vec(FIELD_W * 2.1, FIELD_H * 0.42)            # Offset for "held piece"
HOLD_BOX_POS = vec(FIELD_W * 2.1, FIELD_H * 0.42)

# === Movement Directions ===
MOVE_DIRECTIONS = {
    'left': vec(-1, 0),
    'right': vec(1, 0),
    'down': vec(0, 1)
}

# === Game State Constants ===
GAME_STATES = {
    'MENU': 0,
    'PLAYING': 1,
    'GAME_OVER': 2
}

# === Tetromino Definitions ===
# Each shape consists of 4 (x, y) tile offsets relative to its pivot
TETROMINOES = {
    'T': [(0, 0), (-1, 0), (1, 0), (0, -1)],
    'O': [(0, 0), (0, -1), (1, 0), (1, -1)],
    'J': [(0, 0), (-1, 0), (0, -1), (0, -2)],
    'L': [(0, 0), (1, 0), (0, -1), (0, -2)],
    'I': [(0, 0), (0, 1), (0, -1), (0, -2)],
    'S': [(0, 0), (-1, 0), (0, -1), (1, -1)],
    'Z': [(0, 0), (1, 0), (0, -1), (-1, -1)]
}

# === Tetromino Colors (used for rendering) ===
TETROMINO_COLORS = {
    'T': 'purple',
    'O': 'yellow',
    'J': 'blue',
    'L': 'orange',
    'I': 'cyan',
    'S': 'green',
    'Z': 'red'
}

# === Stage-Specific Board Sizes (for progressive difficulty) ===
STAGE_BOARD_SIZES = {
    1: (4, 8),     # Very small board
    2: (6, 12),    # Small-medium board
    3: (8, 16),    # Medium-large board
    4: (10, 18),   # Almost standard
    5: (10, 20)    # Standard size
}

def update_field_dimensions(width, height):
    """
    Dynamically updates global board size and all dependent UI offsets/resolutions.

    Args:
        width (int): New board width.
        height (int): New board height.

    Returns:
        tuple: Updated window resolution (WIN_W, WIN_H).
    """
    global FIELD_W, FIELD_H, FIELD_SIZE, FIELD_RES, WIN_RES, WIN_W, WIN_H
    global INIT_POS_OFFSET, NEXT_POS_OFFSET, HOLD_POS_OFFSET, HOLD_BOX_POS

    old_w, old_h = FIELD_W, FIELD_H
    FIELD_W = width
    FIELD_H = height
    FIELD_SIZE = (FIELD_W, FIELD_H)
    FIELD_RES = (FIELD_W * TILE_SIZE, FIELD_H * TILE_SIZE)

    WIN_RES = WIN_W, WIN_H = FIELD_RES[0] * FIELD_SCALE_W, FIELD_RES[1] * FIELD_SCALE_H

    # Recalculate UI offsets to align with new board dimensions
    INIT_POS_OFFSET = pg.Vector2(FIELD_W // 2 - 1, 0)
    NEXT_POS_OFFSET = vec(FIELD_W * 1.3, FIELD_H * 0.42)
    HOLD_POS_OFFSET = vec(FIELD_W * 2, FIELD_H * 0.42)
    HOLD_BOX_POS = vec(FIELD_W * 2, FIELD_H * 0.42)

    print(f"Updated field dimensions from {old_w}×{old_h} to {FIELD_W}×{FIELD_H}")
    return WIN_RES

def stage_params(stage: int):
    """
    Returns gameplay parameters for a given training stage.

    Args:
        stage (int): Stage index (difficulty level or curriculum step).

    Returns:
        tuple: (include_hold: bool, action_limit: int, allowed_shapes: list[str])
    """
    include_hold = stage >= 3                           # Hold mechanic unlocks at stage 3
    action_limit = 3 if stage == 1 else (5 if include_hold else 4)

    # Control which shapes are available at each stage for progressive complexity
    allowed_shapes = {
        1: ['O'],
        2: ['O', 'I'],
        3: ['O', 'I', 'T'],
        4: ['O', 'I', 'T', 'L']
    }.get(stage, list(TETROMINOES.keys()))              # Stage 5+ uses full shape set

    return include_hold, action_limit, allowed_shapes
