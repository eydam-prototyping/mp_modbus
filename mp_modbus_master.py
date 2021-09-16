# ToDo:
# - remove debug output
# - async
# - error messages
# - documentation
# - modbus master (rtu) -> factory for slaves

from mp_modbus_frame import modbus_frame, modbus_rtu_frame, modbus_tcp_frame
import socket
import time

import os
mp = False
if hasattr(os, "uname") and os.uname().sysname in ["esp32"]:
    import machine
    import uasyncio as asyncio
    import gc
    mp = True
else:
    import asyncio


class modbus_master:
    def __init__(self, ms_type: str = "tcp"):
        self.ms_type = ms_type

    def _send(self, frame: modbus_frame) -> modbus_frame:
        """MUST BE OVERRIDDEN

        Args:
            frame (modbus_frame): the frame to send

        Returns:
            modbus_frame: response
        """
        pass

    async def _send_async(self, frame: modbus_frame) -> modbus_frame:
        """MUST BE OVERRIDDEN (async)

        Args:
            frame (modbus_frame): the frame to send

        Returns:
            modbus_frame: response
        """
        pass

    def read_coils(self, register: int, length: int) -> bytearray:
        """Read a number (length) of coils

        Args:
            register (int): start register
            length (int): number of coils

        Returns:
            bytearray: response
        """
        return self._read_registers(register, length, 1)

    async def read_coils_async(self, register: int, length: int) -> bytearray:
        """Read a number (length) of coils (async)

        Args:
            register (int): start register
            length (int): number of coils

        Returns:
            bytearray: response
        """
        return await self._read_registers_async(register, length, 1)

    def read_digital_inputs(self, register: int, length: int) -> bytearray:
        """Read a number (length) of digital inputs

        Args:
            register (int): start register
            length (int): number of inputs

        Returns:
            bytearray: response
        """
        return self._read_registers(register, length, 2)

    async def read_digital_inputs_async(self, register: int, length: int) -> bytearray:
        """Read a number (length) of digital inputs (async)

        Args:
            register (int): start register
            length (int): number of inputs

        Returns:
            bytearray: response
        """
        return await self._read_registers_async(register, length, 2)

    def read_holding_registers(self, register: int, length: int) -> bytearray:
        """Read a number (length) of holding registers

        Args:
            register (int): start register
            length (int): number of holding registers

        Returns:
            bytearray: response
        """
        return self._read_registers(register, length, 3)

    async def read_holding_registers_async(self, register: int, length: int) -> bytearray:
        """Read a number (length) of holding registers (async)

        Args:
            register (int): start register
            length (int): number of holding registers

        Returns:
            bytearray: response
        """
        return await self._read_registers_async(register, length, 3)

    def read_input_registers(self, register: int, length: int) -> bytearray:
        """Read a number (length) of input registers

        Args:
            register (int): start register
            length (int): number of input registers

        Returns:
            bytearray: response
        """
        return self._read_registers(register, length, 4)

    async def read_input_registers_async(self, register: int, length: int) -> bytearray:
        """Read a number (length) of input registers (async)

        Args:
            register (int): start register
            length (int): number of input registers

        Returns:
            bytearray: response
        """
        return await self._read_registers_async(register, length, 4)

    def _read_registers(self, register: int, length: int, code: int) -> bytearray:
        """private helper function

        Args:
            register (int): start register
            length (int): number of registers
            code (int): function code

        Returns:
            bytearray: response
        """
        if self.ms_type == "tcp":
            f = modbus_tcp_frame(transaction_id=self.ti, func_code=code,
                                 register=register, fr_type="request", length=length)
            resp = self._send(self, f.get_frame())
            resp_frame = modbus_tcp_frame.parse_frame(resp)
            self.ti += 1
        elif self.ms_type == "rtu":
            f = modbus_rtu_frame(device_addr=self.device_addr, func_code=code,
                                 register=register, fr_type="request", length=length)
            resp = self._send(f.get_frame())
            resp_frame = modbus_rtu_frame.parse_frame(resp, fr_type="response")

        return resp_frame.data

    async def _read_registers_async(self, register: int, length: int, code: int) -> bytearray:
        """private helper function (asnc)

        Args:
            register (int): start register
            length (int): number of registers
            code (int): function code

        Returns:
            bytearray: response
        """
        if self.ms_type == "tcp":
            f = modbus_tcp_frame(transaction_id=self.ti, func_code=code,
                                 register=register, fr_type="request", length=length)
            resp = await self._send_async(f.get_frame())
            resp_frame = modbus_tcp_frame.parse_frame(resp)
            self.ti += 1
        elif self.ms_type == "rtu":
            f = modbus_rtu_frame(device_addr=self.device_addr, func_code=code,
                                 register=register, fr_type="request", length=length)
            resp = await self._send_async(f.get_frame())
            resp_frame = modbus_rtu_frame.parse_frame(resp, fr_type="response")

        return resp_frame.data

    def write_coil(self, register: int, value: bool or int or str) -> bool:
        """Write a coil

        Args:
            register (int): register of the coil
            value (bool or int or str): True/1/"on"/"ON"/"On" or False/0/"off"/"OFF"/"Off" 

        Raises:
            ValueError: if value is not valid
            ValueError: if coil can't be written

        Returns:
            bool: The value of the coil
        """
        if value in [True, 1, "on", "ON", "On"]:
            data = bytearray([0xFF, 0x00])
        elif value in [False, 0, "off", "OFF", "Off"]:
            data = bytearray([0x00, 0x00])
        else:
            raise ValueError("cannot write coil value {}".format(value))
        res = self._write_registers(register, 1, data, 5)
        return res == bytearray([0xFF, 0x00])

    async def write_coil_async(self, register: int, value: bool or int or str) -> bool:
        """Write a coil (async)

        Args:
            register (int): register of the coil
            value (bool or int or str): True/1/"on"/"ON"/"On" or False/0/"off"/"OFF"/"Off" 

        Raises:
            ValueError: if value is not valid
            ValueError: if coil can't be written

        Returns:
            bool: The value of the coil
        """
        if value in [True, 1, "on", "ON", "On"]:
            data = bytearray([0xFF, 0x00])
        elif value in [False, 0, "off", "OFF", "Off"]:
            data = bytearray([0x00, 0x00])
        else:
            raise ValueError("cannot write coil value {}".format(value))
        res = await self._write_registers_async(register, 1, data, 5)
        return res == bytearray([0xFF, 0x00])

    def write_holding_register(self, register: int, value: bytearray) -> bytearray:
        """Write a holding register

        Args:
            register (int): register of the holding register
            value (bytearray): value

        Raises:
            ValueError: if register can't be written

        Returns:
            bytearray: the written value
        """
        return self._write_registers(register, 0, value, 6)

    async def write_holding_register_async(self, register: int, value: bytearray) -> bytearray:
        """Write a holding register (async)

        Args:
            register (int): register of the holding register
            value (bytearray): value

        Raises:
            ValueError: if register can't be written

        Returns:
            bytearray: the written value
        """
        return await self._write_registers_async(register, 0, value, 6)

    def write_coils(self, register: int, count: int, value: bytearray) -> bytearray:
        """Write multiple coils

        Args:
            register (int): start register of the coils
            count (int): number of coils
            value (bytearray): value

        Raises:
            ValueError: if coils can't be written

        Returns:
            bytearray: the value of the coils
        """
        return self._write_registers(register, count, value, 15)

    async def write_coils_async(self, register: int, count: int, value: bytearray) -> bytearray:
        """Write multiple coils (async)

        Args:
            register (int): start register of the coils
            count (int): number of coils
            value (bytearray): value

        Raises:
            ValueError: if coils can't be written

        Returns:
            bytearray: the value of the coils
        """
        return await self._write_registers_async(register, count, value, 15)

    def write_registers(self, register: int, value: bytearray) -> bytearray:
        """Write multiple registers

        Args:
            register (int): start register
            value (bytearray): value

        Raises:
            ValueError: if registers can't be written

        Returns:
            bytearray: the written value
        """
        return self._write_registers(register, len(value)//2, value, 16)

    async def write_registers_async(self, register: int, value: bytearray) -> bytearray:
        """Write multiple registers (async)

        Args:
            register (int): start register
            value (bytearray): value

        Raises:
            ValueError: if registers can't be written

        Returns:
            bytearray: the written value
        """
        return await self._write_registers_async(register, len(value)//2, value, 16)

    def _write_registers(self, register: int, length: int, value: bytearray, code: int) -> bytearray or int:
        """Helper function

        Args:
            register (int): register
            length (int): length
            value (bytearray): value
            code (int): function code

        Raises:
            ValueError: if value can't be written

        Returns:
            bytearray or int: data or length (depending on function code)
        """
        f = None
        if self.ms_type == "tcp":
            if code in [0x05, 0x06]:
                f = modbus_tcp_frame(transaction_id=self.ti, func_code=code,
                                     register=register, fr_type="request", data=value)
            if code in [0x0F, 0x10]:
                f = modbus_tcp_frame(transaction_id=self.ti, func_code=code,
                                     register=register, fr_type="request", data=value, length=length)
            self.ti += 1
        elif self.ms_type == "rtu":
            if code in [0x05, 0x06]:
                f = modbus_rtu_frame(
                    func_code=code, register=register, fr_type="request", data=value)
            if code in [0x0F, 0x10]:
                f = modbus_rtu_frame(
                    func_code=code, register=register, fr_type="request", data=value, length=length)

        resp = self._send(self, f.get_frame())

        if self.ms_type == "tcp":
            resp_frame = modbus_tcp_frame.parse_frame(resp)
        elif self.ms_type == "rtu":
            resp_frame = modbus_rtu_frame.parse_frame(resp)

        if resp_frame.func_code in [0x05, 0x06]:
            return resp_frame.data
        if resp_frame.func_code in [0x0F, 0x10]:
            return resp_frame.length
        if resp_frame.func_code in [0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
            txt = {
                1: "ILLEGAL_FUNCTION", 2: "ILLEGAL_DATA_ADDRESS", 3: "ILLEGAL_DATA_VALUE", 4: "SLAVE_DEVICE_FAILURE", 5: "ACKNOWLEDGE",
                6: "SLAVE_DEVICE_BUSY", 7: "NEGATIVE_ACKNOWLEDGE", 8: "MEMORY_PARITY_ERROR", 10: "GATEWAY_PATH_UNAVAILABLE",
                11: "GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND"}[resp_frame.error_code]
            raise ValueError("Received Error Frame (Function Code: {:02x}, Exception Code: {:02x}, {})".format(
                resp_frame.func_code, resp_frame.error_code, txt))

    async def _write_registers_async(self, register: int, length: int, value: bytearray, code: int) -> bytearray or int:
        """Helper function (async)

        Args:
            register (int): register
            length (int): length
            value (bytearray): value
            code (int): function code

        Raises:
            ValueError: if value can't be written

        Returns:
            bytearray or int: data or length (depending on function code)
        """
        f = None
        if self.ms_type == "tcp":
            if code in [0x05, 0x06]:
                f = modbus_tcp_frame(transaction_id=self.ti, func_code=code,
                                     register=register, fr_type="request", data=value)
            if code in [0x0F, 0x10]:
                f = modbus_tcp_frame(transaction_id=self.ti, func_code=code,
                                     register=register, fr_type="request", data=value, length=length)
            self.ti += 1
        elif self.ms_type == "rtu":
            if code in [0x05, 0x06]:
                f = modbus_rtu_frame(
                    func_code=code, register=register, fr_type="request", data=value)
            if code in [0x0F, 0x10]:
                f = modbus_rtu_frame(
                    func_code=code, register=register, fr_type="request", data=value, length=length)

        resp = await self._send_async(f.get_frame())

        if self.ms_type == "tcp":
            resp_frame = modbus_tcp_frame.parse_frame(resp)
        elif self.ms_type == "rtu":
            resp_frame = modbus_rtu_frame.parse_frame(resp)

        if resp_frame.func_code in [0x05, 0x06]:
            return resp_frame.data
        if resp_frame.func_code in [0x0F, 0x10]:
            return resp_frame.length
        if resp_frame.func_code in [0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
            txt = {
                1: "ILLEGAL_FUNCTION", 2: "ILLEGAL_DATA_ADDRESS", 3: "ILLEGAL_DATA_VALUE", 4: "SLAVE_DEVICE_FAILURE", 5: "ACKNOWLEDGE",
                6: "SLAVE_DEVICE_BUSY", 7: "NEGATIVE_ACKNOWLEDGE", 8: "MEMORY_PARITY_ERROR", 10: "GATEWAY_PATH_UNAVAILABLE",
                11: "GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND"}[resp_frame.error_code]
            raise ValueError("Received Error Frame (Function Code: {:02x}, Exception Code: {:02x}, {})".format(
                resp_frame.func_code, resp_frame.error_code, txt))


class modbus_tcp_client(modbus_master):
    def __init__(self, host: str, port: int=502, *args, **kwargs):
        """Init a modbus tcp client

        Args:
            host (str): IP or Hostname
            port (int): Port Defaults to 502
        """

        self.host = host
        self.port = port
        self.connected = False
        self.ti = 1
        super(modbus_tcp_client, self).__init__(ms_type="tcp", *args, **kwargs)

    def _send(self, frame: bytearray) -> bytearray:
        """Send a frame an return the resonse

        Args:
            frame (bytearray): data to send

        Returns:
            bytearray: response
        """
        self.sock.send(frame)
        return self.sock.recv(256)

    async def _send_async(self, frame: bytearray) -> bytearray:
        """Send a frame an return the resonse (async)

        Args:
            frame (bytearray): data to send

        Returns:
            bytearray: response
        """
        loop = asyncio.get_event_loop()
        self.sock.send(frame)
        return await loop.sock_recv(self.sock, 256)

    def connect(self):
        """Connect socket
        """
        if not self.connected:
            self.sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True

    def disconnect(self):
        """Disconnect socket
        """
        if self.connected:
            self.sock.close()
            self.connected = False


class modbus_rtu_master(modbus_master):
    def __init__(self, uart_no: int=1, baudrate: int=9600, bits: int=8, stop: int=1, 
        parity: int=None, tx_pin:int=14, rx_pin:int=13, en_pin:int=15, uart=None, 
        device_addr:int=1, *args, **kwargs):
        """Init a modbus RTU master. Pins or UART-Modul can be passed. If a second slave

        Args:
            uart_no (int, optional): [description]. Defaults to 1.
            baudrate (int, optional): [description]. Defaults to 9600.
            bits (int, optional): [description]. Defaults to 8.
            stop (int, optional): [description]. Defaults to 1.
            parity (int, optional): [description]. Defaults to None.
            tx_pin (int, optional): [description]. Defaults to 14.
            rx_pin (int, optional): [description]. Defaults to 13.
            en_pin (int, optional): [description]. Defaults to 15.
            uart (uart, optional): [description]. Defaults to None.
            device_addr (int, optional): [description]. Defaults to 1.
        """

        super(modbus_rtu_master, self).__init__(ms_type="rtu", *args, **kwargs)
        self.device_addr = device_addr
        if mp:
            self.baudrate = baudrate
            self.en_pin = machine.Pin(en_pin, machine.Pin.OUT)
            if uart is None:
                self.uart = machine.UART(
                    uart_no, baudrate, tx=tx_pin, rx=rx_pin)
                self.uart.init(baudrate=baudrate, bits=bits, parity=parity, stop=stop,
                               tx=tx_pin, rx=rx_pin, timeout=30, timeout_char=30, rxbuf=1024)
            else:
                self.uart = uart
        else:
            self.uart = uart

    def _send(self, frame: bytearray) -> bytearray:
        """Send a frame an return the resonse

        Args:
            frame (bytearray): data to send

        Returns:
            bytearray: response
        """
        if mp:
            self.en_pin.value(1)
            self.uart.write(frame)
            t = len(frame)*9/self.baudrate
            time.sleep(t+.01)   # wait until data is send
            self.en_pin.value(0)
            i = 0
            time.sleep(0.05)
            while (self.uart.any() == 0) & (i < 1):
                time.sleep(0.05)
                i += 0.05
            if self.uart.any() > 0:
                resp = self.uart.readline()
            else:
                raise ValueError("Timeout")
        else:
            self.uart.write(frame)
            i = 0
            while (self.uart.inWaiting() == 0) & (i < 1):
                time.sleep(0.05)
                i += 0.05
            if self.uart.inWaiting() > 0:
                resp = self.uart.read_all()
            else:
                raise ValueError("Timeout")
        return resp

    async def _send_async(self, frame: bytearray) -> bytearray:
        """Send a frame an return the resonse (async)

        Args:
            frame (bytearray): data to send

        Returns:
            bytearray: response
        """
        if mp:
            self.en_pin.value(1)
            self.uart.write(frame)
            t = len(frame)*9/self.baudrate
            await asyncio.sleep(t+.01)   # wait until data is send
            self.en_pin.value(0)
            i = 0
            await asyncio.sleep(0.05)
            while (self.uart.any() == 0) & (i < 1):
                await asyncio.sleep(0.05)
                i += 0.05
            if self.uart.any() > 0:
                resp = self.uart.readline()
            else:
                raise ValueError("Timeout")
        else:
            self.uart.write(frame)
            i = 0
            while (self.uart.inWaiting() == 0) & (i < 1):
                await asyncio.sleep(0.05)
                i += 0.05
            if self.uart.inWaiting() > 0:
                resp = self.uart.read_all()
            else:
                raise ValueError("Timeout")
        return resp
