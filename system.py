from threading import Thread, Event
from core.protocols import *
from core.exceptions import *
from core.logging import colors


class Slave(Thread):

    def __init__(self, configuration):
        Thread.__init__(self)
        self.Configuration = configuration
        self.shutdown_flag = Event()

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        """
                while True:
            time.sleep(0.5)
            addr = random.randrange(1, 5, 1)
            value = self.Configuration.Data.read_bit(addr)
            print("[*] Read %d : %d " % (addr, value))
        """


        print("Slave listening for connections in %s : %d" % (self.Configuration.Address, self.Configuration.Port))
        s.bind((self.Configuration.Address, self.Configuration.Port))
        s.listen(5)

        # while not self.shutdown_flag.is_set():
        while True:
            cnx, addr = s.accept()
            print("Connection done by " + str(addr))
            while True:
                try:
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
                except OSError:
                    print("Connection closed.")
                    cnx.close()

    def __get_answer(self, modbus_packet):
        """
        Gets the requested Modbus answer.
        :param modbus_packet:
        :return:
        """

        modbus_exception = self.__validate_function_code(modbus_packet)
        if modbus_exception:
            return modbus_exception

        # READ COILS
        if isinstance(modbus_packet.payload, ModbusPDU01ReadCoils):
            try:
                coil_status = modbus_packet.payload.process(
                    datablock=self.Configuration.Data, coilsmask=self.Configuration.Coils)

                if modbus_packet.payload.startAddr == 2:
                    print("[*] Response Address %d , value %s " % (modbus_packet.payload.startAddr, str(coil_status)))
                pdu = ModbusPDU01ReadCoilsAnswer(coilStatus=coil_status, byteCount=len(coil_status))
                adu = ModbusADU(len=len(pdu) + 1)

            except ModbusException as ex:
                # Create ModbusException response packet
                adu = ModbusADU(len=3)
                pdu = ModbusPDUGenericException(funcCode=modbus_packet.funcCode + 128, exceptCode=ex.exception_code)
            return adu / pdu

        # READ DISCRETE INPUTS
        elif isinstance(modbus_packet.payload, ModbusPDU02ReadDiscreteInputs):
            try:
                input_status = modbus_packet.payload.process(
                    datablock=self.Configuration.Data, discrete_inputs_mask=self.Configuration.DiscreteInputs)

                pdu = ModbusPDU02ReadDiscreteInputsAnswer(inputStatus=input_status, byteCount=len(input_status))
                adu = ModbusADU(len=len(pdu) + 1)
            except ModbusException as ex:
                # Create ModbusException response packet
                adu = ModbusADU(len=3)
                pdu = ModbusPDUGenericException(funcCode=modbus_packet.funcCode + 128, exceptCode=ex.exception_code)

            return adu / pdu

        # READ HOLDING REGISTERS
        elif isinstance(modbus_packet.payload, ModbusPDU03ReadHoldingRegisters):
            try:
                registers_status = modbus_packet.payload.process(
                    datablock=self.Configuration.Data,
                    holding_registers_mask=self.Configuration.HoldingRegisters)
                pdu = ModbusPDU03ReadHoldingRegistersAnswer(registerVal=registers_status, byteCount=len(registers_status))
                adu = ModbusADU(len=len(pdu) + 1)
            except ModbusException as ex:
                # Create ModbusException response packet
                adu = ModbusADU(len=3)
                pdu = ModbusPDUGenericException(funcCode=modbus_packet.funcCode + 128, exceptCode=ex.exception_code)

            return adu / pdu

        # READ INPUT REGISTERS
        elif isinstance(modbus_packet.payload, ModbusPDU04ReadInputRegisters):
            try:
                registers_status = modbus_packet.payload.process(
                    datablock=self.Configuration.Data,
                    input_registers_mask=self.Configuration.InputRegisters)
                pdu = ModbusPDU04ReadInputRegistersAnswer(registerVal=registers_status, byteCount=len(registers_status))
                adu = ModbusADU(len=len(pdu) + 1)
            except ModbusException as ex:
                # Create ModbusException response packet
                adu = ModbusADU(len=3)
                pdu = ModbusPDUGenericException(funcCode=modbus_packet.funcCode + 128, exceptCode=ex.exception_code)

            return adu / pdu

        # WRITE SINGLE COIL
        elif isinstance(modbus_packet.payload, ModbusPDU05WriteSingleCoil):
            try:
                modbus_packet.payload.process(datablock=self.Configuration.Data, coils_mask=self.Configuration.Coils)
                # If goes OK, return an echo of request packet
                return modbus_packet

            except ModbusException as ex:
                # Create ModbusException response packet
                adu = ModbusADU(len=3)
                pdu = ModbusPDUGenericException(funcCode=modbus_packet.funcCode + 128, exceptCode=ex.exception_code)

            return adu / pdu

        elif isinstance(modbus_packet.payload, ModbusPDU06WriteSingleRegister):
            try:
                modbus_packet.payload.process(datablock=self.Configuration.Data,
                                              holding_registers_mask=self.Configuration.HoldingRegisters)
                # If goes OK, return an echo of request packet
                return modbus_packet
            except ModbusException as ex:
                adu = ModbusADU(len=3)
                pdu = ModbusPDUGenericException(funcCode=modbus_packet.funcCode + 128, exceptCode=ex.exception_code)

            return adu/pdu

        elif isinstance(modbus_packet.payload, ModbusPDU0FWriteMultipleCoils):
            try:
                modbus_packet.payload.process(datablock=self.Configuration.Data, coils_mask=self.Configuration.Coils)
                pdu = ModbusPDU0FWriteMultipleCoilsAnswer(startingAddr=modbus_packet.payload.startingAddr,
                                                          quantityOutput=modbus_packet.payload.quantityOutput)
                adu = ModbusADU(len=len(pdu)+1)

            except SlaveDeviceFailure as ex:
                print("[*]" + colors.bold + colors.fg.red + " System Failure while writting multiple coils: "
                      + ex.message)
                print("[*]" + colors.bold + colors.fg.red + " A ModbusException has sent with Exception code 04."
                      + colors.reset)
                adu = ModbusADU(len=3)
                pdu = ModbusPDUGenericException(funcCode=modbus_packet.funcCode + 128, exceptCode=ex.exception_code)
            except ModbusException as ex:
                adu = ModbusADU(len=3)
                pdu = ModbusPDUGenericException(funcCode=modbus_packet.funcCode + 128, exceptCode=ex.exception_code)

            return adu / pdu

        # TODO: All type of answers
        else:
            print("Unknown Function Code received.")
            adu = ModbusADU(len=3)
            code = modbus_packet.funcCode
            # TODO: Exception with requested function code + 127
            pdu = ModbusPDUGenericException(funcCode=code + 128, exceptCode=1)
            return adu / pdu

    def __validate_function_code(self, modbus_packet):
        """
        Cheks if slave supports requested function code.
        :param modbus_packet: Recived packet
        :return:    If it does, None is returned.
                    If it's not supported, the corresponding ModbusException Packet is returned.
        """
        data = binascii.hexlify(bytes(modbus_packet.payload))
        function_code = int(data[0:2], 16)
        if function_code not in self.Configuration.SupportedFunctionCodes:
            adu = ModbusADU(len=3)
            pdu = ModbusPDUIllegalFunctionException(funcCode=function_code+127)
            return adu / pdu
