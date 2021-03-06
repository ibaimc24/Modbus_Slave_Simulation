from system import Slave
import signal
import sys
from core.interface import MainMenu
from core.handler import Handler



def terminate(signum, frame):
    print("Exiting program...")
    sys.exit(5)


if __name__ == '__main__':

    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)

    configuration = MainMenu.start_menu()
    configuration.Coils.show_blocks()
    configuration.DiscreteInputs.show_blocks()
    configuration.InputRegisters.show_blocks()
    configuration.HoldingRegisters.show_blocks()
    slave = Slave(configuration)
    handler = Handler(slave.Configuration.Data, slave.Configuration.Data.Blocks)
    handler.start()
    slave.start()
    handler.join()
    slave.join()



