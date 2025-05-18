# tetris_settings.py (Add these new constants)
import os

import pygame as pg
from pygame.math import Vector2 as vec

FPS = 65 
FIELD_COLOR = (48,39,32)
BG_COLOR = (24,89,117)

# Step 1: Try injected global variable (e.g., Colab)
FONT_PATH = globals().get('FONT_PATH', None)

# Step 2: If not provided, use local PC default
if not FONT_PATH:
    FONT_PATH = 'C:\\Users\\USER\\Desktop\\tomer\\school\\Software Engineering\\Programes\\games\\tetris_game\\FREAKSOFNATUREMASSIVE.ttf'

# Step 3: If the file doesn't exist, use system font
if not os.path.exists(FONT_PATH):
    print("⚠️ Custom font not found — using system fallback.")
    FONT_PATH = None  # Let rendering code handle fallback

ANIM_TIME_INTERVAL = 300
FAST_ANIM_TIME_INTERVAL = 30

TILE_SIZE = 50 
FIELD_SIZE = FIELD_W, FIELD_H = 10,20
FIELD_RES = FIELD_W * TILE_SIZE, FIELD_H * TILE_SIZE

FIELD_SCALE_W, FIELD_SCALE_H = 2.5, 1  

WIN_RES = WIN_W, WIN_H = FIELD_RES[0] * FIELD_SCALE_W, FIELD_RES[1] * FIELD_SCALE_H

INIT_POS_OFFSET = pg.Vector2(FIELD_W // 12, -1)
NEXT_POS_OFFSET = vec(FIELD_W * 1.3 - 3.5, FIELD_H * 0.42)  # Position for the next piece
NEXT_BOX_POS = vec(FIELD_W * 1.3, FIELD_H * 0.42)
HOLD_POS_OFFSET = vec(FIELD_W * 2.1, FIELD_H * 0.42)  # Position for the held piece
HOLD_BOX_POS = vec(FIELD_W * 2.1, FIELD_H * 0.42)    # Position for hold box

MOVE_DIRECTIONS = {'left': vec(-1,0),'right': vec(1,0), 'down': vec(0,1)}

GAME_STATES = {  # New constant
    'MENU': 0,
    'PLAYING': 1,
    'GAME_OVER': 2
}

TETROMINOES = {
    'T': [(0,0),(-1,0),(1,0),(0,-1)],
    'O': [(0,0),(0,-1),(1,0),(1,-1)],
    'J': [(0,0),(-1,0),(0,-1),(0,-2)],
    'L': [(0,0),(1,0),(0,-1),(0,-2)],
    'I': [(0,0),(0,1),(0,-1),(0,-2)],
    'S': [(0,0),(-1,0),(0,-1),(1,-1)],
    'Z': [(0,0),(1,0),(0,-1),(-1,-1)]
    #'A':[(0,0)]
}

TETROMINO_COLORS = {
    'T': 'purple',
    'O': 'yellow',
    'J': 'blue',
    'L': 'orange',
    'I': 'cyan',
    'S': 'green',
    'Z': 'red',
    #'A': 'white' 
}
STAGE_BOARD_SIZES = {
    1: (4, 8),     # Small starting board
    2: (6, 12),    # Medium board
    3: (8, 16),    # Larger board
    4: (10, 18),   # Almost standard
    5: (10, 20)    # Standard Tetris board
}

def update_field_dimensions(width, height):
    global FIELD_W, FIELD_H, FIELD_SIZE, FIELD_RES, WIN_RES, WIN_W, WIN_H
    global INIT_POS_OFFSET, NEXT_POS_OFFSET, HOLD_POS_OFFSET, HOLD_BOX_POS, NEXT_BOX_POS

    FIELD_W = width
    FIELD_H = height
    FIELD_SIZE = FIELD_W, FIELD_H
    FIELD_RES = FIELD_W * TILE_SIZE, FIELD_H * TILE_SIZE

    WIN_RES = WIN_W, WIN_H = FIELD_RES[0] * FIELD_SCALE_W, FIELD_RES[1] * FIELD_SCALE_H

    # Fix: Center tetrominos horizontally on smaller boards
    INIT_POS_OFFSET = pg.Vector2(FIELD_W // 2 - 1, 0)  # Changed from FIELD_W // 2 to center better
    
    # Keep original box position
    NEXT_BOX_POS = vec(FIELD_W * 1.3, FIELD_H * 0.42)
    
    # Adjust tetromino position to be centered in the box
    NEXT_POS_OFFSET = vec(FIELD_W * 1.3 - 0.5, FIELD_H * 0.3) # Adjusted to center tetromino
    
    # Hold positions
    HOLD_POS_OFFSET = vec(FIELD_W * 2, FIELD_H * 0.3) # Also adjust y-coordinate
    HOLD_BOX_POS = vec(FIELD_W * 2, FIELD_H * 0.42)  # Keep box position unchanged

    return WIN_RES

def stage_params(stage:int):
    """
    Return (include_hold, action_limit, allowed_shapes) for the given stage.
    Keeps the logic in ONE place so every module agrees.
    """
    include_hold = stage >= 3                    # Hold is legal only from stage 3
    action_limit = 3 if stage == 1 else (5 if include_hold else 4)

    allowed_shapes = {
        1: ['O'],
        2: ['O', 'I'],
        3: ['O', 'I', 'T'],
        4: ['O', 'I', 'T', 'L']
    }.get(stage, list(TETROMINOES.keys()))       # stage ≥ 5 → full set

    return include_hold, action_limit, allowed_shapes