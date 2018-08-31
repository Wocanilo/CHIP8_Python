# CHIP8 CPU


from Config import MAX_MEMORY, PROGRAM_COUNTER_START

class Chip8Cpu:


    def __init__(self):

        # Existen 16 registros de proposito general (V0-VF).
        # VF se encuentra reservado como marca para algunas instrucciones
        # I suele almacenar direcciones de memorias cuyos datos van a ser accedidos por la CPU
        # Stack permite almacenar el puntero de instrucciones (pc) cuando se realizan saltos, llamadas a subrutinas...
        # SP permite almacenar el nivel en el que se encuentrra el ultimo puntero de instrucciones almacenado.

        self.registers = {
            'v': [],
            'I': 0,
            'pc': PROGRAM_COUNTER_START, # O tal vez 0?
            'stack': [],
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



        #Creamos el array de memoria

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
        # Cada instruccion está formada por 2 bytes. Cada byte está formado por 8 bits.
        # Debemos desplazar el valor del primer byte 8 puestos a la izq. para luego realizar un OR sobre ambos bytes
        self.instruction = self.memory[self.registers['pc']] << 8 | self.memory[self.registers['pc'] + 1]

        self.registers['pc'] = self.registers['pc'] + 2
        print(hex(self.instruction))
