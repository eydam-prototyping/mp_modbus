# mp_modbus
Modbus Lib for Micropython

## mp_modbus_frame

Create a modbus frame (you shouldn't have to do it by yourself):
  ```python
  from mp_modbus_frame import modbus_rtu_frame, modbus_tcp_frame

  # RTU
  rtu_frame = modbus_rtu_frame(
      device_addr=1,    # slave address
      func_code=3,      # function code
      register=100,     # requested register
      length=2,         # number of requested registers
      fr_type="request" # type of frame
    )

  # or parsing:
  rtu_frame = modbus_rtu_frame.parse_frame(
    bytearray([0x01, 0x03, 0x00, 0x12, 0x00, 0x08, 0xe4, 0x09])
    )

  # TCP
  tcp_frame = modbus_tcp_frame(
      transaction_id=1, # transaction id
      unit_id=1,        # unit id
      device_addr=1,    # slave address
      func_code=3,      # function code
      register=100,     # requested register
      length=2,         # number of requested registers
      fr_type="request" # type of frame
    )  

  # or parsing:
  tcp_frame = modbus_tcp_frame.parse_frame(
    bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x01, 0x03, 
        0x00, 0x12, 0x00, 0x08])
    )
  ```
## mp_modbus_master

RTU-Master or TCP-Client:
```python
from mp_modbus_master import modbus_rtu_master, modbus_tcp_client

# RTU
rtu_master = modbus_rtu_master(
  uart_no=2, parity=0, tx_pin=12, rx_pin=13, en_pin=32
  )

frame = rtu_master.read_holding_registers(305, 1)
print(frame.data)

# TCP

```