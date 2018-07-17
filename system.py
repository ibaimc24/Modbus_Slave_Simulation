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
        print("Slave listening for connections")
        s.bind(('0.0.0.0', 502))
        s.listen(5)

        cnx, addr = s.accept()
        print("Connection donde by " + str(addr))
        while not self.shutdown_flag.is_set():
            data = cnx.recv(1024)  # OPTIMIZE: lower buffer = faster
            if not data:
                break

            # TODO: chech for not Modbus Packets
            pkt = ModbusADU(data)
            response = self.__get_answer(pkt)
            # response = response.encode("utf-8")

            cnx.sendto(bytes(response), (addr[0], addr[1]))
        cnx.close()

    def __get_answer(self, modbus_packet):

        if isinstance(modbus_packet.payload, Raw):
            print("Malformed Modbus Packet")

        elif isinstance(modbus_packet.payload, ModbusPDU01ReadCoils):
            # print(colors.WARNING + "Modbus Read Coils Pakcet Recived." + colors.reset)
            start_addr = modbus_packet.payload.startAddr
            quantity = modbus_packet.payload.quantity
            # TODO:
            try:
                self.__validate_function_code(1)
                self.__validate_outputs_quantity(quantity)
                self.__validate_data_value(start_addr, quantity)
                data = self.__execute_modbus_function(1, start_addr, quantity)
                adu = ModbusADU()
                pdu = ModbusPDU01ReadCoilsAnswer()

                # 1025 in 8 bit numbers (x401)
                # data = [4, 0, 1]
                pdu.coilStatus = data
                pdu.byteCount = len(pdu.coilStatus)
                adu.len = len(pdu) + 1
                return adu/pdu

            except InvalidFunctionCode:
                # TODO: Generate Modbus Exception
                pass
            except InvalidDataAddress:
                # TODO: Generate Modbus Exception
                pass
            except InvalidDataValue:
                # TODO: Generate Modbus Exception
                pass
            except ModbusException:
                # TODO: Generate Modbus Exception
                pass

        # TODO: All type of answers
        else:
            print("Fail")

    def __validate_function_code(self, function_code):
        if function_code not in self.Configuration.SupportedFunctionCodes:
            raise InvalidFunctionCode()
        # print(colors.WARNING + "Modbus Read Coils pakcet proccessing." + colors.reset)

    def __validate_data_address(self, start_addr):
        # TODO: validate or raise ExceptionCode = 2

        pass

    def __validate_data_value(self, start_addr, quantity):
        # print(colors.WARNING + "Checking for access permissions" + colors.reset)
        if not self.Configuration.Coils.can_access(start_addr, quantity):
            raise InvalidDataAddress()

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
            raise InvalidDataValue()
