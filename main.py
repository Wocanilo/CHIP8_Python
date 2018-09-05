from CPU import Chip8Cpu
from pygame import time
from Screen import Chip8Screen

SCALE_FACTOR  = 10


if __name__ == '__main__':
    #We need to create the screen first
    screen = Chip8Screen(SCALE_FACTOR)
    #Then we pass the screen to the CPU
    cpu = Chip8Cpu()

    cpu.load_rom("FONTS.chip8", 0x050)
    cpu.load_rom("pong.rom")

    running = True

    internalClock = time.Clock()

    while running:
        internalClock.tick_busy_loop(60) # Limita la CPU a funcionar a 60Hz
        if cpu.execute_instruction() == 0x0:
            running = False



