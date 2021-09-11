# ToDo:
# - remove debug output
# - async
# - error messages
# - documentation

from mp_modbus_frame import modbus_rtu_frame, modbus_tcp_frame
import socket
import math

import os
mp = False
if hasattr(os, "uname") and os.uname().sysname in ["esp32"]:
    mp = True
    import uasyncio
else:
    import asyncio

class modbus_slave:
    def __init__(self, sl_type="tcp", context=None):
        self.sl_type = sl_type
        self.context = context
        self.forward_message = None

    def handle_message(self, frame):
        if self.context is None:
            if self.forward_message is not None:
                return self.forward_message(frame)
            return 
        db = {1: "co", 2: "di", 3: "hr", 4: "ir", 5:"co", 6:"hr", 15: "co", 16:"hr"}[frame.func_code]
        if frame.func_code in [1, 2, 3, 4]: 
            if db in self.context:
                if self._check_register(frame.register, frame.length, self.context[db]):
                    data = self._get_data(frame.register, frame.length, self.context[db])
                    if frame.func_code in [1,2]:
                        res = bytearray([0x00]*math.ceil(frame.length/8))
                        for i in range(frame.length):
                            if data[2*i: 2*i+2] == bytearray([0xFF, 0x00]):
                                res[i//8] |= 0x01<<(i%8)
                    else: 
                        res = data
                    if self.sl_type == "tcp":
                        return modbus_tcp_frame(
                            transaction_id=frame.transaction_id, unit_id=frame.unit_id, 
                            func_code=frame.func_code, fr_type="response", data=res) 
                    if self.sl_type == "rtu":
                        return modbus_rtu_frame(device_addr=frame.device_addr, 
                            func_code=frame.func_code, fr_type="response", data=res) 

        if frame.func_code in [5, 6, 15, 16]:
            if db in self.context:
                if frame.func_code in [5, 6]:
                    length = 1
                    data = frame.data
                if frame.func_code in [15]:
                    length = frame.length
                    data = bytearray([0x00, 0x00]*length)
                    for i in range(frame.length):
                        if frame.data[i//8] & 0x01<<(i%8) > 0:
                            data[2*i] = 0xFF
                if frame.func_code in [16]:
                    length = frame.length
                    data = frame.data
                if self._check_register(frame.register, length, self.context[db]):
                    self._set_data(frame.register, length, self.context[db], data)
                if frame.func_code in [5, 6]:
                    if self.sl_type == "tcp":
                        return modbus_tcp_frame(
                            transaction_id=frame.transaction_id, unit_id=frame.unit_id, register=frame.register,
                            func_code=frame.func_code, fr_type="response", data=data)
                    if self.sl_type == "rtu":
                        return modbus_rtu_frame(
                            device_addr=frame.device_addr, register=frame.register,
                            func_code=frame.func_code, fr_type="response", data=data)

                if frame.func_code in [15, 16]:
                    if self.sl_type == "tcp":
                        return modbus_tcp_frame(
                            transaction_id=frame.transaction_id, unit_id=frame.unit_id, register=frame.register,
                            func_code=frame.func_code, fr_type="response", length=frame.length) 
                    if self.sl_type == "rtu":
                        return modbus_rtu_frame(
                            device_addr=frame.device_addr, register=frame.register,
                            func_code=frame.func_code, fr_type="response", length=frame.length) 

    def _check_register(self, register, length, dataBlock):
        return (dataBlock["startAddr"] <= register) & (dataBlock["startAddr"] + len(dataBlock["registers"]) >= (register+length)) 
    
    def _get_data(self, register, length, data_Block):
        offset = register - data_Block["startAddr"]
        return data_Block["registers"][2*offset: 2*(offset+length)]

    def _set_data(self, register, length, data_Block, data):
        offset = ((register - data_Block["startAddr"]))
        for i in range(length*2):
            data_Block["registers"][2*offset+i] = data[i]     


class modbus_rtu_slave(modbus_slave):
    def __init__(self, uart, debug=True, *args, **kwargs):
        self.debug = debug
        self.uart = uart
        super(modbus_rtu_slave, self).__init__(sl_type="rtu" ,*args, **kwargs)
    
    async def run_async(self):
        if self.debug: print("starting async rtu slave")
        while True:
            if mp:
                pass
            else:
                if self.uart.any():
                    frame = self.uart.readline()
                    print(frame)


class modbus_tcp_server(modbus_slave):
    def __init__(self, host, port, debug=True, *args, **kwargs):
        self.host = host
        self.port = port
        self.debug = debug
        super(modbus_tcp_server, self).__init__(sl_type="tcp" ,*args, **kwargs)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        while True:
            conn, addr = sock.accept()
            if self.debug: print("new connection from {}".format(addr))
            while True:
                frame = conn.recv(256)
                if len(frame) > 0:
                    print(frame)
                    try:
                        res = self.handle_message(modbus_tcp_frame.parse_frame(frame)).get_frame()
                        print(res)
                        conn.send(res)
                    except:
                        break
                else:
                    break
            conn.close()

    async def run_async(self):
        if self.debug: print("starting async tcp server on port {}".format(self.port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        loop = asyncio.get_event_loop()
        sock.bind((self.host, self.port))
        sock.listen(5)
        sock.setblocking(False)
        while True:
            conn, addr = await loop.sock_accept(sock)
            if self.debug: print("new connection from {}".format(addr))
            while True:
                frame = await loop.sock_recv(conn, 256)
                if len(frame) > 0:
                    req = modbus_tcp_frame.parse_frame(frame)
                    if self.debug: print("received Frame        {}".format(req))
                    res = self.handle_message(req)
                    if self.debug: print("responding with Frame {}".format(res))
                    conn.send(res.get_frame())
                else:
                    if self.debug: print("shutting down async server")
                    break
            conn.close()
            