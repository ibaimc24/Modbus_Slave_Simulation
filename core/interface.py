from easygui import *
import sys


class ConfigurationInterface:

    ConfigItems = ['DiscreteInputs', 'Coils', 'InputRegisters', 'HoldingRegisters']
    Ranges = ['[0-65535]', '0-4095']

    def __init__(self, config_item):
        if config_item not in self.ConfigItems:
            raise ValueError("Config item must be one of next values: " + str(self.ConfigItems))
        if config_item in self.ConfigItems[0:2]:
            interval = self.Ranges[0]
        else:
            interval = self.Ranges[1]
        self.msg = "Enter a range for " + config_item + " values. " + interval

    def show(self):
        title = "Slave Configuration"
        field_name = ["Range"]
        field_values = multenterbox(self.msg, title, field_name)

        if not field_values:  # Cancelled
            sys.exit(0)

        [self.start, self.end] = self.__validate_values(field_values[0])

    def get_input(self):
        return self.start, self.end

    @staticmethod
    def __validate_values(range):
        range = range.strip()
        range = range.split('-')
        start = int(range[0])
        end = int(range[1])
        if start >= end:
            # Invalid range
            pass
        elif start < 0:
            # Invalid range
            pass
        elif end > 65535:
            # Invalid range
            pass
        else:
            # Data Ok
            pass
        return start, end




