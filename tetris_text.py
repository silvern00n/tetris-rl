import pygame.freetype as ft
from tetris_settings import *

class Text:
    def __init__(self, app):
        self.app = app
        if FONT_PATH:
            self.font = ft.Font(FONT_PATH, size=int(TILE_SIZE * 1.65))
        else:
            # Fallback to a default system font
            self.font = ft.SysFont('Arial', int(TILE_SIZE * 1.65))
            
    def draw_shadowed_text(self, text, pos, fgcolor, bgcolor, size, shadow_offset=(2, 2), shadow_color="black"):
        shadow_pos = (pos[0] + shadow_offset[0], pos[1] + shadow_offset[1])
        self.font.render_to(self.app.screen, shadow_pos, text, fgcolor=shadow_color, size=size)
        self.font.render_to(self.app.screen, pos, text, fgcolor=fgcolor, bgcolor=bgcolor, size=size)

    def draw(self):
        self.draw_shadowed_text(
            "TETRIS:",
            (WIN_W * 0.595, WIN_H * 0.02),
            fgcolor="white",
            bgcolor=None,
            size=TILE_SIZE * 1.65,
            shadow_offset=(3, 3),
        )

        # "Next" Text
        self.draw_shadowed_text(
            "NEXT:",
            (WIN_W * 0.46, WIN_H * 0.18),
            fgcolor="orange",
            bgcolor=None,
            size=TILE_SIZE * 1.4,
            shadow_offset=(2, 2),
        )

        # "Score" Text
        self.draw_shadowed_text(
            "SCORE:",
            (WIN_W * 0.64, WIN_H * 0.70),
            fgcolor="orange",
            bgcolor=None,
            size=TILE_SIZE * 1.4,
            shadow_offset=(2, 2),
        )
        # Score Value
        self.draw_shadowed_text(
            f'{self.app.tetris.score}',
            (WIN_W * 0.64, WIN_H * 0.78),  #
            fgcolor="white",
            bgcolor=None,
            size=TILE_SIZE * 1.8,
            shadow_offset=(3, 3),
        )

        # Level Text
        self.draw_shadowed_text(
            f'lvl: {self.app.tetris.level}',
            (WIN_W * 0.65, WIN_H * 0.58),  # Adjusted slightly down from 0.55
            fgcolor="orange",
            bgcolor=None,
            size=TILE_SIZE * 1.4,
            shadow_offset=(3, 3),
        )
        self.draw_shadowed_text(
            "HOLD:",
            (WIN_W * 0.75, WIN_H * 0.18),
            fgcolor="orange",
            bgcolor=None,
            size=TILE_SIZE * 1.4,
            shadow_offset=(2, 2),
        )