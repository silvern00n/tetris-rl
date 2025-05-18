from tetris_settings import *
import random

class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, pos, color):
        self.tetromino = tetromino
        # Initialize sprite AFTER setting tetromino to ensure proper group assignment
        super().__init__(self.tetromino.tetris.sprite_group)
        
        self.pos = vec(pos) + INIT_POS_OFFSET
        self.next_pos = vec(pos) + NEXT_POS_OFFSET
        self.hold_pos = vec(pos) + HOLD_POS_OFFSET
        self.color = color
        
        self.image = pg.Surface([TILE_SIZE, TILE_SIZE])
        pg.draw.rect(self.image, color, (1, 1, TILE_SIZE - 2, TILE_SIZE - 2), border_radius=8)
        self.rect = self.image.get_rect()
        self.sfx_image = self.image.copy()
        self.sfx_image.set_alpha(110)
        self.sfx_speed = random.uniform(0.2,0.6)
        self.sfx_cycles = random.randrange(6,8)
        self.cycle_counter = 0
        
        self.alive = True
        self.in_field = True  # New flag to track if block is in play field

    def sfx_end_time(self):
        if self.tetromino.tetris.app.anim_trigger:
            self.cycle_counter +=1
            if self.cycle_counter>self.sfx_cycles:
                self.cycle_counter = 0
                return True

    def sfx_run(self):
        self.image = self.sfx_image
        self.pos.y -= self.sfx_speed
        self.image = pg.transform.rotate(self.image, pg.time.get_ticks() * self.sfx_speed)

    def is_alive(self):
        if not self.alive:
            if not self.sfx_end_time():
                self.sfx_run()
            else:
                self.kill()
            # Make sure block is removed from field array if it's in the field
            if self.in_field:
                tetris = self.tetromino.tetris
                x, y = int(self.pos.x), int(self.pos.y)
                if 0 <= x < FIELD_W and 0 <= y < FIELD_H:
                    if tetris.field_array[y][x] == self:
                        tetris.field_array[y][x] = 0

    def set_rect_pos(self):
        if self.tetromino.held:
            pos = self.hold_pos
        elif self.tetromino.current:
            pos = self.pos
        else:
            pos = self.next_pos

        self.rect.topleft = pos * TILE_SIZE

    def is_collide(self, pos):
        x, y = int(pos.x), int(pos.y)
        
        # Get field dimensions from the tetromino's tetris instance
        field_array = self.tetromino.tetris.field_array
        field_height = len(field_array)
        field_width = len(field_array[0]) if field_height > 0 else 0
        
        # Check bounds using actual field dimensions
        if not (0 <= x < field_width and y < field_height):
            return True
        if y >= 0 and self.tetromino.tetris.field_array[y][x]:
            return True
        return False

    def update(self):
        self.is_alive()
        self.set_rect_pos()

    def rotate(self, pivot_pos):
        translated = self.pos - pivot_pos
        rotated = translated.rotate(90)
        return rotated + pivot_pos