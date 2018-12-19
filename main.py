from CPU import Chip8Cpu
from pygame import time
import npyscreen
import threading
import argparse

inputfile = ''
clockspeed = 0
dump = False

class Interprete(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", MainForm())

class MainForm(npyscreen.Form):
    def create(self):
        self.grid_instrucciones = self.add(npyscreen.GridColTitles, always_show_cursor=True, col_titles=('Instruction', 'Mnemonic', 'Human', 'Result'))
        self.grid_instrucciones.set_grid_values_from_flat_list([])

        thread_time = threading.Thread(target=self.execute,args=())
        thread_time.daemon = True
        thread_time.start()

    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def execute(self):
        cpu = Chip8Cpu()

        cpu.load_rom(inputfile, 0)

        internalClock = time.Clock()

        running = True

        while running:
            internalClock.tick_busy_loop(clockspeed)  # Limita la CPU a funcionar a 1hz
            cpu.decrement_timers()
            instruccion = cpu.execute_instruction()

            if instruccion == 0x0:
                self.grid_instrucciones.values.append((hex(instruccion), "HALT"))
                running = False
            else:
                self.grid_instrucciones.values.append((hex(instruccion), cpu.instruction_name[0], cpu.instruction_name[1], cpu.instruction_name[2]))

            if instruccion == 0x0:
                running = False
                if dump:
                    for i, registro in enumerate(cpu.registers['v']):
                        self.grid_instrucciones.values.append(("0x0", "DUMP V" + str(i), bin(registro)))

            self.grid_instrucciones.display()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='file')
    parser.add_argument('-c', '--clockspeed', dest='clock_speed')
    parser.add_argument('-d', '--dump', action='count')
    args = parser.parse_args()

    if args.file != None and args.clock_speed != None:
        clockspeed = int(args.clock_speed)
        inputfile = args.file
        if args.dump == 1:
            dump = True
        interprete = Interprete()
        interprete.run()
    else:
        parser.print_usage()







