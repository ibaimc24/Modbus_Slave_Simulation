from bitarray import bitarray


class DataBlock:

    # TODO: Catch arguments exceptions

    blockName = "Data"

    def __init__(self):
        self.data = bitarray(2**16)
        self.data.setall(0)

    def show(self):
        print("\n\n------ " + self.blockName + " ------\n")
        for i in range(0, 65535, 16):
            print(self.data[i:i+16].to01())

    def change_register(self, start_addr, n_registers, valuess):
        pass

    def read_register(self, addr):
        """
        Reads a data segment of 16 bit register in the specified register address.
        :param addr: register number. Each register returns 16 bits integer. 0 <= addr < 4.096
        :return: 16 bit integer representing the register value.
        """
        bit_num = addr * 16
        return self.data[bit_num:bit_num+16]

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
        return self.data[addr]

    def write_bit(self, addr, value):
        """
        Writes value in  the specified addr bit.
        :param addr:
        :param value:
        :return:
        """
        self.data[addr] = value


class CoilsMask(DataBlock):

    blockName = "Coils Mask"

    def __init__(self, start_addr, end_addr):
        DataBlock.__init__(self)
        self.data[start_addr:end_addr] = True

    def can_access(self, start_addr, quantity):
        requested = self.data[start_addr : start_addr+quantity]
        # Returns True when all bits in the array are True.
        return requested.all()


class InputRegistersMask(DataBlock):

    blockName = "Input Register"

    def __init__(self, start_addr, end_addr):
        DataBlock.__init__(self)
        self.data[start_addr:end_addr] = True


class HoldingRegistersMask(DataBlock):

    blockName = "Holding Registers"

    def __init__(self, start_addr, end_addr):
        DataBlock.__init__(self)
        self.data[start_addr:end_addr] = True


class DiscreteInputsMask(DataBlock):

    blockName = "Discrete Inputs"

    def __init__(self, start_addr, end_addr):
        DataBlock.__init__(self)
        self.data[start_addr:end_addr] = True
