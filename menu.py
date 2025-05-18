import pygame as pg
from tetris import Tetris
from tetris_settings import *
import pygame.freetype as ft
import sys

class Menu:
    def __init__(self, app):
        self.app = app
        self.font = ft.Font(FONT_PATH)
        self.buttons = {
            'MENU': [
                {'text': 'START GAME', 'pos': (WIN_W * 0.5, WIN_H * 0.4), 'action': self.start_game},
                {'text': 'QUIT', 'pos': (WIN_W * 0.5, WIN_H * 0.5), 'action': self.quit_game}
            ],
            'GAME_OVER': [
                {'text': 'PLAY AGAIN', 'pos': (WIN_W * 0.5, WIN_H * 0.4), 'action': self.start_game},
                {'text': 'QUIT', 'pos': (WIN_W * 0.5, WIN_H * 0.5), 'action': self.quit_game}
            ]
        }
        self.selected_button = 0

    def draw_button(self, text, pos, selected=False):
        color = 'yellow' if selected else 'white'
        text_surf, text_rect = self.font.render(text, size=TILE_SIZE)
        text_rect.center = pos
        self.app.screen.blit(text_surf, text_rect)

    def draw(self):
        self.app.screen.fill(BG_COLOR)
        current_buttons = self.buttons[
            'GAME_OVER' if self.app.game_state == GAME_STATES['GAME_OVER'] else 'MENU'
        ]

        # Draw title
        title = 'GAME OVER' if self.app.game_state == GAME_STATES['GAME_OVER'] else 'TETRIS'
        title_surf, title_rect = self.font.render(title, size=TILE_SIZE * 2)
        title_rect.center = (WIN_W * 0.5, WIN_H * 0.2)
        self.app.screen.blit(title_surf, title_rect)

        # Draw score if game over
        if self.app.game_state == GAME_STATES['GAME_OVER']:
            score_text = f'SCORE: {self.app.tetris.score}'
            score_surf, score_rect = self.font.render(score_text, size=TILE_SIZE)
            score_rect.center = (WIN_W * 0.5, WIN_H * 0.3)
            self.app.screen.blit(score_surf, score_rect)

        # Draw buttons
        for i, button in enumerate(current_buttons):
            self.draw_button(button['text'], button['pos'], i == self.selected_button)

    def start_game(self):
        self.app.game_state = GAME_STATES['PLAYING']
        self.app.tetris = Tetris(self.app)

    def quit_game(self):
        pg.quit()
        sys.exit()

    def handle_input(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                self.selected_button = (self.selected_button - 1) % len(self.buttons[
                    'GAME_OVER' if self.app.game_state == GAME_STATES['GAME_OVER'] else 'MENU'
                ])
            elif event.key == pg.K_DOWN:
                self.selected_button = (self.selected_button + 1) % len(self.buttons[
                    'GAME_OVER' if self.app.game_state == GAME_STATES['GAME_OVER'] else 'MENU'
                ])
            elif event.key == pg.K_RETURN:
                current_buttons = self.buttons[
                    'GAME_OVER' if self.app.game_state == GAME_STATES['GAME_OVER'] else 'MENU'
                ]
                current_buttons[self.selected_button]['action']()
