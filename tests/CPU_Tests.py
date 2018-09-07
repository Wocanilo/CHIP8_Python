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

    def test_skip_if_vx_equals_nn(self):
        self.cpu.opcode = 0x3c21
        self.cpu.registers['v'][0xc] = 0x21
        self.cpu.skip_if_vx_equals_nn()
        self.assertEqual(self.cpu.registers['pc'], 0x202)

    def test_skip_if_vx_not_equals_nn(self):
        self.cpu.opcode = 0x4222
        self.cpu.skip_if_vx_not_equals_nn()
        self.assertEqual(self.cpu.registers['pc'], 0x202)

    def test_skip_if_vx_equals_vy(self):
        self.cpu.opcode = 0x5c20
        self.cpu.registers['v'][0xc] = 0x23
        self.cpu.registers['v'][0x2] = 0x23
        self.cpu.skip_if_vx_equals_vy()
        self.assertEqual(self.cpu.registers['pc'], 0x202)

    def test_skip_if_vx_not_equals_vy(self):
        self.cpu.opcode = 0x92f0
        self.cpu.registers['v'][0x2] = 22
        self.cpu.skip_if_vx_not_equals_vy()
        self.assertEqual(self.cpu.registers['pc'], 0x202)

    def test_jump_to_address_plus_v0(self):
        self.cpu.opcode = 0xB400
        self.cpu.registers['v'][0] = 0x21
        self.cpu.jump_to_address()
        self.assertEqual(self.cpu.registers['pc'], 0x421)

    def test_set_vx_bitwise_random(self):
        self.cpu.opcode = 0xC022
        self.cpu.set_vx_bitwise_random()

        self.cpu.opcode = 0xC122
        self.cpu.set_vx_bitwise_random()

        self.assertNotEqual(self.cpu.registers['v'][0], self.cpu.registers['v'][1])

    def test_set_vx_to_vy(self):
        self.cpu.opcode = 0x8230
        self.cpu.set_vx_to_vy()
        self.assertEqual(self.cpu.registers['v'][0x2], self.cpu.registers['v'][0x3])

if __name__ == '__main__':

    unittest.main()