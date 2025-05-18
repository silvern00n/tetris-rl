from tetris_settings import *
from block import *
import random

class Tetromino:
    def __init__(self, tetris, current=True, held=False, shape=None):
        self.tetris = tetris
        self.current = current
        self.held = held

        # Get the current field dimensions to calculate correct offset
        field_array = self.tetris.field_array
        field_width = len(field_array[0]) if field_array and len(field_array) > 0 else FIELD_W

        # Calculate proper initial offset for current field size
        initial_x = max(0, field_width // 2 - 1)  # Center horizontally
        initial_y = 0  # Start from top

        # Determine the shape: use provided one or pick random
        allowed_shapes = getattr(self.tetris.app, 'allowed_shapes', list(TETROMINOES.keys()))
        self.shape = shape if shape is not None else random.choice(allowed_shapes)
        self.color = TETROMINO_COLORS[self.shape]

        # Create blocks with the calculated offset
        self.blocks = []
        for pos in TETROMINOES[self.shape]:
            # Apply proper offset to each block
            block_pos = vec(pos[0] + initial_x, pos[1] + initial_y)
            self.blocks.append(Block(self, block_pos, self.color))

        self.can_be_held = True

        # Adjust position if needed to ensure all blocks are within bounds
        self._adjust_initial_position()

        # Final collision check
        if any(block.is_collide(block.pos) for block in self.blocks):
            # Try clamping positions to field bounds
            for block in self.blocks:
                block.pos.x = max(0, min(field_width - 1, block.pos.x))
                block.pos.y = max(0, block.pos.y)

            # If still invalid, raise error with debug info
            if any(block.is_collide(block.pos) for block in self.blocks):
                print(f"Field dimensions: {field_width}×{len(field_array)}")
                print(f"Tetromino shape: {self.shape}")
                print(f"Block positions: {[block.pos for block in self.blocks]}")
                raise ValueError("Initial tetromino position is invalid even after adjustment.")

    def _adjust_initial_position(self):
        """Ensure tetromino is within field bounds horizontally"""
        # Get actual field dimensions
        field_array = self.tetris.field_array
        field_width = len(field_array[0]) if field_array and len(field_array) > 0 else FIELD_W
        
        # Check if any blocks are outside field
        min_x = min(block.pos.x for block in self.blocks)
        max_x = max(block.pos.x for block in self.blocks)
        
        # If too far left, move right
        if min_x < 0:
            offset = abs(min_x)
            for block in self.blocks:
                block.pos.x += offset
        
        # If too far right, move left
        elif max_x >= field_width:
            offset = max_x - field_width + 1
            for block in self.blocks:
                block.pos.x -= offset

    def set_seed(seed):
        random.seed(seed)

    def rotate(self):
        pivot_pos = self.blocks[0].pos
        new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]
        if not self.is_collide(new_block_positions):
            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

    def is_collide(self, block_positions):
        for block, pos in zip(self.blocks, block_positions):
            if block.is_collide(pos):
                return True
        return False

    def check_landing(self):
        new_positions = [block.pos + MOVE_DIRECTIONS['down'] for block in self.blocks]
        return self.is_collide(new_positions)

    def move(self, direction):
        move_direction = MOVE_DIRECTIONS[direction]
        new_block_positions = [block.pos + move_direction for block in self.blocks]
        if not self.is_collide(new_block_positions):
            for block in self.blocks:
                block.pos += move_direction

    def update(self):
        if not self.check_landing():
            self.move(direction='down')