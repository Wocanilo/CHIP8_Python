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
        self.scale_factor = scale_factor
        display.init()
        self.surface = display.set_mode((screen_width * scale_factor, screen_height * scale_factor), DOUBLEBUF, SCREEN_DEPTH)
        display.set_caption('CHIP8 Emulator')
        self.clear_screen()
        display.flip()

    def clear_screen(self):
        self.surface.fill(PIXEL_STATES[0])

    def draw_pixel(self, x_pos, y_pos, pixel_state):

        x_base = x_pos * self.scale_factor
        y_base = y_pos * self.scale_factor

        draw.rect(self.surface, PIXEL_STATES[pixel_state], (x_base, y_base, self.scale_factor, self.scale_factor))

    def get_pixel(self, x_pos, y_pos):

        x_scale = x_pos * self.scale_factor
        y_scale = y_pos * self.scale_factor

        if self.surface.get_at((x_scale, y_scale)) == PIXEL_STATES[0]:
            return 0
        else:
            return 1

