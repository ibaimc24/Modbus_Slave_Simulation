from threading import Thread
from core.data import DataBlock
import random
from time import sleep


class Handler(Thread):

    SleepDelay = 0.5214

    def __init__(self, data, blocks):
        Thread.__init__(self)
        # Data to be handled
        self.datablock = data

        # segments of data addresses to handle
        self.blocks = blocks

    def run(self):
        random.seed()
        while True:
            # Select random block
            block = random.choice(self.blocks)

            # Select random address from block
            addr = random.randrange(block[0], block[1], 1)

            # Write random bit value
            self.datablock.write_bit(addr, random.choice([0, 1]))
            # print("[*] written %d" % addr)
            sleep(self.SleepDelay)
