import unittest
from CPU import Chip8Cpu


class CpuTests(unittest.TestCase):


    # Preparamos la CPU para ser usada durante los tests
    def setUp(self):
        self.cpu = Chip8Cpu()

    def test_rom(self):
        # Comprueba si podemos cargar un archivo en memoria correctamente
        self.cpu.load_rom('testRom', 0x100)
        self.assertEqual(ord('a'), self.cpu.memory[0x100])
        self.assertEqual(ord('b'), self.cpu.memory[0x100 + 1])

if __name__ == '__main__':

    unittest.main()