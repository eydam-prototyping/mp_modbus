import unittest
import mp_modbus
import threading

class Test(unittest.TestCase):
    def test_read_write_coil(self):
        cl = mp_modbus.modbus_tcp_client("127.0.0.1", 502)
        cl.connect()
        self.assertTrue(cl.write_coil(2, 1))
        self.assertEqual(cl.read_coils(2, 1)[0], 1)
        self.assertFalse(cl.write_coil(2, 0))
        self.assertEqual(cl.read_coils(2, 1)[0], 0)
        self.assertTrue(cl.write_coil(2, 1))
        self.assertTrue(cl.write_coil(3, 1))
        self.assertTrue(cl.write_coil(4, 1))
        self.assertTrue(cl.write_coil(5, 1))
        self.assertEqual(cl.read_coils(2, 4)[0], 0x0F)
        cl.disconnect()
        
    def test_read_inputs(self):
        cl = mp_modbus.modbus_tcp_client("127.0.0.1", 502)
        cl.connect()
        self.assertEqual(cl.read_digital_inputs(10,5)[0], 0x1F)
        cl.disconnect()
        
    def test_read_holding_registers(self):
        cl = mp_modbus.modbus_tcp_client("127.0.0.1", 502)
        cl.connect()
        self.assertEqual(cl.read_holding_registers(5,3), bytearray([0x00, 0x11, 0x00, 0x11, 0x00, 0x11]))
        cl.disconnect()
        
    def test_read_input_registers(self):
        cl = mp_modbus.modbus_tcp_client("127.0.0.1", 502)
        cl.connect()
        self.assertEqual(cl.read_input_registers(15,3), bytearray([0x00, 0x11, 0x00, 0x11, 0x00, 0x11]))
        cl.disconnect()
        
    def test_write_register(self):
        cl = mp_modbus.modbus_tcp_client("127.0.0.1", 502)
        cl.connect()
        self.assertEqual(cl.write_holding_register(20,bytearray([0x12, 0x34])), bytearray([0x12, 0x34]))
        cl.disconnect()
        
    def test_write_coils(self):
        cl = mp_modbus.modbus_tcp_client("127.0.0.1", 502)
        cl.connect()
        self.assertEqual(cl.write_coils(25, 15, bytearray([0x12, 0x34])), 15)
        cl.disconnect()
        
    def test_write_registers(self):
        cl = mp_modbus.modbus_tcp_client("127.0.0.1", 502)
        cl.connect()
        self.assertEqual(cl.write_registers(30, bytearray([0x12, 0x34, 0x56, 0x78])), 2)
        self.assertEqual(cl.write_registers(40, bytearray([0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC])), 3)
        cl.disconnect()

    def test_server_handle_message_1(self):
        srv = mp_modbus.modbus_tcp_server("", 0, context={"co":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)}})

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=1, register=1000, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x01]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=1, register=1001, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x02]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=1, register=1000, length=3, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x05]))

    def test_server_handle_message_2(self):
        srv = mp_modbus.modbus_tcp_server("", 0, context={"di":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)}})

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=2, register=1000, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x01]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=2, register=1001, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x02]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=2, register=1000, length=3, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x05]))

    def test_server_handle_message_3(self):
        srv = mp_modbus.modbus_tcp_server("", 0, context={"hr":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])}})

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=3, register=1000, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x00, 0x01, 0x02, 0x03]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=3, register=1001, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x02, 0x03, 0x04, 0x05]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=3, register=1000, length=3, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05]))

    def test_server_handle_message_4(self):
        srv = mp_modbus.modbus_tcp_server("", 0, context={"ir":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])}})

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=4, register=1000, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x00, 0x01, 0x02, 0x03]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=4, register=1001, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x02, 0x03, 0x04, 0x05]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=4, register=1000, length=3, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05]))

    def test_server_handle_message_5(self):
        srv = mp_modbus.modbus_tcp_server("", 0, context={"co":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00]*3)}})

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=5, register=1000, fr_type="request", data=bytearray([0xFF, 0x00]))
        srv.handle_message(msg)
        self.assertEqual(srv.context["co"]["registers"], bytearray([0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00]))
        
        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=5, register=1001, fr_type="request", data=bytearray([0x00, 0x00]))
        srv.handle_message(msg)
        self.assertEqual(srv.context["co"]["registers"], bytearray([0xFF, 0x00, 0x00, 0x00, 0xFF, 0x00]))

    def test_server_handle_message_6(self):
        srv = mp_modbus.modbus_tcp_server("", 0, context={"hr":{"startAddr": 1000, "registers": bytearray([0x00, 0x00]*3)}})

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=6, register=1000, fr_type="request", data=bytearray([0xFF, 0x00]))
        srv.handle_message(msg)
        self.assertEqual(srv.context["hr"]["registers"], bytearray([0xFF, 0x00, 0x00, 0x00, 0x00, 0x00]))
        
        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=6, register=1001, fr_type="request", data=bytearray([0xAB, 0xCD]))
        srv.handle_message(msg)
        self.assertEqual(srv.context["hr"]["registers"], bytearray([0xFF, 0x00, 0xAB, 0xCD, 0x00, 0x00]))

    def test_server_handle_message_15(self):
        srv = mp_modbus.modbus_tcp_server("", 0, context={"co":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00]*4)}})

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=15, register=1000, fr_type="request", data=bytearray([0x0f]), length=4)
        self.assertEqual(srv.handle_message(msg).get_frame(), bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x02, 0x0f, 0x03, 0xe8, 0x00, 0x04]))
        self.assertEqual(srv.context["co"]["registers"], bytearray([0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=15, register=1000, fr_type="request", data=bytearray([0x00]), length=2)
        self.assertEqual(srv.handle_message(msg).get_frame(), bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x02, 0x0f, 0x03, 0xe8, 0x00, 0x02]))
        self.assertEqual(srv.context["co"]["registers"], bytearray([0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00]))

    def test_server_handle_message_16(self):
        srv = mp_modbus.modbus_tcp_server("", 0, context={"hr":{"startAddr": 1000, "registers": bytearray([0x00, 0x00]*4)}})

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=16, register=1000, fr_type="request", data=bytearray([0xAB, 0xCD, 0x12, 0x34]), length=2)
        self.assertEqual(srv.handle_message(msg).get_frame(), bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x02, 0x10, 0x03, 0xe8, 0x00, 0x02]))
        self.assertEqual(srv.context["hr"]["registers"], bytearray([0xAB, 0xCD, 0x12, 0x34, 0x00, 0x00, 0x00, 0x00]))

        msg = mp_modbus.modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=16, register=1001, fr_type="request", data=bytearray([0xAB, 0xCD]), length=1)
        self.assertEqual(srv.handle_message(msg).get_frame(), bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x02, 0x10, 0x03, 0xe9, 0x00, 0x01]))
        self.assertEqual(srv.context["hr"]["registers"], bytearray([0xAB, 0xCD, 0xAB, 0xCD, 0x00, 0x00, 0x00, 0x00]))

    def test_tcp_server(self):
        srv = mp_modbus.modbus_tcp_server("127.0.0.1", 503, context={
            "co":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)},   # Coils: ON OFF ON OFF ON OFF ON OFF ON OFF
            "di":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)},   # Digital Inputs: ON OFF ON OFF ON OFF ON OFF ON OFF
            "hr":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])},
            "ir":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])}
        })
        t = threading.Thread(target=srv.run)
        t.start()
        cl = mp_modbus.modbus_tcp_client("127.0.0.1", 503)
        cl.connect()
        self.assertEqual(cl.read_coils(1000, 1), bytearray([0x01]))
        self.assertEqual(cl.read_coils(1001, 1), bytearray([0x00]))
        self.assertEqual(cl.read_coils(1000, 2), bytearray([0x01]))
        self.assertEqual(cl.read_coils(1001, 2), bytearray([0x02]))
        self.assertEqual(cl.read_coils(1000, 3), bytearray([0x05]))

        self.assertEqual(cl.write_coil(1001, 1), True)
        self.assertEqual(cl.read_coils(1000, 3), bytearray([0x07]))
        self.assertEqual(cl.write_coil(1001, 0), False)
        self.assertEqual(cl.read_coils(1000, 3), bytearray([0x05]))
        self.assertEqual(cl.write_coils(1000, 3, bytearray([0x07])), 3)
        self.assertEqual(cl.read_coils(1000, 3), bytearray([0x07]))
        self.assertEqual(cl.write_coils(1000, 3, bytearray([0x00])), 3)
        self.assertEqual(cl.read_coils(1000, 3), bytearray([0x00]))
    
        self.assertEqual(cl.read_digital_inputs(1000, 1), bytearray([0x01]))
        self.assertEqual(cl.read_digital_inputs(1000, 2), bytearray([0x01]))
        self.assertEqual(cl.read_digital_inputs(1000, 3), bytearray([0x05]))
        self.assertEqual(cl.read_digital_inputs(1001, 1), bytearray([0x00]))
        self.assertEqual(cl.read_digital_inputs(1001, 2), bytearray([0x02]))
        self.assertEqual(cl.read_digital_inputs(1001, 3), bytearray([0x02]))

        self.assertEqual(cl.read_holding_registers(1000, 1), bytearray([0x00, 0x01]))
        self.assertEqual(cl.read_holding_registers(1000, 2), bytearray([0x00, 0x01, 0x02, 0x03]))
        self.assertEqual(cl.read_holding_registers(1001, 2), bytearray([0x02, 0x03, 0x04, 0x05]))
        self.assertEqual(cl.read_holding_registers(1002, 3), bytearray([0x04, 0x05, 0x06, 0x07, 0x08, 0x09]))

        self.assertEqual(cl.write_holding_register(1000, bytearray([0xFF, 0xEE])), bytearray([0xFF, 0xEE]))
        self.assertEqual(cl.read_holding_registers(1000, 1), bytearray([0xFF, 0xEE]))
        self.assertEqual(cl.write_holding_register(1001, bytearray([0xFF, 0xEE])), bytearray([0xFF, 0xEE]))
        self.assertEqual(cl.read_holding_registers(1000, 2), bytearray([0xFF, 0xEE, 0xFF, 0xEE]))

        self.assertEqual(cl.read_input_registers(1000, 1), bytearray([0x00, 0x01]))
        self.assertEqual(cl.read_input_registers(1000, 2), bytearray([0x00, 0x01, 0x02, 0x03]))
        self.assertEqual(cl.read_input_registers(1001, 2), bytearray([0x02, 0x03, 0x04, 0x05]))
        self.assertEqual(cl.read_input_registers(1002, 3), bytearray([0x04, 0x05, 0x06, 0x07, 0x08, 0x09]))

        cl.disconnect()
        