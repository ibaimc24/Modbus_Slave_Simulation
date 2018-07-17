from core.utils import Configuration
from system import Slave
import signal
import sys



def terminate(signum, frame):
    print("Exiting program...")
    sys.exit(5)


if __name__ == '__main__':
    print(hex(1025))

    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)

    configuration = Configuration()

    # TODO: initialization configration before here
    slave = Slave(configuration)
    slave.run()


