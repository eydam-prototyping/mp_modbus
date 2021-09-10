import unittest
from mp_modbus_slave import modbus_tcp_server
from mp_modbus_frame import modbus_tcp_frame

class Test(unittest.TestCase):
    def test_server_handle_message_1(self):
        srv = modbus_tcp_server("", 0, context={"co":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)}})

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=1, register=1000, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x01]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=1, register=1001, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x02]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=1, register=1000, length=3, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x05]))

    def test_server_handle_message_2(self):
        srv = modbus_tcp_server("", 0, context={"di":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00, 0x00, 0x00]*5)}})

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=2, register=1000, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x01]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=2, register=1001, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x02]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=2, register=1000, length=3, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x05]))

    def test_server_handle_message_3(self):
        srv = modbus_tcp_server("", 0, context={"hr":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])}})

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=3, register=1000, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x00, 0x01, 0x02, 0x03]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=3, register=1001, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x02, 0x03, 0x04, 0x05]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=3, register=1000, length=3, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05]))

    def test_server_handle_message_4(self):
        srv = modbus_tcp_server("", 0, context={"ir":{"startAddr": 1000, "registers": bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])}})

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=4, register=1000, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x00, 0x01, 0x02, 0x03]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=4, register=1001, length=2, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x02, 0x03, 0x04, 0x05]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=4, register=1000, length=3, fr_type="request")
        self.assertEqual(srv.handle_message(msg).data, bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05]))

    def test_server_handle_message_5(self):
        srv = modbus_tcp_server("", 0, context={"co":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00]*3)}})

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=5, register=1000, fr_type="request", data=bytearray([0xFF, 0x00]))
        srv.handle_message(msg)
        self.assertEqual(srv.context["co"]["registers"], bytearray([0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00]))
        
        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=5, register=1001, fr_type="request", data=bytearray([0x00, 0x00]))
        srv.handle_message(msg)
        self.assertEqual(srv.context["co"]["registers"], bytearray([0xFF, 0x00, 0x00, 0x00, 0xFF, 0x00]))

    def test_server_handle_message_6(self):
        srv = modbus_tcp_server("", 0, context={"hr":{"startAddr": 1000, "registers": bytearray([0x00, 0x00]*3)}})

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=6, register=1000, fr_type="request", data=bytearray([0xFF, 0x00]))
        srv.handle_message(msg)
        self.assertEqual(srv.context["hr"]["registers"], bytearray([0xFF, 0x00, 0x00, 0x00, 0x00, 0x00]))
        
        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=6, register=1001, fr_type="request", data=bytearray([0xAB, 0xCD]))
        srv.handle_message(msg)
        self.assertEqual(srv.context["hr"]["registers"], bytearray([0xFF, 0x00, 0xAB, 0xCD, 0x00, 0x00]))

    def test_server_handle_message_15(self):
        srv = modbus_tcp_server("", 0, context={"co":{"startAddr": 1000, "registers": bytearray([0xFF, 0x00]*4)}})

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=15, register=1000, fr_type="request", data=bytearray([0x0f]), length=4)
        self.assertEqual(srv.handle_message(msg).get_frame(), bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x02, 0x0f, 0x03, 0xe8, 0x00, 0x04]))
        self.assertEqual(srv.context["co"]["registers"], bytearray([0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=15, register=1000, fr_type="request", data=bytearray([0x00]), length=2)
        self.assertEqual(srv.handle_message(msg).get_frame(), bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x02, 0x0f, 0x03, 0xe8, 0x00, 0x02]))
        self.assertEqual(srv.context["co"]["registers"], bytearray([0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00]))

    def test_server_handle_message_16(self):
        srv = modbus_tcp_server("", 0, context={"hr":{"startAddr": 1000, "registers": bytearray([0x00, 0x00]*4)}})

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=16, register=1000, fr_type="request", data=bytearray([0xAB, 0xCD, 0x12, 0x34]), length=2)
        self.assertEqual(srv.handle_message(msg).get_frame(), bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x02, 0x10, 0x03, 0xe8, 0x00, 0x02]))
        self.assertEqual(srv.context["hr"]["registers"], bytearray([0xAB, 0xCD, 0x12, 0x34, 0x00, 0x00, 0x00, 0x00]))

        msg = modbus_tcp_frame(transaction_id=1, unit_id=2, func_code=16, register=1001, fr_type="request", data=bytearray([0xAB, 0xCD]), length=1)
        self.assertEqual(srv.handle_message(msg).get_frame(), bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x02, 0x10, 0x03, 0xe9, 0x00, 0x01]))
        self.assertEqual(srv.context["hr"]["registers"], bytearray([0xAB, 0xCD, 0xAB, 0xCD, 0x00, 0x00, 0x00, 0x00]))