from CPU import Chip8Cpu
from pygame import time
if __name__ == '__main__':
    #We need to create the screen first

    #Then we pass the screen to the CPU
    cpu = Chip8Cpu()

    cpu.load_rom("FONTS.chip8", 0x050)
    cpu.load_rom("Chip8Test.rom")

    running = True

    internalClock = time.Clock()

    while running:
        internalClock.tick_busy_loop(60) # Limita la CPU a funcionar a 60Hz
        cpu.execute_instruction()



