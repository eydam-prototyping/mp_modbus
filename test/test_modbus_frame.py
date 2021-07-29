import unittest
import mp_modbus

class Test(unittest.TestCase):
    def test_init1(self):
        f = mp_modbus.modbus_frame(desc={
            "type": "request",
            "device_addr": 1,
            "func_code": 3,
            "register": 3000,
            "length": 10
        })
        self.assertEqual(f.data, bytearray([0x01, 0x03, 0x0b, 0xb8, 0x00, 0x0a, 0x47, 0xcc]))

    def test_init2(self):
        test_list = [{
            "frame": bytearray([0x01, 0x03, 0x0b, 0xb8, 0x00, 0x0a, 0x47, 0xcc]),
            "type": "request", "addr": 1, "code": 3, "reg": 3000, "len": 10,
        },{
            "frame": bytearray([0x01, 0x03, 0x00, 0x12, 0x00, 0x08, 0xe4, 0x09]),
            "type": "request", "addr": 1, "code": 3, "reg": 18, "len": 8,
        },{
            "frame": bytearray([0x01, 0x02, 0x00, 0x12, 0x00, 0x08, 0xd9, 0xc9]),
            "type": "request", "addr": 1, "code": 2, "reg": 18, "len": 8,
        },{
            "frame": bytearray([0x01, 0x04, 0x00, 0x12, 0x00, 0x08, 0x51, 0xc9]),
            "type": "request", "addr": 1, "code": 4, "reg": 18, "len": 8,
        },{
            "frame": bytearray([0x01, 0x01, 0x00, 0x12, 0x00, 0x08, 0x9d, 0xc9]),
            "type": "request", "addr": 1, "code": 1, "reg": 18, "len": 8,
        },{
            "frame": bytearray([0x01, 0x0f, 0x00, 0x12, 0x00, 0x08, 0x01, 0xff, 0x06, 0xd6]),
            "type": "request", "addr": 1, "code": 15, "reg": 18, "len": 8, "data": bytearray([0xFF])
        },{
            "frame": bytearray([0x01, 0x10, 0x00, 0x12, 0x00, 0x08, 0x10, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0xd5, 0x51]),
            "type": "request", "addr": 1, "code": 16, "reg": 18, "len": 8, "data": bytearray([0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01])
        },{
            "frame": bytearray([0x01, 0x06, 0x00, 0x12, 0x00, 0x01, 0xe8, 0x0f]),
            "type": "both", "addr": 1, "code": 6, "reg": 18, "len": 1, "data": bytearray([0x00, 0x01])
        },{
            "frame": bytearray([0x01, 0x05, 0x00, 0x12, 0xff, 0x00, 0x2c, 0x3f]),
            "type": "both", "addr": 1, "code": 5, "reg": 18, "len": 1, "data": bytearray([0xFF, 0x00])
        },{
            "frame": bytearray([0x01, 0x03, 0x10, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x93, 0xb4]),
            "type": "response", "addr": 1, "code": 3, "byte_count": 16, "data": bytearray([0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01])
        },{
            "frame": bytearray([0x01, 0x02, 0x01, 0xff, 0xe1, 0xc8]),
            "type": "response", "addr": 1, "code": 2, "byte_count": 1, "data": bytearray([0xFF]),
        },{
            "frame": bytearray([0x01, 0x04, 0x10, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x22, 0xc1]),
            "type": "response", "addr": 1, "code": 4, "byte_count": 16, "data": bytearray([0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01]),
        },{
            "frame": bytearray([0x01, 0x01, 0x01, 0xff, 0x11, 0xc8]),
            "type": "response", "addr": 1, "code": 1, "byte_count": 1, "data": bytearray([0xFF]),
        },{
            "frame": bytearray([0x01, 0x0f, 0x00, 0x12, 0x00, 0x08, 0xf4, 0x08]),
            "type": "response", "addr": 1, "code": 15, "reg": 18, "len": 8,
        },{
            "frame": bytearray([0x01, 0x10, 0x00, 0x12, 0x00, 0x08, 0x61, 0xca]),
            "type": "response", "addr": 1, "code": 16, "reg": 18, "len": 8,
        },{
            "frame": bytearray([0x01, 0x06, 0x00, 0x12, 0x00, 0x01, 0xe8, 0x0f]),
            "type": "both", "addr": 1, "code": 6, "reg": 18, "data": bytearray([0x00, 0x01]),
        },{
            "frame": bytearray([0x01, 0x05, 0x00, 0x12, 0xff, 0x00, 0x2c, 0x3f]),
            "type": "both", "addr": 1, "code": 5, "reg": 18, "data": bytearray([0xFF, 0x00]),
        }]

        for test in test_list:
            f = mp_modbus.modbus_frame(frame=test["frame"])
            self.assertEqual(f.type, test["type"])
            self.assertEqual(f.device_addr, test["addr"])
            self.assertEqual(f.func_code, test["code"])

            if test["type"] == "request":
                self.assertEqual(f.register, test["reg"])
                self.assertEqual(f.length, test["len"])
                if test["code"] in [0x0F, 0x10]:
                    self.assertEqual(f.data, test["data"])

            if test["type"] == "response":
                if test["code"] in [0x01, 0x02, 0x03, 0x04]:
                    self.assertEqual(f.byte_count, test["byte_count"])
                    self.assertEqual(f.data, test["data"])
                if test["code"] in [0x0F, 0x10]:
                    self.assertEqual(f.length, test["len"])
            
            if test["type"] == "both":
                self.assertEqual(f.register, test["reg"])
                self.assertEqual(f.data, test["data"])



    