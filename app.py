from tetris_settings import *
import sys
from tetris import Tetris
import pygame as pg
from tetris_text import Text
from menu import Menu
from tetromino import Tetromino
from block import Block

class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption('Tetris')
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.set_timer()
        self.tetris = Tetris(self)
        self.text = Text(self)
        self.menu = Menu(self)
        self.allowed_shapes = list(TETROMINOES.keys())  
        self.game_state = GAME_STATES['MENU']

    def check_event(self):
        self.anim_trigger = False
        self.fast_anim_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if self.game_state == GAME_STATES['PLAYING']:
                    if event.key == pg.K_c:
                        self.tetris.hold_piece()
                    else:
                        self.tetris.control(pressed_key=event.key)
                else:
                    self.menu.handle_input(event)
            elif event.type == self.user_event:
                self.anim_trigger = True
            elif event.type == self.fast_user_event:
                self.fast_anim_trigger = True

    def set_timer(self):
        self.user_event = pg.USEREVENT + 0
        self.fast_user_event = pg.USEREVENT + 1
        self.anim_trigger = False
        self.fast_anim_trigger = False
        pg.time.set_timer(self.user_event, ANIM_TIME_INTERVAL)
        pg.time.set_timer(self.fast_user_event, FAST_ANIM_TIME_INTERVAL)

    def update(self):
        if self.game_state == GAME_STATES['PLAYING']:
            self.tetris.update()
        self.clock.tick(FPS)

    def draw(self):
        self.screen.fill(BG_COLOR)
        if self.game_state == GAME_STATES['PLAYING']:
            self.screen.fill(FIELD_COLOR, rect=(0, 0, *FIELD_RES))
            self.tetris.draw()
            self.text.draw()
        else:
            self.menu.draw()
        pg.display.flip()

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()

    def set_field_dimensions(self, width, height):
        self.field_width = width
        self.field_height = height
        
        # Update global constants
        new_win_res = update_field_dimensions(width, height)
        
        # Resize screen
        self.screen = pg.display.set_mode(new_win_res)
        
        # If game is already initialized, reset it with new dimensions
        if hasattr(self, 'tetris'):
            self.tetris.reset_game()

if __name__ == '__main__':
    app = App()
    app.run()
