import unittest
from CPU import Chip8Cpu
import numpy

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
        self.assertEqual(0x402, self.cpu.registers['pc'])

    def test_vx_to_nn(self):
        self.cpu.opcode = 0x6b01
        self.cpu.set_vx_to_nn()
        self.assertEqual(0x1, self.cpu.registers['v'][0xb])

    def test_skip_if_vx_equals_nn(self):
        self.cpu.opcode = 0x3c21
        self.cpu.registers['v'][0xc] = 0x21
        self.cpu.skip_if_vx_equals_nn()
        self.assertEqual(0x202, self.cpu.registers['pc'])

    def test_skip_if_vx_not_equals_nn(self):
        self.cpu.opcode = 0x4222
        self.cpu.skip_if_vx_not_equals_nn()
        self.assertEqual(0x202, self.cpu.registers['pc'])

    def test_skip_if_vx_equals_vy(self):
        self.cpu.opcode = 0x5c20
        self.cpu.registers['v'][0xc] = 0x23
        self.cpu.registers['v'][0x2] = 0x23
        self.cpu.skip_if_vx_equals_vy()
        self.assertEqual(0x202, self.cpu.registers['pc'])

    def test_skip_if_vx_not_equals_vy(self):
        self.cpu.opcode = 0x92f0
        self.cpu.registers['v'][0x2] = 22
        self.cpu.skip_if_vx_not_equals_vy()
        self.assertEqual(0x202, self.cpu.registers['pc'])

    def test_jump_to_address_plus_v0(self):
        self.cpu.opcode = 0xB400
        self.cpu.registers['v'][0] = 0x21
        self.cpu.jump_to_address()
        self.assertEqual(0x421, self.cpu.registers['pc'])

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

    def test_set_vx_to_vx_or_vy(self):
        self.cpu.opcode = 0x8013
        self.cpu.registers['v'][0x0] = numpy.uint8(0x22)
        self.cpu.registers['v'][0x1] = numpy.uint8(0x54)

        self.cpu.set_vx_to_vx_or_vy()
        self.assertEqual(0x76, self.cpu.registers['v'][0x0])

    def test_set_vx_and_vx_or_vy(self):
        self.cpu.opcode = 0x8013
        self.cpu.registers['v'][0x0] = numpy.uint8(0x22)
        self.cpu.registers['v'][0x1] = numpy.uint8(0x25)

        self.cpu.set_vx_to_vx_and_vy()
        self.assertEqual(0x20, self.cpu.registers['v'][0x0])

    def test_set_vx_and_vx_xor_vy(self):
        self.cpu.opcode = 0x8013
        self.cpu.registers['v'][0x0] = numpy.uint8(0x22)
        self.cpu.registers['v'][0x1] = numpy.uint8(0x25)

        self.cpu.set_vx_to_vx_xor_vy()
        self.assertEqual(0x7, self.cpu.registers['v'][0x0])

    def test_add_nn_to_vx_no_flag(self):
        self.cpu.opcode = 0x7c23
        self.cpu.registers['v'][0xc] = numpy.uint8(0xff)
        self.cpu.add_nn_to_vx_no_flag()
        self.assertEqual(0x22, self.cpu.registers['v'][0xc])

    def test_add_vy_to_vx(self):
        self.cpu.opcode = 0x8234

        self.cpu.registers['v'][0x2] = numpy.uint8(0x23)
        self.cpu.registers['v'][0x3] = numpy.uint8(0x25)
        self.cpu.add_vy_to_vx()

        self.assertEqual(0x48, self.cpu.registers['v'][0x2])
        self.assertEqual(0, self.cpu.registers['v'][0xf])

        self.cpu.registers['v'][0x2] = numpy.uint8(0xff)
        self.cpu.add_vy_to_vx()

        self.assertEqual(0x24, self.cpu.registers['v'][0x2])
        self.assertEqual(1, self.cpu.registers['v'][0xf])

    def test_subtract_vx_minus_vy(self):
        self.cpu.opcode = 0x8235

        self.cpu.registers['v'][0x2] = numpy.uint8(0x0)
        self.cpu.registers['v'][0x3] = numpy.uint8(0x1)
        self.cpu.subtract_vx_minus_vy()

        self.assertEqual(0xff, self.cpu.registers['v'][0x2])
        self.assertEqual(1, self.cpu.registers['v'][0xf])

        self.cpu.registers['v'][0x2] = numpy.uint8(0xff)
        self.cpu.subtract_vx_minus_vy()

        self.assertEqual(0xfe, self.cpu.registers['v'][0x2])
        self.assertEqual(0, self.cpu.registers['v'][0xf])

    def test_subtract_vy_minus_vx(self):
        self.cpu.opcode = 0x8235

        self.cpu.registers['v'][0x2] = numpy.uint8(0x0)
        self.cpu.registers['v'][0x3] = numpy.uint8(0x1)
        self.cpu.subtract_vy_minus_vx()

        self.assertEqual(0x1, self.cpu.registers['v'][0x2])
        self.assertEqual(0, self.cpu.registers['v'][0xf])

        self.cpu.registers['v'][0x2] = numpy.uint8(0xff)
        self.cpu.subtract_vy_minus_vx()

        self.assertEqual(0x2, self.cpu.registers['v'][0x2])
        self.assertEqual(1, self.cpu.registers['v'][0xf])

    def test_store_least_bit_right_shift(self):
        self.cpu.opcode = 0x8006

        self.cpu.registers['v'][0x0] = numpy.uint8(0x23)
        self.cpu.store_least_bit_right_shift()
        self.assertEqual(0x11, self.cpu.registers['v'][0x0])
        self.assertEqual(0x3, self.cpu.registers['v'][0xf])

    def test_store_most_bit_left_shift(self):
        self.cpu.opcode = 0x8006

        self.cpu.registers['v'][0x0] = numpy.uint8(0x23)
        self.cpu.store_most_bit_left_shift()
        self.assertEqual(0x46, self.cpu.registers['v'][0x0])
        self.assertEqual(0x2, self.cpu.registers['v'][0xf])


if __name__ == '__main__':

    unittest.main()