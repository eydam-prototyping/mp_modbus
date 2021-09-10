# ToDo:
# - remove debug output
# - error messages + test cases
# - documentation

class modbus_frame:
    def __init__(self, func_code=0, register=None, fr_type="request", length=None, data=None, error_code=None):
        self.type = fr_type

        if func_code not in [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x0F, 0x10, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
            raise ValueError("function code {} is not supported".format(func_code))
        self.func_code = func_code
        
        if fr_type == "request":
            if data is not None:
                if func_code not in [0x05, 0x06, 0x0F, 0x10]:
                    raise ValueError("data is not supported for {} with function code {}".format(fr_type, func_code))
        elif fr_type == "response":
            if data is not None:
                if func_code not in [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]:
                    raise ValueError("data is not supported for {} with function code {}".format(fr_type, func_code))
        self.data = data

        if fr_type == "response":
            if register is not None:
                if func_code not in [0x05, 0x06, 0x0F, 0x10]:
                    raise ValueError("register is not supported for {} with function code {}".format(fr_type, func_code))
        self.register = register

        if fr_type == "request":
            if length is not None:
                if func_code not in [0x01, 0x02, 0x03, 0x04, 0x0F, 0x10]:
                    raise ValueError("length is not supported for {} with function code {}".format(fr_type, func_code))
        elif fr_type == "response":
            if length is not None:
                if func_code not in [0x0F, 0x10]:
                    raise ValueError("length is not supported for {} with function code {}".format(fr_type, func_code))
        self.length = length

        if fr_type == "response":
            if error_code is not None:
                if func_code not in [0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
                    raise ValueError("error_code is not supported for {} with function code {}".format(fr_type, func_code))
        self.error_code = error_code

        self.pdu = None
        self.frame = None

    def _create_pdu(self):
        self.pdu = bytearray([])
        self.pdu += bytearray([self.func_code])

        if self.type == "request":
            self.pdu += bytearray([self.register>>8, self.register&0xFF])
            if self.func_code in [0x01, 0x02, 0x03, 0x04, 0x0F, 0x10]:
                self.pdu += bytearray([self.length>>8, self.length&0xFF])
            if self.func_code in [0x0F, 0x10]:
                self.pdu += bytearray([len(self.data)])
            if self.func_code in [0x05, 0x06, 0x0F, 0x10]:
                self.pdu += self.data
        
        if self.type == "response":
            if self.func_code in [0x01, 0x02, 0x03, 0x04]:
                self.pdu += bytearray([len(self.data)])
            if self.func_code in [0x05, 0x06, 0x0F, 0x10]:
                self.pdu += bytearray([self.register>>8, self.register&0xFF])
            if self.func_code in [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]:
                self.pdu += self.data
            if self.func_code in [0x0F, 0x10]:
                self.pdu += bytearray([self.length>>8, self.length&0xFF])
            if self.func_code in [0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
                self.pdu += bytearray([self.error_code])
    
    def _create_frame(self):
        pass
    
    def get_frame(self):
        if self.frame is None:
            self._create_frame()
        return self.frame
       

class modbus_rtu_frame(modbus_frame):
    def __init__(self, device_addr=0, *args, **kwargs):
        """Create modbus rtu frame. 

        Args:
            device_addr (int, optional): Slave address. Defaults to 0.
            func_code (int, optional): Function code (1-6,15,16). Defaults to 0.
            register ([type], optional): Register. Defaults to None.
            fr_type (str, optional): Frame type (request/response). Defaults to "request".
            length ([type], optional): Length of reqested data. Defaults to None.
            data ([type], optional): Payload. Defaults to None.
        """
        super(modbus_rtu_frame, self).__init__(*args, **kwargs)
        self.device_addr = device_addr
        self.frame = None

    def _create_frame(self):
        self._create_pdu()
        self.frame = bytearray([self.device_addr]) + self.pdu
        crc = modbus_rtu_frame._crc16(self.frame)
        self.frame += bytearray([crc&0xFF, crc>>8])

    def __str__(self):
        return "<modbus_rtu_frame ({}): device: {}, func_code: {}, frame:{}>".format(self.type, self.device_addr, self.func_code, " ".join(["{:02x}".format(x) for x in self.get_frame()]))

    @classmethod
    def _crc16(cls, data):
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

    @classmethod
    def parse_frame(cls, frame, fr_type=None):
        """Factory Method: Create a modbus_rtu_frame from bytearray.

        Args:
            frame (bytearray): frame to parse.

        Returns:
            modbus_rtu_frame: parsed frame
        """
        device_addr = frame[0]
        func_code = frame[1]
        
        if cls._check_both(frame):
            register = (frame[2]<<8) + frame[3]
            data = frame[4:6]
            return modbus_rtu_frame(device_addr=device_addr, func_code=func_code, register=register, fr_type="request", data=data)

        if cls._check_request(frame) and ((fr_type is None) or (fr_type == "request")):
            register = (frame[2]<<8) + frame[3]
            length = (frame[4]<<8) + frame[5]
            data = None
            if func_code in [0x0F, 0x10]:
                bc = frame[6]
                data = frame[7:7+bc]
            return modbus_rtu_frame(device_addr=device_addr, func_code=func_code, register=register, fr_type="request", length=length, data=data)

        if cls._check_response(frame) and ((fr_type is None) or (fr_type == "response")):
            if func_code in [0x01, 0x02, 0x03, 0x04]:
                bc = frame[2]
                data = frame[3:3+bc]
                return modbus_rtu_frame(device_addr=device_addr, func_code=func_code, fr_type="response", data=data)
            if func_code in [0x0F, 0x10]:
                register = (frame[2]<<8) + frame[3]
                length = (frame[4]<<8) + frame[5]
                return modbus_rtu_frame(device_addr=device_addr, func_code=func_code, register=register, fr_type="response", length=length)
            if func_code in [0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
                error_code = frame[2]
                return modbus_rtu_frame(device_addr=device_addr, func_code=func_code, fr_type="response", error_code=error_code)

    @classmethod 
    def _check_both(cls, frame):
        """Parser-Helper: if func_code is 0x05 or 0x06, we can't decide if it is a 
        request or a response. This method checks, if is a valid 0x05- or 0x06-frame.

        Args:
            frame (bytearray): The frame to check.

        Returns:
            bool: True, if it is a valid 0x05- or 0x06-frame.
        """
        try:
            func_code = frame[1]
            if func_code not in [0x05, 0x06]:
                return False
            return cls._crc16(frame[0:6]) == (frame[7] << 8)+frame[6]
        except:
            return False

    @classmethod 
    def _check_request(cls, frame):
        """Parser-Helper: This method checks, if is a valid request. It returns False,
        if the frame could be a request or a response.

        Args:
            frame (bytearray): The frame to check.

        Returns:
            bool: True, if it is a valid request.
        """
        try:
            func_code = frame[1]
            if func_code in [0x01, 0x02, 0x03, 0x04]:
                return cls._crc16(frame[0:6]) == (frame[7] << 8)+frame[6]
            if func_code in [0x10, 0x0F]:
                bc = frame[6]
                if len(frame) >= 8+bc:
                    return cls._crc16(frame[0:7+bc]) == (frame[8+bc] << 8)+frame[7+bc]
                else:
                    return False
        except:
            return False
    
    @classmethod
    def _check_response(cls, frame):
        """Parser-Helper: This method checks, if is a valid response. It returns False,
        if the frame could be a request or a response.

        Args:
            frame (bytearray): The frame to check.

        Returns:
            bool: True, if it is a valid response.
        """
        try:
            func_code = frame[1]
            if func_code in [0x01, 0x02, 0x03, 0x04]:
                bc = frame[2]
                if len(frame) >= bc + 5:
                    return cls._crc16(frame[0:3+bc]) == (frame[4+bc] << 8)+frame[3+bc]
            if func_code in [0x10, 0x0F]:
                return cls._crc16(frame[0:6]) == (frame[7] << 8)+frame[6]
            if func_code in [0x83, 0x86]:
                return cls._crc16(frame[0:3]) == (frame[4] << 8)+frame[3]
        except:
            return False

    @classmethod
    def transform_frame(cls, tcp_frame):
        frame = modbus_rtu_frame()
        frame.data
        frame.device_addr = tcp_frame.unit_id
        frame.func_code = tcp_frame.func_code
        frame.length = tcp_frame.length
        frame.register = tcp_frame.register
        frame.type = tcp_frame.register
        return frame


class modbus_tcp_frame(modbus_frame):
    def __init__(self, transaction_id=0, unit_id=0, *args, **kwargs):
        """Create modbus tcp frame. 

        Args:
            transaction_id (int, optional): Transaction ID. Defaults to 0.
            unit_id (int, optional): Unit address. Defaults to 0.
            func_code (int, optional): Function code (1-6,15,16). Defaults to 0.
            register ([type], optional): Register. Defaults to None.
            fr_type (str, optional): Frame type (request/response). Defaults to "request".
            length ([type], optional): Length of reqested data. Defaults to None.
            data ([type], optional): Payload. Defaults to None.
        """
        super(modbus_tcp_frame, self).__init__(*args, **kwargs)
        self.transaction_id = transaction_id
        self.unit_id = unit_id
        self.frame = None

    def _create_frame(self):
        self._create_pdu()
        self.frame = bytearray([self.transaction_id>>8, self.transaction_id&0xFF])
        self.frame += bytearray([0x00, 0x00]) # Protocol ID
        l = len(self.pdu)+1
        self.frame += bytearray([l>>8, l&0xFF])
        self.frame += bytearray([self.unit_id])
        self.frame += self.pdu

    def __str__(self):
        return "<modbus_tcp_frame ({}): func_code: {}, frame:{}>".format(self.type, self.func_code, " ".join(["{:02x}".format(x) for x in self.get_frame()]))
    
    @classmethod
    def parse_frame(cls, frame):
        """Factory Method: Create a modbus_tcp_frame from bytearray.

        Args:
            frame (bytearray): frame to parse.

        Returns:
            modbus_tcp_frame: parsed frame
        """
        transaction_id = (frame[0]<<8) + frame[1]
        length = (frame[4]<<8) + frame[5]
        unit_id = frame[6]
        func_code = frame[7]
        
        if cls._check_both(frame, length):
            register = (frame[8]<<8) + frame[9]
            data = frame[10:12]
            return modbus_tcp_frame(transaction_id=transaction_id ,unit_id=unit_id, func_code=func_code, register=register, fr_type="request", data=data)

        if cls._check_request(frame, length):
            register = (frame[8]<<8) + frame[9]
            d_length = (frame[10]<<8) + frame[11]
            data = None
            if func_code in [0x0F, 0x10]:
                bc = frame[12]
                data = frame[13:13+bc]
            return modbus_tcp_frame(transaction_id=transaction_id ,unit_id=unit_id, func_code=func_code, register=register, fr_type="request", data=data, length=d_length)
        
        if cls._check_response(frame, length):
            if func_code in [0x01, 0x02, 0x03, 0x04]:
                bc = frame[8]
                data = frame[9:9+bc]
                return modbus_tcp_frame(transaction_id=transaction_id ,unit_id=unit_id, func_code=func_code, fr_type="response", data=data)
            if func_code in [0x0F, 0x10]:
                register = (frame[8]<<8) + frame[9]
                d_length = (frame[10]<<8) + frame[11]
                return modbus_tcp_frame(transaction_id=transaction_id ,unit_id=unit_id, func_code=func_code, fr_type="response", register=register, length=d_length)
            if func_code in [0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
                error_code = frame[8]
                return modbus_tcp_frame(transaction_id=transaction_id ,unit_id=unit_id, func_code=func_code, fr_type="response", error_code=error_code)
        

    @classmethod 
    def _check_both(cls, frame, length):
        """Parser-Helper: if func_code is 0x05 or 0x06, we can't decide if it is a 
        request or a response. This method checks, if is a valid 0x05- or 0x06-frame.

        Args:
            frame (bytearray): The frame to check.

        Returns:
            bool: True, if it is a valid 0x05- or 0x06-frame.
        """
        try:
            func_code = frame[7]
            if func_code not in [0x05, 0x06]:
                return False
            return len(frame) == length + 6
        except:
            return False

    @classmethod 
    def _check_request(cls, frame, length):
        """Parser-Helper: This method checks, if is a valid request. It returns False,
        if the frame could be a request or a response.

        Args:
            frame (bytearray): The frame to check.

        Returns:
            bool: True, if it is a valid request.
        """
        try:
            func_code = frame[7]
            if func_code in [0x01, 0x02, 0x03, 0x04]:
                if len(frame) == length + 6:
                    return length == 6
            if func_code in [0x10, 0x0F]:
                bc = frame[12]
                if len(frame) == bc+13:
                    return len(frame) == length + 6
            return False
        except:
            return False
    
    @classmethod
    def _check_response(cls, frame, length):
        """Parser-Helper: This method checks, if is a valid response. It returns False,
        if the frame could be a request or a response.

        Args:
            frame (bytearray): The frame to check.

        Returns:
            bool: True, if it is a valid response.
        """
        try:
            func_code = frame[7]
            if func_code in [0x01, 0x02, 0x03, 0x04]:
                bc = frame[8]
                if len(frame) == bc + 9:
                    return len(frame) == length + 6
            if func_code in [0x10, 0x0F]:
                return len(frame) == length + 6
            if func_code in [0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x8F, 0x90]:
                return length == 3
        except:
            return False
