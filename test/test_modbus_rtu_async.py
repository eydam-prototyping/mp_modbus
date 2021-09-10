import unittest
from mp_modbus_master import modbus_rtu_master
from mp_modbus_slave import modbus_rtu_slave_async
import asyncio
import serial

class Test(unittest.TestCase):
    def setUp(self) :
        with serial.Serial("COM50") as uart1:
            self.srv = modbus_rtu_slave_async(context={
                "co":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)},   # Coils: ON OFF ON OFF ON OFF ON OFF ON OFF
                "di":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)},   # Digital Inputs: ON OFF ON OFF ON OFF ON OFF ON OFF
                "hr":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])},
                "ir":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])}
            }, uart=uart1, debug=True)
        return super().setUp()

    async def run_coroutines(self, coro_list):
        await asyncio.gather(*coro_list)

#    def test1(self):
#        with serial.Serial("COM50") as s:
#            s.write("test".encode("utf-8"))
#            s.flush()
#        
#        with serial.Serial("COM51") as s:
#            print(s.read(2))

    def test_read_coils_async(self):
        return
        async def client_routine():
            print(1)
            with serial.Serial("COM51") as uart2:
                sreader = asyncio.StreamReader(uart2)
                print(2)
                uart2.write("test".encode("utf-8"))
                print(3)
                uart2.flush()   
                print(4)

        asyncio.run(self.run_coroutines([ client_routine()]))