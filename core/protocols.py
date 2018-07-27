from scapy.all import *
import binascii
from core.exceptions import *
from bitarray import bitarray

# own constant definitions
transId = 1
connection = None
timeout = 5
modport = 502

function_code_name = {
    1: "Read Coils",
    2: "Read Discrete Inputs",
    3: "Read Multiple Holding Registers",
    4: "Read Input Registers",
    5: "Write Single Coil",
    6: "Write Single Holding Register",
    7: "Read Exception Status",
    8: "Diagnostic",
    11: "Get Com Event Counter",
    12: "Get Com Event Log",
    15: "Write Multiple Coils",
    16: "Write Multiple Holding Registers",
    17: "Report Slave ID",
    20: "Read File Record",
    21: "Write File Record",
    22: "Mask Write Register",
    23: "Read/Write Multiple Registers",
    24: "Read FIFO Queue",
    43: "Read Device Identification"}

_modbus_exceptions = {
    1: "Illegal function",
    2: "Illegal data address",
    3: "Illegal data value",
    4: "Slave device failure",
    5: "Acknowledge",
    6: "Slave device busy",
    8: "Memory parity error",
    10: "Gateway path unavailable",
    11: "Gateway target device failed to respond"}

class Transaction:

    @staticmethod
    def validate_function_code(supported_functions, requested_function):
        if requested_function in supported_functions:
            return True
        else:
            return False

    @staticmethod
    def validate_data_address(data_mask, start_addr, quantity):
        # Validatione permissions of the request
        # Exception 02
        return data_mask.can_access(start_addr, quantity)

    @staticmethod
    def validate_data_value(quantity):
        # validate quantity of outputs
        # Exception 03
        if quantity < 1 or quantity > 2000:
            return False
        else:
            return True


    @staticmethod
    def execute_function():
        # Exception 04
        pass


class ModbusADU(Packet):

    name = "ModbusADU"
    fields_desc = [

        # needs to be unique
        XShortField("transId", 0x0000),

        # needs to be zero (Modbus)
        XShortField("protoId", 0x0000),

        # is calculated with payload
        XShortField("len", None),

        # 0xFF or 0x00 should be used for Modbus over TCP/IP
        XByteField("unitId", 0x0)
    ]

    def guess_payload_class(self, payload):
        # First byte of the payload is Modbus function code (254 available function codes)
        data = binascii.hexlify(bytes(payload))
        function_code = int(data[0:2], 16)

        if function_code == 0x01:
            return ModbusPDU01ReadCoils
        elif function_code == 0x81:
            return ModbusPDU01ReadCoilsException

        elif function_code == 0x02:
            return ModbusPDU02ReadDiscreteInputs
        elif function_code == 0x82:
            return ModbusPDU02ReadDiscreteInputsException

        elif function_code == 0x03:
            return ModbusPDU03ReadHoldingRegisters
        elif function_code == 0x83:
            return ModbusPDU03ReadHoldingRegistersException

        elif function_code == 0x04:
            return ModbusPDU04ReadInputRegisters
        elif function_code == 0x84:
            return ModbusPDU04ReadInputRegistersException

        elif function_code == 0x05:
            return ModbusPDU05WriteSingleCoil

        elif function_code == 0x85:
            return ModbusPDU05WriteSingleCoilException

        elif function_code == 0x06:
            return ModbusPDU06WriteSingleRegister
        elif function_code == 0x86:
            return ModbusPDU06WriteSingleRegisterException

        elif function_code == 0x07:
            return ModbusPDU07ReadExceptionStatus
        elif function_code == 0x87:
            return ModbusPDU07ReadExceptionStatusException

        elif function_code == 0x0F:
            return ModbusPDU0FWriteMultipleCoils
        elif function_code == 0x8F:
            return ModbusPDU0FWriteMultipleCoilsException

        elif function_code == 0x10:
            return ModbusPDU10WriteMultipleRegisters
        elif function_code == 0x90:
            return ModbusPDU10WriteMultipleRegistersException

        elif function_code == 0x11:
            return ModbusPDU11ReportSlaveId
        elif function_code == 0x91:
            return ModbusPDU11ReportSlaveIdException
        else:
            return Packet.guess_payload_class(self, payload)



# Can be used to replace all Modbus read
class ModbusPDUReadGeneric(Packet):
    name = "Read Generic"
    fields_desc = [
        XByteField("funcCode", 0x01),
        XShortField("startAddr", 0x0000),
        XShortField("quantity", 0x0001)
    ]


# 0x01 - Read Coils
class ModbusPDU01ReadCoils(Packet):
    name = "Read Coils Request"
    fields_desc = [
        XByteField("funcCode", 0x01),
        # 0x0000 to 0xFFFF
        XShortField("startAddr", 0x0000),
        XShortField("quantity", 0x0001)
    ]

    def process(self, datablock, coilsmask, supported_functions):
        # Read Coils State Diagram:
        if not Transaction.validate_function_code(supported_functions, 1):
            raise InvalidFunctionCode01(1)

        if not Transaction.validate_data_value(self.quantity):
            raise InvalidDataValue03()

        if not Transaction.validate_data_address(coilsmask, self.startAddr, self.quantity):
            raise InvalidDataAddress02()

        return self.execute(datablock)

    def execute(self, datablock):
        # response array
        data = []

        # bits internal array
        bits = []
        counter = 1

        # Read all requested bits and storage in internal array 'bits'
        for i in range(self.startAddr, self.startAddr + self.quantity):
            bits.append(datablock.read_bit(i))

            if counter is 8:  # When got 8 bits, create an integer and append to response
                data.append(int(bitarray(bits).to01(), 2))
                # Restart internal variables
                bits = []
                counter = 0
            counter += 1

        # 0 Padding to 8 multiple
        while len(bits) % 8 is not 0:
            bits.append(False)

        # Append padding byte
        data.append(int(bitarray(bits).to01(), 2))
        return data


class ModbusPDU01ReadCoilsAnswer(Packet):
    name = "Read Coils Answer"
    fields_desc = [
        XByteField("funcCode", 0x01),
        BitFieldLenField("byteCount", None, 8, count_of="coilStatus"),
        FieldListField("coilStatus", [0x00], ByteField("", 0x00), count_from=lambda pkt: pkt.byteCount)]


class ModbusPDU01ReadCoilsException(Packet):
    name = "Read Coils Exception"
    fields_desc = [
        XByteField("funcCode", 0x81),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]


# 0x02 - Read Discrete Inputs
class ModbusPDU02ReadDiscreteInputs(Packet):
    name = "Read Discrete Inputs"
    fields_desc = [
        XByteField("funcCode", 0x02),
        XShortField("startAddr", 0x0000),
        XShortField("quantity", 0x0001)]

    def process(self, datablock, discrete_inputs_mask, supported_functions):
        # TODO: define
        # Read DiscreteInputs Diagram:
        if not Transaction.validate_function_code(supported_functions, 1):
            raise InvalidFunctionCode01(1)

        if not Transaction.validate_data_value(self.quantity):
            raise InvalidDataValue03()

        if not Transaction.validate_data_address(discrete_inputs_mask, self.startAddr, self.quantity):
            raise InvalidDataAddress02()

        return self.execute(datablock)

    def execute(self, datablock):
        # TODO: define
        pass


class ModbusPDU02ReadDiscreteInputsAnswer(Packet):
    name = "Read Discrete Inputs Answer"
    fields_desc = [
        XByteField("funcCode", 0x02),
        BitFieldLenField("byteCount", None, 8, count_of="inputStatus"),
        FieldListField("inputStatus", [0x00], ByteField("", 0x00), count_from=lambda pkt: pkt.byteCount)]


class ModbusPDU02ReadDiscreteInputsException(Packet):
    name = "Read Discrete Inputs Exception"
    fields_desc = [
        XByteField("funcCode", 0x82),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]


# 0x03 - Read Holding Registers
class ModbusPDU03ReadHoldingRegisters(Packet):
    name = "Read Holding Registers"
    fields_desc = [
        XByteField("funcCode", 0x03),
        XShortField("startAddr", 0x0001),
        XShortField("quantity", 0x0002)]


class ModbusPDU03ReadHoldingRegistersAnswer(Packet):
    name = "Read Holding Registers Answer"
    fields_desc = [
        XByteField("funcCode", 0x03),
        BitFieldLenField("byteCount", None, 8, count_of="registerVal"),
        FieldListField("registerVal", [0x00], ByteField("", 0x00), count_from=lambda pkt: pkt.byteCount)]


class ModbusPDU03ReadHoldingRegistersException(Packet):
    name = "Read Holding Registers Exception"
    fields_desc = [
        XByteField("funcCode", 0x83),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]


# 0x04 - Read Input Registers
class ModbusPDU04ReadInputRegisters(Packet):
    name = "Read Input Registers"
    fields_desc = [
        XByteField("funcCode", 0x04),
        XShortField("startAddr", 0x0000),
        XShortField("quantity", 0x0001)]


class ModbusPDU04ReadInputRegistersAnswer(Packet):
    name = "Read Input Registers Answer"
    fields_desc = [
        XByteField("funcCode", 0x04),
        BitFieldLenField("byteCount", None, 8, count_of="registerVal"),
        FieldListField("registerVal", [0x00], ByteField("", 0x00), count_from=lambda pkt: pkt.byteCount)]


class ModbusPDU04ReadInputRegistersException(Packet):
    name = "Read Input Registers Exception"
    fields_desc = [
        XByteField("funcCode", 0x84),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]


# 0x05 - Write Single Coil
class ModbusPDU05WriteSingleCoil(Packet):
    name = "Write Single Coil"
    fields_desc = [
        XByteField("funcCode", 0x05),
        XShortField("outputAddr", 0x0000),   # from 0x0000 to 0xFFFF
        XShortField("outputValue", 0x0000)]  # 0x0000 == Off, 0xFF00 == On


class ModbusPDU05WriteSingleCoilAnswer(Packet):  # The answer is the same as the request if successful
    name = "Write Single Coil"
    fields_desc = [
        XByteField("funcCode", 0x05),
        XShortField("outputAddr", 0x0000),   # from 0x0000 to 0xFFFF
        XShortField("outputValue", 0x0000)]  # 0x0000 == Off, 0xFF00 == On


class ModbusPDU05WriteSingleCoilException(Packet):
    name = "Write Single Coil Exception"
    fields_desc = [
        XByteField("funcCode", 0x85),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]


# 0x06 - Write Single Register
class ModbusPDU06WriteSingleRegister(Packet):
    name = "Write Single Register"
    fields_desc = [
        XByteField("funcCode", 0x06),
        XShortField("registerAddr", 0x0000),
        XShortField("registerValue", 0x0000)]


class ModbusPDU06WriteSingleRegisterAnswer(Packet):

    name = "Write Single Register Answer"
    fields_desc = [
        XByteField("funcCode", 0x06),
        XShortField("registerAddr", 0x0000),
        XShortField("registerValue", 0x0000)]


class ModbusPDU06WriteSingleRegisterException(Packet):
    name = "Write Single Register Exception"
    fields_desc = [
        XByteField("funcCode", 0x86),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]


# 0x07 - Read Exception Status (Serial Line Only)
class ModbusPDU07ReadExceptionStatus(Packet):
    name = "Read Exception Status"
    fields_desc = [XByteField("funcCode", 0x07)]


class ModbusPDU07ReadExceptionStatusAnswer(Packet):
    name = "Read Exception Status Answer"
    fields_desc = [
        XByteField("funcCode", 0x07),
        XByteField("startingAddr", 0x00)]


class ModbusPDU07ReadExceptionStatusException(Packet):
    name = "Read Exception Status Exception"
    fields_desc = [
        XByteField("funcCode", 0x87),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]


# 0x0F - Write Multiple Coils
class ModbusPDU0FWriteMultipleCoils(Packet):
    name = "Write Multiple Coils"
    fields_desc = [
        XByteField("funcCode", 0x0F),
        XShortField("startingAddr", 0x0000),
        XShortField("quantityOutput", 0x0001),
        BitFieldLenField("byteCount", None, 8, count_of="outputsValue", adjust=lambda pkt, x:x),
        FieldListField("outputsValue", [0x00], XByteField("", 0x00), count_from=lambda pkt: pkt.byteCount)]


class ModbusPDU0FWriteMultipleCoilsAnswer(Packet):
    name = "Write Multiple Coils Answer"
    fields_desc = [
        XByteField("funcCode", 0x0F),
        XShortField("startingAddr", 0x0000),
        XShortField("quantityOutput", 0x0001)]


class ModbusPDU0FWriteMultipleCoilsException(Packet):
    name = "Write Multiple Coils Exception"
    fields_desc = [
        XByteField("funcCode", 0x8F),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]


# 0x10 - Write Multiple Registers
class ModbusPDU10WriteMultipleRegisters(Packet):
    name = "Write Multiple Registers"
    fields_desc = [
        XByteField("funcCode", 0x10),
        XShortField("startingAddr", 0x0000),
        XShortField("quantityRegisters", 0x0001),
        BitFieldLenField("byteCount", None, 8, count_of="outputsValue", adjust=lambda pkt, x:x),
        FieldListField("outputsValue", [0x00], XByteField("", 0x00), count_from=lambda pkt: pkt.byteCount)]


class ModbusPDU10WriteMultipleRegistersAnswer(Packet):
    name = "Write Multiple Registers Answer"
    fields_desc = [
        XByteField("funcCode", 0x10),
        XShortField("startingAddr", 0x0000),
        XShortField("quantityRegisters", 0x0001)]


class ModbusPDU10WriteMultipleRegistersException(Packet):
    name = "Write Multiple Registers Exception"
    fields_desc = [
        XByteField("funcCode", 0x90),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]


# 0x11 - Report Slave Id
class ModbusPDU11ReportSlaveId(Packet):
    name = "Report Slave Id"
    fields_desc = [XByteField("funcCode", 0x11)]


class ModbusPDU11ReportSlaveIdAnswer(Packet):
    name = "Report Slave Id Answer"
    fields_desc = [
        XByteField("funcCode", 0x11),
        BitFieldLenField("byteCount", None, 8, length_of="slaveId"),
        ConditionalField(StrLenField("slaveId", "", length_from=lambda pkt: pkt.byteCount),
                         lambda pkt: pkt.byteCount > 0),
        ConditionalField(XByteField("runIdicatorStatus", 0x00), lambda pkt: pkt.byteCount > 0)]


class ModbusPDU11ReportSlaveIdException(Packet):
    name = "Report Slave Id Exception"
    fields_desc = [
        XByteField("funcCode", 0x91),
        ByteEnumField("exceptCode", 1, _modbus_exceptions)]
