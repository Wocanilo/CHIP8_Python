# CHIP8 CPU


from Config import MAX_MEMORY, PROGRAM_COUNTER_START, DEBUG

class Chip8Cpu:


    def __init__(self):

        # Existen 16 registros de proposito general (V0-VF).
        # VF se encuentra reservado como marca para algunas instrucciones
        # I suele almacenar direcciones de memorias cuyos datos van a ser accedidos por la CPU
        # Stack permite almacenar el puntero de instrucciones (pc) cuando se realizan saltos, llamadas a subrutinas...
        # SP permite almacenar el nivel en el que se encuentrra el ultimo puntero de instrucciones almacenado.

        self.registers = {
            'v': [None] * 16,
            'I': 0,
            'pc': PROGRAM_COUNTER_START, # O tal vez 0?
            'stack': [None] * 16,
            'sp': 0
        }


        #Ambos llevan a cabo una cuenta regresiva a 60Hz hasta llegar a 0
        #delay_timer: controla los eventos de los juegos
        #sound_timer: si su valor es distinto de cero se produce un pitido

        self.timers = {
            'delay_timer': 0,
            'sound_timer': 0
        }

        #Debemos divir los OPCODES segun el tipo de operacion y construir diccionarios que 'traduzcan' el codigo


        self.general_opcode_lookup = {
            0x1: self.jump_to_address,
            0x3: self.skip_if_vx_equals_nn,
            0x6: self.set_vx_to_nn
        }

        self.opcode = 0
        self.memory = bytearray(MAX_MEMORY)


    def load_rom(self, rom, offset=PROGRAM_COUNTER_START):
        """
        Carga un archivo en memoria a partir del lugar indicado

        :param rom: el nombre del archivo a cargar
        :param offset: la ubicación de memoria donde empezar a cargar el archivo

        """
        with open(rom, "rb") as file_data:
             #Enumerate nos permite iterar sobre un objeto mientras mantenemos un contador del bucle actual
            for index, val in enumerate(file_data.read()): #Is a .read() needed?
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
            print("ERROR. OpCode: " + hex(instruction) + " Not found in lookup table.")

        return self.opcode

    def jump_to_address(self):
        """
        Salta a la dirección de memoria especificada por los últimos 3 bits de la instrucción
        """
        self.registers['pc'] = self.opcode & 0x0FFF

    def set_vx_to_nn(self):
        """
        Establece el valor de Vx a nn
        """
        registerToSet = (self.opcode & 0x0F00) >> 8
        valueToSet = (self.opcode & 0x00FF)
        self.registers['v'][registerToSet] = valueToSet

    def skip_if_vx_equals_nn(self):
        """
        Si Vx es igual a nn saltamos la siguiente instrucción
        """
        registerToCheck = (self.opcode & 0x0F00) >> 8
        valueToCheck = (self.opcode & 0x00FF)

        if self.registers['v'][registerToCheck] == valueToCheck:
            self.registers['pc'] = self.registers['pc'] + 2

