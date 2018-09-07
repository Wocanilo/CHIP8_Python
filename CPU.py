# CHIP8 CPU


from Config import MAX_MEMORY, PROGRAM_COUNTER_START, DEBUG
from os import urandom
from random import seed, randint
import numpy


class Chip8Cpu:

    def __init__(self):

        # Existen 16 registros de proposito general (V0-VF).
        # VF se encuentra reservado como marca para algunas instrucciones
        # I suele almacenar direcciones de memorias cuyos datos van a ser accedidos por la CPU
        # Stack permite almacenar el puntero de instrucciones (pc) cuando se realizan saltos, llamadas a subrutinas...
        # SP permite almacenar el nivel en el que se encuentrra el ultimo puntero de instrucciones almacenado.

        self.registers = {
            'v': [numpy.uint8(0)] * 16,
            'I': 0,
            'pc': PROGRAM_COUNTER_START,  # O tal vez 0?
            'stack': [0] * 16,
            'sp': 0
        }

        # Ambos llevan a cabo una cuenta regresiva a 60Hz hasta llegar a 0
        # delay_timer: controla los eventos de los juegos
        # sound_timer: si su valor es distinto de cero se produce un pitido

        self.timers = {
            'delay_timer': 0,
            'sound_timer': 0
        }

        # Debemos divir los OPCODES segun el tipo de operacion y construir diccionarios que 'traduzcan' el codigo

        self.general_opcode_lookup = {
            0x0: self.clear_or_end_subroutine,
            0x1: self.jump_to_address,
            0x2: self.call_subroutine,
            0x3: self.skip_if_vx_equals_nn,
            0x4: self.skip_if_vx_not_equals_nn,
            0x5: self.skip_if_vx_equals_vy,
            0x6: self.set_vx_to_nn,
            0x7: self.add_nn_to_vx_no_flag,
            0x8: self.execute_logic_instruction,
            0x9: self.skip_if_vx_not_equals_vy,
            0xA: self.set_i_to_address,
            0xB: self.jump_to_address,
            0xC: self.set_vx_bitwise_random
        }

        self.logic_opcode_lookup = {
            0x0: self.set_vx_to_vy,
            0x1: self.set_vx_to_vx_or_vy,
            0x2: self.set_vx_to_vx_and_vy,
            0x3: self.set_vx_to_vx_xor_vy
        }

        self.opcode = 0
        self.memory = bytearray(MAX_MEMORY)
        seed(urandom(20))

    def load_rom(self, rom, offset=PROGRAM_COUNTER_START):
        """
        Carga un archivo en memoria a partir del lugar indicado

        :param rom: el nombre del archivo a cargar
        :param offset: la ubicación de memoria donde empezar a cargar el archivo

        """
        with open(rom, "rb") as file_data:
            # Enumerate nos permite iterar sobre un objeto mientras mantenemos un contador del bucle actual
            for index, val in enumerate(file_data.read()):  # Is a .read() needed?
                self.memory[index + offset] = val

    def execute_instruction(self):
        """
        Obtiene la siguiente instrucción de la memoria y lo ejecuta

        :return: OPCODE
        """
        # Cada instruccion está formada por 2 bytes. Cada byte está formado por 8 bits.
        # Debemos desplazar el valor del primer byte 8 puestos a la izq. para luego realizar un OR sobre ambos bytes
        instruction = self.memory[self.registers['pc']] << 8 | self.memory[self.registers['pc'] + 1]

        self.registers['pc'] = self.registers['pc'] + 2

        if DEBUG:
            print("Proxima instruccion: " + hex(instruction))
            print("Direccion actual del programa: " + str(self.registers['pc']))

        self.opcode = instruction
        instruction = (instruction & 0xF000) >> 12
        try:
            self.general_opcode_lookup[instruction]()
        except KeyError:
            print("ERROR. OpCode: " + hex(self.opcode) + " Not found in general lookup table.")

        return self.opcode

    def execute_logic_instruction(self):
        instruction = self.opcode & 0x000F
        try:
            self.logic_opcode_lookup[instruction]()
        except KeyError:
            print("ERROR. OpCode: " + hex(self.opcode) + " Not found in logical lookup table.")


    def jump_to_address(self):
        """
        Salta a la dirección de memoria especificada por los últimos 3 bits de la instrucción
        """
        if (self.opcode & 0xF000) >> 12 == 0xB:
            self.registers['pc'] = (self.opcode & 0x0FFF) + self.registers['v'][0]
        else:
            self.registers['pc'] = self.opcode & 0x0FFF

    def set_vx_to_nn(self):
        """
        Establece el valor de Vx a nn
        """
        register_to_set = (self.opcode & 0x0F00) >> 8
        value_to_set = (self.opcode & 0x00FF)
        self.registers['v'][register_to_set] = numpy.uint8(value_to_set)

    def skip_if_vx_equals_nn(self):
        """
        Si Vx es igual a nn saltamos la siguiente instrucción
        """
        register_to_check = (self.opcode & 0x0F00) >> 8
        value_to_check = (self.opcode & 0x00FF)

        if self.registers['v'][register_to_check] == value_to_check:
            self.registers['pc'] = self.registers['pc'] + 2

    def skip_if_vx_not_equals_nn(self):
        """
        Si Vx es desigual a nn saltamos la siguiente instrucción.
        """
        register_to_check = (self.opcode & 0x0F00) >> 8
        value_to_check = (self.opcode & 0x00FF)

        if self.registers['v'][register_to_check] != value_to_check:
            self.registers['pc'] = self.registers['pc'] + 2

    def skip_if_vx_equals_vy(self):
        """
        Si Vx es igual a Vy saltamos la siguiente instrucción.
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        if self.registers['v'][vx_register] == self.registers['v'][vy_register]:
            self.registers['pc'] = self.registers['pc'] + 2

    def skip_if_vx_not_equals_vy(self):
        """
        Si Vx es desigual a Vy saltamos la siguiente instrucción.
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        if self.registers['v'][vx_register] != self.registers['v'][vy_register]:
            self.registers['pc'] = self.registers['pc'] + 2

    def set_i_to_address(self):
        """
        Asigna a I nnn (?)
        """
        self.registers['I'] = (self.opcode & 0x0FFF)

    def set_vx_bitwise_random(self):
        """
        Bitwise random number with nnn and set result to Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        nnn_value = (self.opcode & 0x00FF)

        self.registers['v'][vx_register] = numpy.uint8(randint(0, 255) & nnn_value)

    def set_vx_to_vy(self):
        """
        Establece el valor de Vy a Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][vx_register] = numpy.uint8(self.registers['v'][vy_register])

    def set_vx_to_vx_or_vy(self):
        """
        Realiza la operación OR sobre Vx y Vy y guarda el valor en Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][vx_register] = numpy.uint8(self.registers['v'][vx_register] | self.registers['v'][vy_register])

    def set_vx_to_vx_and_vy(self):
        """
        Realiza la operación AND sobre Vx y Vy y guarda el valor en Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][vx_register] = numpy.uint8(self.registers['v'][vx_register] & self.registers['v'][vy_register])

    def set_vx_to_vx_xor_vy(self):
        """
        Realiza la operación AND sobre Vx y Vy y guarda el valor en Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][vx_register] = numpy.uint8(self.registers['v'][vx_register] ^ self.registers['v'][vy_register])

    def call_subroutine(self):
        """
        Llama a la subrutina en nnn.
        """
        subroutine_address = self.opcode & 0x0FFF

        self.registers['stack'][self.registers['sp']] = self.registers['pc'] + 2  # Saltamos a la siguiente instrucción.
        self.registers['sp'] = self.registers['sp'] + 1

        self.registers['pc'] = subroutine_address

    def clear_or_end_subroutine(self):
        """
        Limpia la pantalla
        El flujo del programa se devuelve a la instrucción que llamó a la subrutina
        """
        if self.opcode & 0x000F == 0xE:
            self.registers['pc'] = self.registers['stack'][self.registers['sp']]
            self.registers['sp'] = self.registers['sp'] - 1
        # else:
            # clear screen

    def add_nn_to_vx_no_flag(self):
        """
        Suma a Vx nn sin establecer la bandera en caso de overflow
        """
        vx_register = (self.opcode & 0x0F00) >> 8

        self.registers['v'][vx_register] = numpy.add(self.registers['v'][vx_register], numpy.uint8(self.opcode & 0x00FF))