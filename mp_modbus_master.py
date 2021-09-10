# ToDo:
# - remove debug output
# - async
# - error messages
# - documentation
# - modbus master (rtu) -> factory for slaves

from mp_modbus_frame import modbus_rtu_frame, modbus_tcp_frame
import socket
import time

import os
mp = False
if hasattr(os, "uname") and os.uname().sysname in ["esp32"]:
    import machine
    import uasyncio
    import gc
    mp = True
else:
    import asyncio

class modbus_master:
    def __init__(self, ms_type="tcp"):
        self.ms_type = ms_type
        self.stream = None

    def read_coils(self, register, length):
        return self._read_registers(register, length, 1)

    async def read_coils_async(self, register, length):
        return await self._read_registers_async(register, length, 1)

    def read_digital_inputs(self, register, length):
        return self._read_registers(register, length, 2)

    async def read_digital_inputs_async(self, register, length):
        return await self._read_registers_async(register, length, 2)

    def read_holding_registers(self, register, length):
        return self._read_registers(register, length, 3)

    async def read_holding_registers_async(self, register, length):
        return await self._read_registers_async(register, length, 3)

    def read_input_registers(self, register, length):
        return self._read_registers(register, length, 4)

    async def read_input_registers_async(self, register, length):
        return await self._read_registers_async(register, length, 4)

    def _read_registers(self, register, length, code):
        if self.ms_type == "tcp":
            f = modbus_tcp_frame(transaction_id=self.ti, func_code=code, register=register, fr_type="request", length=length)
            self.sock.send(f.get_frame())
            resp = self.sock.recv(256) 
            resp_frame = modbus_tcp_frame.parse_frame(resp)
            self.ti += 1
        elif self.ms_type == "rtu":
            if mp:
                f = modbus_rtu_frame(device_addr=self.device_addr, func_code=code, register=register, fr_type="request", length=length)
                self.en_pin.value(1)
                self.uart.write(f.get_frame())
                t = len(f.get_frame())*9/self.baudrate
                time.sleep(t+.01)   # wait until data is send
                self.en_pin.value(0)
                i = 0
                time.sleep(0.05)
                while (self.uart.any()==0) & (i<1):
                    time.sleep(0.05)
                    i+=0.05
                if self.uart.any() > 0:
                    resp = self.uart.readline()
                    resp_frame = modbus_rtu_frame.parse_frame(resp, fr_type="response")
                else:
                    # Timeout
                    pass
        return resp_frame

    async def _read_registers_async(self, register, length, code):
        loop = uasyncio.get_event_loop()
        if self.ms_type == "tcp":
            f = modbus_tcp_frame(transaction_id=self.ti, func_code=code, register=register, fr_type="request", length=length)
            self.sock.send(f.get_frame())
            resp = await loop.sock_recv(self.sock, 256)
            resp_frame = modbus_tcp_frame.parse_frame(resp)
            self.ti += 1
        elif self.ms_type == "rtu":
            f = modbus_rtu_frame(device_addr=self.device_addr, func_code=code, register=register, fr_type="request", length=length)
            print(1)
            self.en_pin.value(1)
            #self.uart.write(f.get_frame())
            await self.writer.awrite(f.get_frame())
            print(2)
            t = len(f.get_frame())*9/self.baudrate
            await uasyncio.sleep(t+.01)   # wait until data is send
            print(3)
            self.en_pin.value(0)
            i = 0
            await uasyncio.sleep(0.05)
            print(4)
            while (self.uart.any()==0) & (i<1):
                print(5)
                await uasyncio.sleep(0.05)
                i+=0.05
            if self.uart.any() > 0:
                resp = await self.reader.readline()
                print(6)
                resp_frame = modbus_rtu_frame.parse_frame(resp, fr_type="response")
            else:
                # Timeout
                pass
        return resp_frame.data

    def write_coil(self, register, value):
        if value in [True, 1, "on", "ON", "On"]:
            data = bytearray([0xFF, 0x00])
        elif value in [False, 0, "off", "OFF", "Off"]:
            data = bytearray([0x00, 0x00])
        else:
            raise ValueError("cannot write coil value {}".format(value))
        res = self._write_registers(register, 1, data, 5)
        return res == bytearray([0xFF, 0x00])

    async def write_coil_async(self, register, value):
        if value in [True, 1, "on", "ON", "On"]:
            data = bytearray([0xFF, 0x00])
        elif value in [False, 0, "off", "OFF", "Off"]:
            data = bytearray([0x00, 0x00])
        else:
            raise ValueError("cannot write coil value {}".format(value))
        res = await self._write_registers_async(register, 1, data, 5)
        return res == bytearray([0xFF, 0x00])

    def write_holding_register(self, register, value):
        return self._write_registers(register, 0, value, 6)

    async def write_holding_register_async(self, register, value):
        return await self._write_registers_async(register, 0, value, 6)

    def write_coils(self, register, count, value):
        return self._write_registers(register, count, value, 15)

    async def write_coils_async(self, register, count, value):
        return await self._write_registers_async(register, count, value, 15)

    def write_registers(self, register, value):
        return self._write_registers(register, len(value)//2, value, 16)

    async def write_registers_async(self, register, value):
        return await self._write_registers_async(register, len(value)//2, value, 16)

    def _write_registers(self, register, length, value, code):
        f = None
        if code in [0x05, 0x06]:
            f = modbus_tcp_frame(transaction_id=self.ti, func_code=code, register=register, fr_type="request", data=value)
        if code in [0x0F, 0x10]:
            f = modbus_tcp_frame(transaction_id=self.ti, func_code=code, register=register, fr_type="request", data=value, length=length)
        self.sock.send(f.get_frame())
        resp = self.sock.recv(256)
        resp_frame = modbus_tcp_frame.parse_frame(resp)
        self.ti += 1
        if resp_frame.func_code in [0x05, 0x06]:
            return resp_frame.data
        if resp_frame.func_code in [0x0F, 0x10]:
            return resp_frame.length
        if resp_frame.func_code in [0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
            txt = {
                1: "ILLEGAL_FUNCTION", 2: "ILLEGAL_DATA_ADDRESS", 3: "ILLEGAL_DATA_VALUE", 4: "SLAVE_DEVICE_FAILURE", 5: "ACKNOWLEDGE", 
                6: "SLAVE_DEVICE_BUSY", 7: "NEGATIVE_ACKNOWLEDGE", 8: "MEMORY_PARITY_ERROR", 10: "GATEWAY_PATH_UNAVAILABLE", 
                11: "GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND"}[resp_frame.error_code]
            raise ValueError("Received Error Frame (Function Code: {:02x}, Exception Code: {:02x}, {})".format(resp_frame.func_code, resp_frame.error_code, txt))

    async def _write_registers_async(self, register, length, value, code):
        loop = uasyncio.get_event_loop()
        f = None
        if code in [0x05, 0x06]:
            f = modbus_tcp_frame(transaction_id=self.ti, func_code=code, register=register, fr_type="request", data=value)
        if code in [0x0F, 0x10]:
            f = modbus_tcp_frame(transaction_id=self.ti, func_code=code, register=register, fr_type="request", data=value, length=length)
        self.sock.send(f.get_frame())
        resp = await loop.sock_recv(self.sock, 256)
        resp_frame = modbus_tcp_frame.parse_frame(resp)
        self.ti += 1
        if resp_frame.func_code in [0x05, 0x06]:
            return resp_frame.data
        if resp_frame.func_code in [0x0F, 0x10]:
            return resp_frame.length
        if resp_frame.func_code in [0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
            txt = {
                1: "ILLEGAL_FUNCTION", 2: "ILLEGAL_DATA_ADDRESS", 3: "ILLEGAL_DATA_VALUE", 4: "SLAVE_DEVICE_FAILURE", 5: "ACKNOWLEDGE", 
                6: "SLAVE_DEVICE_BUSY", 7: "NEGATIVE_ACKNOWLEDGE", 8: "MEMORY_PARITY_ERROR", 10: "GATEWAY_PATH_UNAVAILABLE", 
                11: "GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND"}[resp_frame.error_code]
            raise ValueError("Received Error Frame (Function Code: {:02x}, Exception Code: {:02x}, {})".format(resp_frame.func_code, resp_frame.error_code, txt))
    

class modbus_tcp_client(modbus_master):
    def __init__(self, host, port, *args, **kwargs):
        self.host = host
        self.port = port
        self.connected = False
        self.ti = 1
        self.transactions = {}
        super(modbus_tcp_client, self).__init__(ms_type="tcp" ,*args, **kwargs)

    def connect(self):
        if not self.connected:    
            self.sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
    
    def disconnect(self):
        if self.connected:
            self.sock.close()
            self.connected = False


class modbus_rtu_master(modbus_master):
    def __init__(self, uart_no=1, baudrate=9600, bits=8, stop=1, parity=None, tx_pin=14, rx_pin=13, en_pin=15, uart=None, device_addr=1, *args, **kwargs):
        super(modbus_rtu_master, self).__init__(ms_type="rtu" ,*args, **kwargs)
        self.device_addr = device_addr
        self.baudrate = baudrate
        self.en_pin = machine.Pin(en_pin, machine.Pin.OUT)
        if uart is None:
            self.uart = machine.UART(uart_no, baudrate, tx=tx_pin, rx=rx_pin)
            self.uart.init(baudrate=baudrate, bits=bits, parity=parity, stop=stop, tx=tx_pin, rx=rx_pin, timeout=30, timeout_char=30, rxbuf=1024)
        else:
            self.uart = uart
        self.writer = uasyncio.StreamWriter(self.uart, {})
        self.reader = uasyncio.StreamReader(self.uart)