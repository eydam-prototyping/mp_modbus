import time
import os
try:
    import machine
except:
    pass
import struct

class modbus_frame:
    def __init__(self, desc=None, frame=None):
        if (desc is not None) and (frame is not None):
            raise ValueError("Either desc or frame is allowed")
        
        self.type = None        # request or response
        self.device_addr = -1
        self.func_code = -1
        self.overhang = None

        if desc is not None:
            self.device_addr = desc.get("device_addr", 1)
            self.func_code = desc.get("func_code", 3)
            self.type = desc.get("type", "request")
            if self.type == "request":
                self.register = desc.get("register", 100)
                self.length = desc.get("length", 1)
            elif self.type == "response":
                pass
            else:
                raise ValueError("type must be 'request' or 'response'")
            self._create_frame()

        if frame is not None:
            if len(frame) >= 6:
                self.device_addr = frame[0]
                self.func_code = frame[1]
                self.type = None
                self.overhang = bytearray()
                self.frame = frame
                if self._check_request(frame):
                    self.type = "request"
                    if self.func_code in [0x05, 0x06]:
                        self.type = "both"
                    if self.func_code in [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]:
                        self.register = (frame[2] << 8)+frame[3]
                        if self.func_code in [0x05, 0x06]:
                            self.data = frame[4:6]
                            self.length = 1
                        else:
                            self.length = (frame[4] << 8)+frame[5]
                        self.crc = (frame[7] << 8)+frame[6]
                        self.overhang = frame[8:]
                    if self.func_code in [0x10, 0x0F]:
                        self.register = (frame[2] << 8)+frame[3]
                        self.length = (frame[4] << 8)+frame[5]
                        self.byte_count = frame[6]
                        self.data = frame[7:7+self.byte_count]
                        self.crc = (frame[8+self.byte_count]
                                    << 8)+frame[7+self.byte_count]
                        self.overhang = frame[9+self.byte_count:]
                elif self._check_response(frame):
                    self.type = "response"
                    if self.func_code in [0x01, 0x02, 0x03, 0x04]:
                        self.byte_count = frame[2]
                        self.data = frame[3:3+self.byte_count]
                        self.crc = (frame[4+self.byte_count]
                                    << 8)+frame[3+self.byte_count]
                        self.overhang = frame[5+self.byte_count:]
                    if self.func_code in [0x10, 0x0F]:
                        self.register = (frame[2] << 8)+frame[3]
                        self.length = (frame[4] << 8)+frame[5]
                        self.crc = (frame[7] << 8)+frame[6]
                        self.overhang = frame[8:]

            else:
                self.overhang = frame
                self.type = None

    def _check_request(self, frame):
        try:
            if self.func_code in [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]:
                return self._crc16(frame[0:6]) == (frame[7] << 8)+frame[6]
            if self.func_code in [0x10, 0x0F]:
                bc = frame[6]
                if len(frame) >= 8+bc:
                    return self._crc16(frame[0:7+bc]) == (frame[8+bc] << 8)+frame[7+bc]
                else:
                    return False
        except:
            return False

    def _check_response(self, frame):
        try:
            if self.func_code in [0x01, 0x02, 0x03, 0x04]:
                bc = frame[2]
                if len(frame) >= bc + 5:
                    return self._crc16(frame[0:3+bc]) == (frame[4+bc] << 8)+frame[3+bc]
            if self.func_code in [0x10, 0x0F]:
                return self._crc16(frame[0:6]) == (frame[7] << 8)+frame[6]
        except:
            return False

    def _create_frame(self):
        self.data = bytearray()
        self.data += bytearray([self.device_addr])
        self.data += bytearray([self.func_code])
        self.data += bytearray([self.register >> 8, self.register & 0xFF])
        self.data += bytearray([self.length >> 8, self.length & 0xFF])
        crc = self._crc16(self.data)
        self.data += bytearray([crc & 0xFF, crc >> 8])

    def _crc16(self, data):
        offset = 0
        length = len(data)
        if data is None or offset < 0 or offset > len(data) - 1 and offset+length > len(data):
            return 0
        crc = 0xFFFF
        for i in range(0, length):
            crc ^= data[offset + i]
            for j in range(0, 8):
                if (crc & 1) > 0:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1
        return crc

    def __str__(self):
        return "<modbus_frame type: {}, addr: {}, func: {}>".format(self.type, self.device_addr, self.func_code)

    def print_data(self):
        print(" ".join(["{:02x}".format(x) for x in self.data]))
        
class modbus_slave:
    def __init__(self, device_addr, controller, table):
        self.device_addr = device_addr
        self.controller = controller
        self.table = table

    def read_holding_register(self, register, length):
        frame = modbus_frame(desc={
            "type": "request",
            "device_addr": self.device_addr,
            "func_code": 3,
            "register": register,
            "length": length
        })
        response = self.controller._request(frame)
        if response is not None:
            return modbus_frame(frame=response)
        else:
            raise Exception("Timeout!")

    def read_value(self, register, type="float", gain=1):
        length = 1
        if type in ["float", "int32", "uint32"]: 
            length = 2
        
        m = self.read_holding_register(register, length)

        if type == "float":
            return struct.unpack(">f", m.data)[0]/gain
        if type == "uint16":
            return struct.unpack(">h", m.data)[0]/gain
        if type == "int32":
            return struct.unpack(">I", m.data)[0]/gain
        if type == "uint32":
            return struct.unpack(">i", m.data)[0]/gain

    def read_value_by_name(self, name):
        if name in self.table:
            return self.read_value(self.table[name]["register"],self.table[name]["type"],self.table[name]["gain"])
        else:
            return None

    def read_all_values(self):
        data = {}
        for key in self.table:
            data[key] = self.read_value_by_name(key)
        return data

class modbus_controller:
    def __init__(self, desc, mode="master"):
        self.mode = desc.get("mode", "RTU")
        self.response_timeout = 1
        self.slaves = []
        if self.mode == "RTU":
            self.baudrate = desc.get("baudrate", 9600)
            self.parity = desc.get("parity", None)
            self.tx_pin = desc.get("tx", 14)
            self.rx_pin = desc.get("rx", 13)
            self.en_pin = machine.Pin(desc.get("en", 15), machine.Pin.OUT) 
            self.uart = machine.UART(1, self.baudrate)
            self.uart.init(baudrate=self.baudrate, bits=8, parity=self.parity, stop=1, tx=self.tx_pin, rx=self.rx_pin)

    def _request(self, frame):
        if self.mode == "RTU":
            self.en_pin.value(1)
            self.uart.write(frame.data)
            t = len(frame.data)*9/self.baudrate
            time.sleep(t+.01)   # wait until data is send
            self.en_pin.value(0)
            i = 0
            time.sleep(0.05)
            while (self.uart.any()==0) & (i<self.response_timeout):
                time.sleep(0.05)
                i+=0.05
            if self.uart.any() > 0:
                res = self.uart.readline()
                return res
            else:
                return None

    def create_slave(self, device_addr, table):
        s = modbus_slave(device_addr, self, table)
        self.slaves.append(s)
        return s

    

if __name__ == "__main__":
    f = modbus_frame()
    print(f)