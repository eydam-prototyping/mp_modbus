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
  ```
## mp_modbus_master

RTU-Master or TCP-Client:
```python
  from mp_modbus_master import modbus_rtu_master, modbus_tcp_client

  # RTU
  
```