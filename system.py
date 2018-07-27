from threading import Thread, Event
from core.protocols import *
from core.exceptions import *
from bitarray import bitarray


class Slave(Thread):

    def __init__(self, configuration):
        Thread.__init__(self)
        self.Configuration = configuration
        self.shutdown_flag = Event()

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Slave listening for connections in %s : %d" % (self.Configuration.Address, self.Configuration.Port))
        s.bind((self.Configuration.Address, self.Configuration.Port))
        s.listen(5)

        cnx, addr = s.accept()
        print("Connection donde by " + str(addr))
        #while not self.shutdown_flag.is_set():
        while True:
            data = cnx.recv(1024)  # OPTIMIZE: lower buffer = faster
            if not data:
                break

            # TODO: chech for not Modbus Packets
            pkt = ModbusADU(data)
            response = self.__get_answer(pkt)
            if response:
                cnx.sendto(bytes(response), (addr[0], addr[1]))
            else:
                continue

        cnx.close()

    def __get_answer(self, modbus_packet):

        if isinstance(modbus_packet.payload, ModbusPDU01ReadCoils):
            try:
                coilStatus = modbus_packet.payload.process(
                    datablock=self.Configuration.Data, coilsmask=self.Configuration.Coils,
                    supported_functions=self.Configuration.SupportedFunctionCodes)

                pdu = ModbusPDU01ReadCoilsAnswer(coilStatus=coilStatus, byteCount=len(coilStatus))
                adu = ModbusADU(len=len(pdu) + 1)
                return adu / pdu
            except ModbusException as ex:
                # Create ModbusException response packet
                adu = ModbusADU(len=3)
                pdu = ModbusPDU01ReadCoilsException(exceptCode=ex.exception_code)
                return adu / pdu

        elif isinstance(modbus_packet.payload, ModbusPDU02ReadDiscreteInputs):
            try:
                input_status = modbus_packet.payload.process(
                    datablock=self.Configuration.Data, discrete_inputs_mask=self.Configuration.DiscreteInputs,
                    supported_functions=self.Configuration.SupportedFunctionCodes)

                pdu = ModbusPDU02ReadDiscreteInputsAnswer(coilStatus=input_status, byteCount=len(input_status))
                adu = ModbusADU(len=len(pdu) + 1)
                return adu / pdu
            except ModbusException as ex:
                # Create ModbusException response packet
                adu = ModbusADU(len=3)
                pdu = ModbusPDU02ReadDiscreteInputsException(exceptCode=ex.exception_code)
                return adu / pdu


        # TODO: All type of answers
        else:
            # Unknown Function Code
            adu = ModbusADU(len=3)

            # TODO: Exception with requested function code + 127
            pdu = ModbusPDU01ReadCoilsException(funcCode=129, exceptCode=1)
            return adu / pdu

    def __validate_function_code(self, function_code):
        if function_code not in self.Configuration.SupportedFunctionCodes:
            raise InvalidFunctionCode01()
        # print(colors.WARNING + "Modbus Read Coils pakcet proccessing." + colors.reset)

    def __validate_data_address(self, start_addr):
        # TODO: validate or raise ExceptionCode = 2

        pass

    def __validate_data_value(self, start_addr, quantity):
        # print(colors.WARNING + "Checking for access permissions" + colors.reset)
        if not self.Configuration.Coils.can_access(start_addr, quantity):
            raise InvalidDataAddress02()

    def __execute_modbus_function(self, function_code, start_addr, quantity):
        # TODO: validate or raise ExceptionCode = 4, 5 or 6
        try:
            bits = []
            ans = []
            counter = 1
            for i in range(start_addr, start_addr+quantity):
                bits.append(self.Configuration.Data.read_bit(i))
                if counter is 8:
                    ans.append(int(bitarray(bits).to01(), 2))
                    bits = []
                    counter = 0
                counter += 1

            return ans
        except Exception as ex:
            raise ModbusException

    def __validate_outputs_quantity(self, quantity):
        # print(colors.WARNING + "Validating number of requested outputs" + colors.reset)
        if quantity < 1 or quantity > 2000:
            raise InvalidDataValue03()
