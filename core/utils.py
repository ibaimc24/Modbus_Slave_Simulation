from core.interface import ConfigurationInterface
from core.data import *


def create_coils_mask():
    interface = ConfigurationInterface('Coils')
    interface.show()
    [start_addr, end_addr] = interface.get_input()
    return CoilsMask(start_addr, end_addr)


def create_input_registers_mask():
    interface = ConfigurationInterface('InputRegisters')
    interface.show()
    [start_addr, end_addr] = interface.get_input()
    return InputRegistersMask(start_addr, end_addr)


def create_holding_registers_mask():
    interface = ConfigurationInterface('HoldingRegisters')
    interface.show()
    [start_addr, end_addr] = interface.get_input()
    return HoldingRegistersMask(start_addr, end_addr)


def create_discrete_inputs_mask():
    interface = ConfigurationInterface('DiscreteInputs')
    interface.show()
    [start_addr, end_addr] = interface.get_input()
    return DiscreteInputsMask(start_addr, end_addr)


class Configuration:

    # TODO: User defined
    SupportedFunctionCodes = [1, 2, 15, 16]

    def __init__(self):
        # TODO: del
        print("starting conf")
        # 1. Create Coils mask
        self.Coils = create_coils_mask()

        # 2. Create InputRegisters mask
        self.InputRegisters = create_input_registers_mask()

        # 3. Create HoldingRegisters mask
        self.HoldingRegisters = create_holding_registers_mask()

        # 4. Create DiscreteInputs mask
        self.DiscreteInputs = create_discrete_inputs_mask()

        # 5. Generate Data Block
        self.Data = DataBlock()
