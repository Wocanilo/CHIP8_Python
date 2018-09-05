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

    def test_jump_to_address(self):
        self.cpu.opcode = 0x1402
        self.cpu.jump_to_address()
        self.assertEqual(self.cpu.registers['pc'], 0x0402)

    def test_vx_to_nn(self):
        self.cpu.opcode = 0x6b01
        self.cpu.set_vx_to_nn()
        self.assertEqual(self.cpu.registers['v'][0xb], 0x01)

    def test_if_vx_equals_nn(self):
        self.cpu.opcode = 0x3c21
        self.cpu.registers['v'][0xc] = 0x21
        self.cpu.skip_if_vx_equals_nn()
        self.assertEqual(self.cpu.registers['pc'], 0x202)

if __name__ == '__main__':

    unittest.main()