from pygame import display, DOUBLEBUF
from pygame import draw

#Constantes
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32


SCREEN_DEPTH = 8


PIXEL_STATES = {
    0: (0, 0, 0, 255),
    1: (250, 250, 250, 255)
}


class Chip8Screen:

    def __init__(self, scale_factor, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        display.init()
        self.surface = display.set_mode((screen_width * scale_factor, screen_height * scale_factor), DOUBLEBUF, SCREEN_DEPTH)
        display.set_caption('CHIP8 Emulator')

    def clear_screen(self):
        self.surface.fill(PIXEL_STATES[0])