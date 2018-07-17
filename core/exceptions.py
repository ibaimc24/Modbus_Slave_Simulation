

class ModbusException(Exception):

    def __init__(self, message, exception_code=1):
        # Call the base class constructor with the parameters it needs
        super().__init__(message + ". ExceptionCode " + str(exception_code))
        self.exception_code = exception_code


class InvalidFunctionCode(ModbusException):

    def __init__(self):
        super().__init__("Invalid Function Code", 1)
        self.exception_code = 1
        self.message = "Invalid Function Code"


class InvalidDataAddress(ModbusException):

    def __init__(self):
        super().__init__("Invalid Function Code", 2)
        self.exception_code = 2
        self.message = "Invalid Data Code"


class InvalidDataValue(ModbusException):

    def __init__(self):
        super().__init__("Invalid Data Value", 3)
        self.exception_code = 3
        self.message = "Invalid Data Value"





