from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
client = ModbusClient('192.168.178.61', port=502)
client.connect()
f = client.read_holding_registers(305,1)
print(f.registers)