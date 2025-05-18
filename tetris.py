from tetris_settings import *
import math
from tetromino import Tetromino
from block import Block

class Tetris:

    def __init__(self, app):
        self.full_lines = 0
        self.lines_last_step = 0
        self.app = app
        self.combo_count = 0
        self.sprite_group = pg.sprite.Group()
        self.grid_surface = pg.Surface(FIELD_RES)
        self.grid_surface.set_colorkey((0, 0, 0))  # Make the surface transparent
        self.draw_grid()

        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.speed_up = False

        self.level = 0
        self.score = 0
        self.lines_to_next_level = 10
        self.points_per_lines = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}

        self.can_hold = True
        self.held_piece = None
        self.hold_sprite_group = pg.sprite.Group()

    def hold_piece(self):
        if not self.can_hold:
            return

        # Save current shape
        current_shape = self.tetromino.shape

        # Remove current piece
        self.remove_current_tetromino()

        if self.held_piece is None:
            # First-time hold
            self.held_piece = current_shape
            self.tetromino = self.next_tetromino
            self.tetromino.current = True
            self.next_tetromino = Tetromino(self, current=False)
        else:
            # Create a new tetromino from the held piece with CORRECT positioning
            new_tetromino = Tetromino(self, current=True, shape=self.held_piece)
            
            # Important fix: RESET the position offset when returning to gameplay
            for block in new_tetromino.blocks:
                block.pos = vec(block.pos.x, block.pos.y)  # Reset to proper game position
                
            # Check if any blocks are above the field and push them down if needed
            min_y = min(block.pos.y for block in new_tetromino.blocks)
            if min_y < 0:
                for block in new_tetromino.blocks:
                    block.pos.y += abs(min_y)
                    
            self.tetromino = new_tetromino
            self.held_piece = current_shape

        self.can_hold = False

        # === FULL CLEANUP OF PREVIOUS HELD BLOCKS ===
        for block in self.hold_sprite_group:
            block.kill()
        self.hold_sprite_group.empty()

        # === Create NEW blocks for visual held piece ===
        for pos in TETROMINOES[self.held_piece]:
            block = pg.sprite.Sprite()
            block.image = pg.Surface([TILE_SIZE, TILE_SIZE])
            color = TETROMINO_COLORS[self.held_piece]
            pg.draw.rect(block.image, color, (1, 1, TILE_SIZE - 2, TILE_SIZE - 2), border_radius=8)

            # Position: use HOLD_POS_OFFSET with proper centering
            block.rect = block.image.get_rect()
            offset_pos = (vec(pos) + HOLD_POS_OFFSET) * TILE_SIZE
            block.rect.topleft = offset_pos

            self.hold_sprite_group.add(block)
            
    def create_tetromino_from_shape(self, shape):
        """
        Helper method to create a new tetromino from the given shape.
        """
        tetromino = Tetromino(self)
        tetromino.shape = shape
        tetromino.color = TETROMINO_COLORS[shape]
        tetromino.blocks = [
            Block(tetromino, pos, tetromino.color) for pos in TETROMINOES[shape]
        ]
        return tetromino

    def remove_current_tetromino(self):
        for block in self.tetromino.blocks:
            block.kill()  # Remove block from the sprite group
            x, y = int(block.pos.x), int(block.pos.y)
            if 0 <= y < FIELD_H:
                self.field_array[y][x] = None  # Clear the field array slot
        self.tetromino.blocks.clear()
        self.sprite_group.update()  # Ensure the sprite group is synchronized

    def spawn_next_tetromino(self):
        if self.app.game_state == GAME_STATES['GAME_OVER']:
            return  # Prevent spawning if the game is over
    
        self.tetromino = self.next_tetromino
        self.tetromino.current = True
    
        try:
            self.next_tetromino = Tetromino(self, current=False)
        except ValueError:
            # Prevent crashing if the next tetromino cannot spawn
            self.app.game_state = GAME_STATES['GAME_OVER']
            return
    
        self.speed_up = False
        self.can_hold = True
    
        # Fix positioning if any part is above the field
        min_y = min(block.pos.y for block in self.tetromino.blocks)
        if min_y < 0:
            shift_down = abs(min_y)
            for block in self.tetromino.blocks:
                block.pos.y += shift_down

    def spawn_held_tetromino(self):
        self.tetromino = Tetromino(self)
        self.tetromino.shape = self.held_piece
        self.tetromino.blocks = [Block(self.tetromino, pos, self.tetromino.color)
                                 for pos in TETROMINOES[self.held_piece]]

    def get_score(self):
        if self.full_lines > 0:
            self.score += self.points_per_lines[self.full_lines] * (self.level + 1)
            self.lines_to_next_level -= self.full_lines
            
            self.lines_last_step = self.full_lines  # Store cleared lines
            self.full_lines = 0
            
            if self.lines_to_next_level <= 0:
                self.level_up()
        else:
            self.lines_last_step = 0  # Reset when no lines cleared

    def check_full_lines(self):
        # Get actual field dimensions
        field_height = len(self.field_array) if self.field_array else 0
        field_width = len(self.field_array[0]) if field_height > 0 else 0
        
        row = field_height - 1
        for y in range(field_height - 1, -1, -1):
            if sum(bool(cell) for cell in self.field_array[y]) < field_width:
                self.field_array[row] = self.field_array[y].copy()
                for block in self.field_array[row]:
                    if block:
                        block.pos.y = row  # Update block position to match array
                row -= 1
            else:
                for block in self.field_array[y]:
                    if block:
                        block.alive = False
                self.field_array[y] = [0] * field_width  # Use actual field width
                self.full_lines += 1
        while row >= 0:
            self.field_array[row] = [0] * field_width  # Use actual field width
            row -= 1

    def put_tetromino_blocks_in_array(self):
        if not hasattr(self, 'tetromino') or not hasattr(self.tetromino, 'blocks'):
            print("Warning: Tetromino or blocks are not properly initialized")
            return
            
        # Get the actual field dimensions from the field_array shape
        field_height = len(self.field_array)
        field_width = len(self.field_array[0]) if field_height > 0 else 0
        
        for block in self.tetromino.blocks:
            if not hasattr(block, 'pos'):
                print(f"Warning: Block has no position attribute")
                continue
                
            try:
                x, y = int(block.pos.x), int(block.pos.y)
                # Use actual field dimensions instead of globals
                if 0 <= x < field_width and 0 <= y < field_height:
                    if not self.field_array[y][x]:
                        self.field_array[y][x] = block
                    # else: silently skip
                else:
                    print(f"Warning: Block at ({x}, {y}) is out of bounds and was skipped. Field size: {field_width}×{field_height}")
            except (ValueError, TypeError) as e:
                print(f"Error processing block position: {e}")
                
        for block in self.tetromino.blocks:
            if not hasattr(block, 'pos'):
                print(f"Warning: Block has no position attribute")
                continue
                
            try:
                x, y = int(block.pos.x), int(block.pos.y)
                if 0 <= x < FIELD_W and 0 <= y < FIELD_H:
                    if not self.field_array[y][x]:
                        self.field_array[y][x] = block
                    # else: silently skip
                else:
                    print(f"Warning: Block at ({x}, {y}) is out of bounds and was skipped.")
            except (ValueError, TypeError) as e:
                print(f"Error processing block position: {e}")

    def get_field_array(self):
        # Get the correct field dimensions from global settings or use app
        if hasattr(self.app, 'field_width') and hasattr(self.app, 'field_height'):
            width = self.app.field_width
            height = self.app.field_height
        else:
            # Fallback to defaults
            width, height = 10, 20
        
        return [[None for _ in range(width)] for _ in range(height)]

    def check_tetromino_landing(self):
        if self.tetromino.check_landing():
            self.put_tetromino_blocks_in_array()
            self.check_full_lines()
            self.get_score()  # This should happen here
            
            if self.full_lines > 0:
                self.combo_count += 1
            else:
                self.combo_count = 0
            
            if self.is_game_over():
                self.app.game_state = GAME_STATES['GAME_OVER']
                return
            
            self.spawn_next_tetromino()

    def control(self, pressed_key):
        if pressed_key == pg.K_LEFT:
            self.tetromino.move(direction='left')
        elif pressed_key == pg.K_RIGHT:
            self.tetromino.move(direction='right')
        elif pressed_key == pg.K_DOWN:
            self.speed_up = True
        elif pressed_key == pg.K_UP:
            self.tetromino.rotate()
        elif pressed_key == pg.K_c:
            self.hold_piece()
            if self.held_piece:
                held_tetromino = Tetromino(self, current=False)
                held_tetromino.shape = self.held_piece
                held_tetromino.color = TETROMINO_COLORS[self.held_piece]
                for block in held_tetromino.blocks:
                    block.pos = block.pos - INIT_POS_OFFSET + HOLD_POS_OFFSET
                    block.image = pg.Surface([TILE_SIZE, TILE_SIZE])
                    pg.draw.rect(block.image, held_tetromino.color, 
                                (1, 1, TILE_SIZE - 2, TILE_SIZE - 2), border_radius=8)
                    self.hold_sprite_group.add(block)

    def release_control(self, released_key):
        if released_key == pg.K_DOWN:
            self.speed_up = False

    def draw(self):
        self.app.screen.blit(self.grid_surface, (0, 0))
        self.sprite_group.draw(self.app.screen)
        self.hold_sprite_group.draw(self.app.screen)

        # Frame around the "Next" display
        next_box_rect = pg.Rect(
            TILE_SIZE * (NEXT_BOX_POS.x -1.5),  # Adjust X position
            TILE_SIZE * (NEXT_BOX_POS.y - 3),  # Adjust Y position
            TILE_SIZE * 5,  # Reduce width from 6 to 5
            TILE_SIZE * 5   # Height of the box
        )
        pg.draw.rect(self.app.screen, 'white', next_box_rect, 2)

        hold_box_rect = pg.Rect(
            TILE_SIZE * (HOLD_BOX_POS.x - 2),
            TILE_SIZE * (HOLD_BOX_POS.y - 3),
            TILE_SIZE * 5,  # Reduce width from 6 to 5
            TILE_SIZE * 5
        )
        pg.draw.rect(self.app.screen, 'white', hold_box_rect, 2)
    
    def update(self):
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self.speed_up]
        if trigger:
            self.tetromino.update()
            self.check_tetromino_landing()
        self.sprite_group.update()
    
    def draw_grid(self):
        self.grid_surface.fill((0, 0, 0))  # Clear previous grid
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pg.draw.rect(self.grid_surface, (96, 96, 96), rect, 1)  # Draw cell borders

        # Add vertical lines
        for x in range(FIELD_W + 1):  # Include one more line for the right edge
            start_pos = (x * TILE_SIZE, 0)
            end_pos = (x * TILE_SIZE, FIELD_H * TILE_SIZE)
            pg.draw.line(self.grid_surface, (96, 96, 96), start_pos, end_pos, 1)

    def reset_game(self):
        # Clear all sprite groups first
        self.sprite_group.empty()
        self.hold_sprite_group.empty()
        
        # Kill all existing tetromino blocks
        if self.tetromino and hasattr(self.tetromino, 'blocks'):
            for block in self.tetromino.blocks:
                block.kill()
        
        if self.next_tetromino and hasattr(self.next_tetromino, 'blocks'):
            for block in self.next_tetromino.blocks:
                block.kill()
        
        # Get actual field dimensions
        field_height = len(self.field_array) if self.field_array else 0
        field_width = len(self.field_array[0]) if field_height > 0 else 0
        
        # Clear field array - properly handle block objects
        if field_height > 0 and field_width > 0:
            for y in range(field_height):
                for x in range(field_width):
                    if self.field_array[y][x] and hasattr(self.field_array[y][x], 'kill'):
                        self.field_array[y][x].kill()
            
            # Clear all cells           
            for y in range(field_height):
                for x in range(field_width):
                    self.field_array[y][x] = None  # Use None instead of a block object
        
        # Create fresh field array
        self.field_array = self.get_field_array()
        
        # Reset tetromino objects with fresh instances
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        
        # Reset game state variables
        self.full_lines = 0
        self.lines_last_step = 0
        self.combo_count = 0
        self.speed_up = False
        
        # Reset scoring
        self.level = 0
        self.score = 0
        self.lines_to_next_level = 10
        
        # Reset hold functionality
        if self.held_piece and hasattr(self.held_piece, 'blocks'):
            for block in self.held_piece.blocks:
                block.kill()
        self.can_hold = True
        self.held_piece = None
        
        # Redraw grid
        self.draw_grid()
        
        # Debug verification (optional)
        field_height = len(self.field_array) if self.field_array else 0
        field_width = len(self.field_array[0]) if field_height > 0 else 0

    def is_game_over(self):
        # Get actual field dimensions
        field_height = len(self.field_array) if self.field_array else 0
        field_width = len(self.field_array[0]) if field_height > 0 else 0
        
        # Check the top 2 rows for blocks (need to ensure we don't exceed actual height)
        max_rows_to_check = min(2, field_height)
        
        for y in range(max_rows_to_check):  # Checks the first N rows
            for x in range(field_width):
                if self.field_array[y][x]:
                    # Set the game state explicitly
                    if hasattr(self, 'app') and hasattr(self.app, 'game_state'):
                        self.app.game_state = GAME_STATES['GAME_OVER']
                    return True  # Game over if any block exists in the top rows
        
        # Ensure the game state is set to PLAYING
        if hasattr(self, 'app') and hasattr(self.app, 'game_state'):
            self.app.game_state = GAME_STATES['PLAYING']
        return False
        
    def level_up(self):
        self.level += 1
        self.lines_to_next_level += 10
        new_interval = max(50, ANIM_TIME_INTERVAL - self.level * 20)
        
        # Check if the app has the user_event attribute before using it
        if hasattr(self.app, 'user_event'):
            pg.time.set_timer(self.app.user_event, new_interval)
        else:
            # For MockApp, we can just skip the timer update since it's not needed for training
            pass