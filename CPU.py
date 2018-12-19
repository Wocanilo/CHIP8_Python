from Config import MAX_MEMORY, PROGRAM_COUNTER_START, DEBUG
from os import urandom
from random import seed, randint
import numpy


class HertzCPU:

    def __init__(self):

        # Existen 16 registros de proposito general (V0-VF).
        # VF se encuentra reservado como marca para algunas instrucciones
        # I suele almacenar direcciones de memorias cuyos datos van a ser accedidos por la CPU
        # Stack permite almacenar el puntero de instrucciones (pc) cuando se realizan saltos, llamadas a subrutinas...
        # SP permite almacenar el nivel en el que se encuentrra el ultimo puntero de instrucciones almacenado.

        self.registers = {
            'v': [numpy.uint8(0)] * 16,
            'I': numpy.uint16(0),
            'pc': PROGRAM_COUNTER_START,
            'stack': [0] * 16,
            'sp': 0,
            'index': 0
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
            0x0: self.end_subroutine,
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
            0xC: self.set_vx_bitwise_random,
            0xF: self.execute_misc_instruction
        }

        self.logic_opcode_lookup = {
            0x0: self.set_vx_to_vy,
            0x1: self.set_vx_to_vx_or_vy,
            0x2: self.set_vx_to_vx_and_vy,
            0x3: self.set_vx_to_vx_xor_vy,
            0x4: self.add_vy_to_vx,
            0x5: self.subtract_vx_minus_vy,
            0x6: self.store_least_bit_right_shift,
            0x7: self.subtract_vy_minus_vx,
            0xE: self.store_most_bit_left_shift,
        }

        self.misc_opcode_lookup = {
            0x3: self.store_bcd_in_memory,
            0x7: self.set_vx_to_delay_timer,
            0x5: self.dump_or_load_v_registers_to_memory_or_set_timer,
            0x8: self.set_sound_timer_to_vx,
            0xE: self.add_vx_to_i
        }

        self.opcode = 0
        self.memory = bytearray(MAX_MEMORY)
        seed(urandom(20))

    def decrement_timers(self):
        if self.timers['delay_timer'] > 0:
            self.timers['delay_timer'] -= 1
        if self.timers['sound_timer'] > 0:
            self.timers['delay_timer'] -= 1

    def load_rom(self, rom, offset=PROGRAM_COUNTER_START):
        """
        Carga un archivo en memoria a partir del lugar indicado

        :param rom: el nombre del archivo a cargar
        :param offset: la ubicación de memoria donde empezar a cargar el archivo

        """
        with open(rom, "r") as file_data:
            # Enumerate nos permite iterar sobre un objeto mientras mantenemos un contador del bucle actual
            for index, val in enumerate(file_data.read().split()):  # Is a .read() needed?
                self.memory[index + offset] = int(val, 2)

    def execute_instruction(self):
        """
        Obtiene la siguiente instrucción de la memoria y lo ejecuta

        :return: OPCODE
        """
        # Cada instruccion está formada por 2 bytes. Cada byte está formado por 8 bits.
        # Debemos desplazar el valor del primer byte 8 puestos a la izq. para luego realizar un OR sobre ambos bytes
        instruction = self.memory[self.registers['pc']] << 8 | self.memory[self.registers['pc'] + 1]

        if DEBUG:
            print("Instruccion: " + hex(instruction))
            print("Direccion actual del programa: " + str(self.registers['pc']))

        self.registers['pc'] = self.registers['pc'] + 2

        self.opcode = instruction
        instruction = (instruction & 0xF000) >> 12
        try:
            self.instruction_name = self.general_opcode_lookup[instruction]()
        except KeyError:
            print("ERROR. OpCode: " + hex(self.opcode) + " Not found in general lookup table.")

        return self.opcode

    def execute_logic_instruction(self):
        instruction = self.opcode & 0x000F
        try:
            instruction_name = self.logic_opcode_lookup[instruction]()
        except KeyError:
            print("ERROR. OpCode: " + hex(self.opcode) + " Not found in logical lookup table.")
        return instruction_name

    def execute_misc_instruction(self):
        instruction = self.opcode & 0x000F
        try:
            instruction_name = self.misc_opcode_lookup[instruction]()
        except KeyError:
            print("ERROR. OpCode: " + hex(self.opcode) + " Not found in misc lookup table.")

        return instruction_name

    def jump_to_address(self):
        """
        Salta a la dirección de memoria especificada por los últimos 3 bits de la instrucción
        """
        if (self.opcode & 0xF000) >> 12 == 0xB:
            self.registers['pc'] = (self.opcode & 0x0FFF) + self.registers['v'][0]
        else:
            self.registers['pc'] = self.opcode & 0x0FFF
            return ("JP " + str(self.opcode & 0x0FFF),)

    def set_vx_to_nn(self):
        """
        Establece el valor de Vx a nn
        """
        register_to_set = (self.opcode & 0x0F00) >> 8
        value_to_set = (self.opcode & 0x00FF)
        self.registers['v'][register_to_set] = numpy.uint8(value_to_set)

        mnemonic = "LD V" +  str(register_to_set) + ", " +  str(value_to_set)
        human = "V" + str(register_to_set) + " <= " + str(value_to_set)
        result = "V" + str(register_to_set) + " = " + str(self.registers['v'][register_to_set])

        return (mnemonic, human, result)

    def skip_if_vx_equals_nn(self):
        """
        Si Vx es igual a nn saltamos la siguiente instrucción
        """
        register_to_check = (self.opcode & 0x0F00) >> 8
        value_to_check = (self.opcode & 0x00FF)
        result = "False"

        if self.registers['v'][register_to_check] == value_to_check:
            self.registers['pc'] = self.registers['pc'] + 2
            result = "True"

        mnemonic = "SE V" + str(register_to_check) + ", " + str(value_to_check)
        human = "V" + str(register_to_check) + " == " + str(value_to_check)

        return (mnemonic, human, result)

    def skip_if_vx_not_equals_nn(self):
        """
        Si Vx es desigual a nn saltamos la siguiente instrucción.
        """
        register_to_check = (self.opcode & 0x0F00) >> 8
        value_to_check = (self.opcode & 0x00FF)
        result = "False"

        if self.registers['v'][register_to_check] != value_to_check:
            self.registers['pc'] = self.registers['pc'] + 2
            result = "True"

        mnemonic = "SNE V" + str(register_to_check) + ", " + str(value_to_check)
        human = "V" + str(register_to_check) + " != " + str(value_to_check)

        return (mnemonic, human, result)

    def skip_if_vx_equals_vy(self):
        """
        Si Vx es igual a Vy saltamos la siguiente instrucción.
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4
        result = "False"

        if self.registers['v'][vx_register] == self.registers['v'][vy_register]:
            self.registers['pc'] = self.registers['pc'] + 2
            result = "True"

        mnemonic = "SE V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " == " + "V" + str(vy_register)

        return (mnemonic, human, result)

    def skip_if_vx_not_equals_vy(self):
        """
        Si Vx es desigual a Vy saltamos la siguiente instrucción.
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4
        result = "False"

        if self.registers['v'][vx_register] != self.registers['v'][vy_register]:
            self.registers['pc'] = self.registers['pc'] + 2
            result = "True"

        mnemonic = "SNE V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " != " + "V" + str(vy_register)

        return (mnemonic, human, result)

    def set_i_to_address(self):
        """
        Asigna a I nnn (?)
        """
        self.registers['I'] = numpy.uint16(self.opcode & 0x0FFF)

        mnemonic = "LD I, " + str(self.opcode & 0x0FFF)
        human = "I <= " + str(self.opcode & 0x0FFF)
        result = "I = " + str(self.opcode & 0x0FFF)

        return (mnemonic, human, result)

    def set_vx_bitwise_random(self):
        """
        Bitwise random number with nnn and set result to Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        nnn_value = (self.opcode & 0x00FF)
        random_number = randint(0, 255)

        self.registers['v'][vx_register] = numpy.uint8(random_number & nnn_value)

        mnemonic = "RND V" + str(vx_register) + ", " + str(nnn_value)
        human = "V" + str(vx_register) + " <= " + str(random_number) + " & " + str(nnn_value)
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def set_vx_to_vy(self):
        """
        Establece el valor de Vy a Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][vx_register] = numpy.uint8(self.registers['v'][vy_register])

        mnemonic = "LD V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " <= V" + str(vy_register)
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vy_register])

        return (mnemonic, human, result)

    def set_vx_to_vx_or_vy(self):
        """
        Realiza la operación OR sobre Vx y Vy y guarda el valor en Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][vx_register] = numpy.bitwise_or(self.registers['v'][vx_register], self.registers['v'][vy_register])

        mnemonic = "OR V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " | V" + str(vy_register)
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def set_vx_to_vx_and_vy(self):
        """
        Realiza la operación AND sobre Vx y Vy y guarda el valor en Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][vx_register] = numpy.bitwise_and(self.registers['v'][vx_register], self.registers['v'][vy_register])

        mnemonic = "AND V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " <= V" + str(vx_register) + " & V" + str(vy_register)
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def set_vx_to_vx_xor_vy(self):
        """
        Realiza la operación XOR sobre Vx y Vy y guarda el valor en Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][vx_register] = numpy.bitwise_xor(self.registers['v'][vx_register], self.registers['v'][vy_register])

        mnemonic = "XOR V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " <= V" + str(vx_register) + " ^ V" + str(vy_register)
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def call_subroutine(self):
        """
        Llama a la subrutina en nnn.
        """
        subroutine_address = self.opcode & 0x0FFF

        self.registers['stack'][self.registers['sp']] = self.registers['pc'] + 2  # Saltamos a la siguiente instrucción.
        self.registers['sp'] = self.registers['sp'] + 1

        self.registers['pc'] = subroutine_address

        mnemonic = "CALL " + str(subroutine_address)
        human = "PC <= " + str(subroutine_address) + ", sp <= " + str(self.registers['sp'])
        result = "PC <= " + str(subroutine_address) + ", sp <= " + str(self.registers['sp'])

        return (mnemonic, human, result)

    def end_subroutine(self):
        """
        Limpia la pantalla
        El flujo del programa se devuelve a la instrucción que llamó a la subrutina
        """
        if self.opcode & 0x000F == 0xE:
            self.registers['pc'] = self.registers['stack'][self.registers['sp']]
            self.registers['sp'] = self.registers['sp'] - 1

        mnemonic = "RET"
        human = "PC <= " + str(self.registers['stack'][self.registers['sp']]) + ", sp <= " + str(self.registers['sp'])
        result = "PC <= " + str(self.registers['stack'][self.registers['sp']]) + ", sp <= " + str(self.registers['sp'])

        return (mnemonic, human, result)

    def add_nn_to_vx_no_flag(self):
        """
        Suma a Vx nn sin establecer la bandera en caso de overflow
        """
        vx_register = (self.opcode & 0x0F00) >> 8

        self.registers['v'][vx_register] = numpy.add(self.registers['v'][vx_register], numpy.uint8(self.opcode & 0x00FF))

        mnemonic = "ADD V" + str(vx_register) + ", " + str(self.opcode & 0x00FF)
        human = "V" + str(vx_register) + " <= V" + str(vx_register) + " + " + str(self.opcode & 0x00FF)
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def add_vy_to_vx(self):
        """
        Suma Vy a Vx. Si llevamos un bit establecemos la bandera a 1
        """
        self.registers['v'][0xf] = numpy.uint8(0)  # No borrow
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        resultado = numpy.add(self.registers['v'][vx_register], self.registers['v'][vy_register])

        if (int(self.registers['v'][vx_register ]) + int(self.registers['v'][vy_register])) > 255:
            self.registers['v'][0xf] = numpy.uint8(1)  # Borrow
        self.registers['v'][vx_register] = resultado

        mnemonic = "ADD V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " <= V" + str(vx_register) + " + V" + str(vy_register)
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def subtract_vx_minus_vy(self):
        """
        Resta Vy a Vx. Si llevamos un bit establecemos la bandera a 1
        """
        self.registers['v'][0xf] = numpy.uint8(0)  # No borrow
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        resultado = numpy.subtract(self.registers['v'][vx_register], self.registers['v'][vy_register])

        if (int(self.registers['v'][vx_register]) - int(self.registers['v'][vy_register])) < 0:
            self.registers['v'][0xf] = numpy.uint8(1) # Borrow
        self.registers['v'][vx_register] = resultado

        mnemonic = "SUB V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " <= V" + str(vx_register) + " - V" + str(vy_register)
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def subtract_vy_minus_vx(self):
        """
        Resta Vx a Vy. Si llevamos un bit establecemos la bandera a 1
        """
        self.registers['v'][0xf] = numpy.uint8(0)  # No borrow
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        resultado = numpy.subtract(self.registers['v'][vy_register], self.registers['v'][vx_register])

        if (int(self.registers['v'][vy_register]) - int(self.registers['v'][vx_register])) < 0:
            self.registers['v'][0xf] = numpy.uint8(1)  # Borrow
        self.registers['v'][vx_register] = resultado

        mnemonic = "SUB V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vy_register) + " <= V" + str(vx_register) + " - V" + str(vy_register)
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def store_least_bit_right_shift(self):
        """
        Almacena el bit menos significativo de Vy en VF y luego desplaza el valor de Vy un bit a la der
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][0xf] = self.registers['v'][vy_register] & 0x0F
        self.registers['v'][vx_register] = self.registers['v'][vx_register] >> 1

        mnemonic = "SHR V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " <= V" + str(vx_register) + " >> 1"
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def store_most_bit_left_shift(self):
        """
        Almacena el bit más significativo de Vy en VF y luego desplaza el valor de Vy un bit a la izq
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        vy_register = (self.opcode & 0x00F0) >> 4

        self.registers['v'][0xf] = (self.registers['v'][vy_register] & 0xF0) >> 4
        self.registers['v'][vx_register] = self.registers['v'][vx_register] << 1

        mnemonic = "SHL V" + str(vx_register) + ", V" + str(vy_register)
        human = "V" + str(vx_register) + " <= V" + str(vx_register) + " << 1"
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def set_vx_to_delay_timer(self):
        """
        Asigna a Vx el valor de delay_timer
        """
        vx_register = (self.opcode & 0x0F00) >> 8

        self.registers['v'][vx_register] = self.timers['delay_timer']

        mnemonic = "LD V" + str(vx_register) + ", DT"
        human = "V" + str(vx_register) + "<= DT"
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def set_sound_timer_to_vx(self):
        """
        Establece sound_timer al valor de Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8

        self.timers['sound_timer'] = self.registers['v'][vx_register]

        mnemonic = "LD V" + str(vx_register) + ", ST"
        human = "V" + str(vx_register) + "<= ST"
        result = "V" + str(vx_register) + " = " + str(self.registers['v'][vx_register])

        return (mnemonic, human, result)

    def add_vx_to_i(self):
        """
        Suma Vx a I y establece la bandera si se produce un overflow
        """
        vx_register = (self.opcode & 0x0F00) >> 8
        self.registers['v'][0xf] = numpy.uint8(0)  # No overflow

        resultado = numpy.add(self.registers['I'], self.registers['v'][vx_register])

        if resultado < (int(self.registers['I']) + int(self.registers['v'][vx_register])):
            self.registers['v'][0xf] = numpy.uint8(1)  # Overflow
        self.registers['I'] = resultado

        return ("NOT IMPLEMENTED", "NOT IMPLEMENTED", "NOT IMPLEMENTED")

    def dump_or_load_v_registers_to_memory_or_set_timer(self):
        """
        Almacena o carga los valores de los registros en/de la memoria
        """
        dump_or_load_or_set = (self.opcode & 0x00F0) >> 4
        vx_register = (self.opcode & 0x0F00) >> 8

        if dump_or_load_or_set == 5:
            for index, register in enumerate(range(0x0, vx_register + 1)):
                self.memory[self.registers['I'] + index] = self.registers['v'][register]
        if dump_or_load_or_set == 6:
            for index, register in enumerate(range(0x0, vx_register + 1)):
                self.registers['v'][register] = self.memory[self.registers['I'] + index]
        if dump_or_load_or_set == 1:
            self.timers['delay_timer'] = self.registers['v'][vx_register]

        return ("NOT IMPLEMENTED", "NOT IMPLEMENTED", "NOT IMPLEMENTED")

    def store_bcd_in_memory(self):
        """
        Guarda en memoria la representacion del numero Vx
        """
        vx_register = (self.opcode & 0x0F00) >> 8

        self.memory[self.registers['I']] = (self.registers['v'][vx_register] & 0xF00) >> 8
        self.memory[self.registers['I'] + 1] = (self.registers['v'][vx_register] & 0x0F0) >> 4
        self.memory[self.registers['I'] + 2] = (self.registers['v'][vx_register] & 0x00F)

        return ("NOT IMPLEMENTED", "NOT IMPLEMENTED", "NOT IMPLEMENTED")
