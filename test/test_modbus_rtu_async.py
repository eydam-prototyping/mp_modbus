import unittest
from mp_modbus_master import modbus_rtu_master
from mp_modbus_slave import modbus_rtu_slave
import asyncio
import serial

class Test(unittest.TestCase):
    def setUp(self) :
        #with serial.Serial("COM50") as uart1:
        self.sl = modbus_rtu_slave(context={
            "co":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)},   # Coils: ON OFF ON OFF ON OFF ON OFF ON OFF
            "di":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)},   # Digital Inputs: ON OFF ON OFF ON OFF ON OFF ON OFF
            "hr":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])},
            "ir":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])}
        }, uart=serial.Serial("COM50"), debug=True)
        return super().setUp()


    async def run_coroutines(self, coro_list):
        await asyncio.gather(*coro_list)


    def test_read_coils_async(self):
        async def client_routine():
            ms = modbus_rtu_master(uart=serial.Serial("COM51"))
            self.assertEqual(await ms.read_coils_async(1000, 1), bytearray([0x01]))
            self.assertEqual(await ms.read_coils_async(1001, 1), bytearray([0x00]))
            self.assertEqual(await ms.read_coils_async(1000, 2), bytearray([0x01]))
            self.assertEqual(await ms.read_coils_async(1001, 2), bytearray([0x02]))
            self.assertEqual(await ms.read_coils_async(1000, 3), bytearray([0x05]))
            self.sl.stop()

        asyncio.run(self.run_coroutines([self.sl.run_async(), client_routine()]))


    def test_read_digital_inputs_async(self):
        async def client_routine():
            ms = modbus_rtu_master(uart=serial.Serial("COM51"))
            self.assertEqual(await ms.read_digital_inputs_async(1000, 1), bytearray([0x01]))
            self.assertEqual(await ms.read_digital_inputs_async(1000, 2), bytearray([0x01]))
            self.assertEqual(await ms.read_digital_inputs_async(1000, 3), bytearray([0x05]))
            self.assertEqual(await ms.read_digital_inputs_async(1001, 1), bytearray([0x00]))
            self.assertEqual(await ms.read_digital_inputs_async(1001, 2), bytearray([0x02]))
            self.assertEqual(await ms.read_digital_inputs_async(1001, 3), bytearray([0x02]))
            self.sl.stop()

        asyncio.run(self.run_coroutines([self.sl.run_async(), client_routine()]))
    

    def test_read_holding_registers_async(self):
        async def client_routine():
            ms = modbus_rtu_master(uart=serial.Serial("COM51"))
            self.assertEqual(await ms.read_holding_registers_async(1000, 1), bytearray([0x00, 0x01]))
            self.assertEqual(await ms.read_holding_registers_async(1000, 2), bytearray([0x00, 0x01, 0x02, 0x03]))
            self.assertEqual(await ms.read_holding_registers_async(1001, 2), bytearray([0x02, 0x03, 0x04, 0x05]))
            self.assertEqual(await ms.read_holding_registers_async(1002, 3), bytearray([0x04, 0x05, 0x06, 0x07, 0x08, 0x09]))            
            self.sl.stop()

        asyncio.run(self.run_coroutines([self.sl.run_async(), client_routine()]))


    def test_read_input_registers_async(self):
        async def client_routine():
            ms = modbus_rtu_master(uart=serial.Serial("COM51"))
            self.assertEqual(await ms.read_input_registers_async(1000, 1), bytearray([0x00, 0x01]))
            self.assertEqual(await ms.read_input_registers_async(1000, 2), bytearray([0x00, 0x01, 0x02, 0x03]))
            self.assertEqual(await ms.read_input_registers_async(1001, 2), bytearray([0x02, 0x03, 0x04, 0x05]))
            self.assertEqual(await ms.read_input_registers_async(1002, 3), bytearray([0x04, 0x05, 0x06, 0x07, 0x08, 0x09]))
            self.sl.stop()

        asyncio.run(self.run_coroutines([self.sl.run_async(), client_routine()]))


    def test_read_write_coils_async(self): 
        async def client_routine():
            ms = modbus_rtu_master(uart=serial.Serial("COM51"))
            self.assertEqual(await ms.write_coil_async(1001, 1), True)
            self.assertEqual(await ms.read_coils_async(1000, 3), bytearray([0x07]))
            self.assertEqual(await ms.write_coil_async(1001, 0), False)
            self.assertEqual(await ms.read_coils_async(1000, 3), bytearray([0x05]))
            self.assertEqual(await ms.write_coils_async(1000, 3, bytearray([0x07])), 3)
            self.assertEqual(await ms.read_coils_async(1000, 3), bytearray([0x07]))
            self.assertEqual(await ms.write_coils_async(1000, 3, bytearray([0x00])), 3)
            self.assertEqual(await ms.read_coils_async(1000, 3), bytearray([0x00]))
            self.sl.stop()
            
        asyncio.run(self.run_coroutines([self.sl.run_async(), client_routine()]))


    def test_read_write_holding_register_async(self): 
        async def client_routine():
            ms = modbus_rtu_master(uart=serial.Serial("COM51"))
            self.assertEqual(await ms.write_holding_register_async(1000, bytearray([0xFF, 0xEE])), bytearray([0xFF, 0xEE]))
            self.assertEqual(await ms.read_holding_registers_async(1000, 1), bytearray([0xFF, 0xEE]))
            self.assertEqual(await ms.write_holding_register_async(1001, bytearray([0xFF, 0xEE])), bytearray([0xFF, 0xEE]))
            self.assertEqual(await ms.read_holding_registers_async(1000, 2), bytearray([0xFF, 0xEE, 0xFF, 0xEE]))
            self.sl.stop()

        asyncio.run(self.run_coroutines([self.sl.run_async(), client_routine()]))