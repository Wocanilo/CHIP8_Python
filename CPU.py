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
            'pc': 0,
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

        #Creamos el array de memoria

        memory = bytearray(MAX_MEMORY)

    def load_rom(self, rom, offset=PROGRAM_COUNTER_START):
        """
        Carga la rom en memoria

        :param rom: el nombre del archivo a cargar
        :param offset: la ubicación de memoria donde empezar a cargar el archivo

        """
        with open(rom, "rb") as file_data:
             #Enumerate nos permite iterar sobre un objeto mientras mantenemos un contador del bucle actual
            for index, val in enumerate(file_data):
                self.memory[index + offset] = val



