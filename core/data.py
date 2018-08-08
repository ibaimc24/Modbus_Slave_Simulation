from bitarray import bitarray
from abc import ABCMeta
import abc
from core.exceptions import SlaveException
from array import array

class DataBlock:

    blockName = "Data"

    BlockTypes = ['bit', 'register']

    def __init__(self, type='bit'):
        if type not in DataBlock.BlockTypes:
            raise SlaveException("Invalid DataBlock type")
        if type == 'bit':
            self.type = 'bit'
            self.data = self.data = bitarray(2**16)
            self.data.setall(0)
        else:
            self.type = 'register'
            self.data = array('h', [0]*100)

        self.Blocks = []

    def add_block(self, start_addr, end):
        self.Blocks.append((start_addr, end))

    def show(self):
        print("\n\n------ " + self.blockName + " ------\n")
        for i in range(0, 65535, 16):
            print(self.data[i:i+16].to01())

    def show_blocks(self):
        print("\t%s " % self.blockName)
        for block in self.Blocks:
            print("\t\t\tFrom \t %d \t to \t %d" % (block[0], block[1]))

    def read_register(self, addr):
        """
        Reads a data segment of 16 bit register in the specified register address.
        :param addr: register number. Each register returns 16 bits integer. 0 <= addr < 4.096
        :return: 16 bit integer representing the register value.
        """
        bit_num = addr * 16
        # Access In mutual exclusion
        value = self.data[bit_num:bit_num+16]
        return value

    def write_register(self, addr, value):
        """
        Writes a 16 bit value in data the specified register address.
        :param addr: Register number to be written.
        :param value: Value to be written in the register.
        :return: None
        """
        bit_num = addr * 16

        # Create new register values and set to 0
        new_reg = bitarray(16)
        new_reg.setall(0)

        # Create bitarray with binary values of 'value'
        in_bits = format(value, "b")
        tmp_reg = bitarray(in_bits)

        # fill new register values with created binary bitarray
        new_reg[16 - len(tmp_reg):] = tmp_reg

        # Insert new register in 'addr' position
        self.data[bit_num:bit_num+16] = new_reg

    def read_bit(self, addr):
        """
        Gets the value of the specified bit in addr position.
        :param addr:
        :return: True if '1'. False if '0'.
        """
        value = self.data[addr]
        return value

    def write_bit(self, addr, value):
        """
        Writes value in  the specified addr bit.
        :param addr:
        :param value:
        :return:
        """
        self.data[addr] = value

class BitTable(DataBlock):

    def __init__(self):
        DataBlock.__init__(self)
        self.data = self.data = bitarray(2 ** 16)
        self.data.setall(0)

class MaskInterface(object):
    __metaclass__ = ABCMeta

    @abc.abstractmethod
    def can_access(self, start_addr, quantity):
        pass

    @abc.abstractmethod
    def add_block(self, start_addr, end_addr):
        pass

    def show_blocks(self):
        pass


class GenerikMask(MaskInterface):

    MaskName = "Generic Mask"

    def __init__(self):
        MaskInterface.__init__(self)
        self.mask = bitarray(2 ** 16)
        self.mask.setall(0)
        self.Blocks = []

    def can_access(self, start_addr, quantity):
        requested = self.mask[start_addr: start_addr + quantity]
        # Returns True when all bits in the array are True.
        return requested.all()

    def add_block(self, start_addr, end_addr):
        self.mask[start_addr:end_addr] = True
        self.Blocks.append((start_addr, end_addr))

    def show_blocks(self):
        print("\t%s " % self.MaskName)
        for block in self.Blocks:
            print("\t\t\tFrom \t %d \t to \t %d" % (block[0], block[1]))


class CoilsMask(GenerikMask):

    MaskName = "Coils Mask"

    def __init__(self):
        GenerikMask.__init__(self)


class InputRegistersMask(GenerikMask):

    MaskName = "Input Register"

    def __init__(self):
        GenerikMask.__init__(self)

    def can_access(self, start_addr, quantity):
        requested = self.mask[start_addr: start_addr + quantity*16]
        return requested.all()


class HoldingRegistersMask(GenerikMask):

    MaskName = "Holding Registers"

    def __init__(self):
        GenerikMask.__init__(self)

    def can_access(self, start_addr, quantity):
        requested = self.mask[start_addr: start_addr + quantity*16]
        return requested.all()


class DiscreteInputsMask(GenerikMask):

    MaskName = "Discrete Inputs"

    def __init__(self):
        GenerikMask.__init__(self)
