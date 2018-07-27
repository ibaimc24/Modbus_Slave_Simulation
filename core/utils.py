from core.interface import ConfigurationInterface, GenericInterace
from core.data import *


class Configuration:

    # TODO: User defined

    DefaultFile = "default.cnf"

    def __init__(self):
        # 5. Generate Data Block
        self.Data = DataBlock()
        self.Coils = CoilsMask()
        self.InputRegisters = InputRegistersMask()
        self.HoldingRegisters = DiscreteInputsMask()
        self.DiscreteInputs = HoldingRegistersMask()
        self.Address = None
        self.Port = None
        self.SupportedFunctionCodes = []
        self.edit_configuration()

    def edit_configuration(self):
        self.Address, self.Port = GenericInterace.get_general_configuration()
        option = GenericInterace.adding_blocks()
        while option is not "Done":
            if option == "Add Coils":
                start, end = ConfigurationInterface().input("Coils")
                self.SupportedFunctionCodes.append(1)
                self.SupportedFunctionCodes.append(5)
                self.Coils.add_block(start, end)

            elif option == "Add InputRegister":
                start, end = ConfigurationInterface().input("InputRegisters")
                self.SupportedFunctionCodes.append(4)
                self.InputRegisters.add_block(start, end)

            elif option == "Add HoldingRegisters":
                start, end = ConfigurationInterface().input("HoldingRegisters")
                self.SupportedFunctionCodes.append(3)
                self.SupportedFunctionCodes.append(6)
                self.HoldingRegisters.add_block(start, end)

            elif option == "Add DiscreteInputs":
                start, end = ConfigurationInterface().input("DiscreteInputs")
                self.SupportedFunctionCodes.append(2)
                self.DiscreteInputs.add_block(start, end)

            option = GenericInterace.adding_blocks()



