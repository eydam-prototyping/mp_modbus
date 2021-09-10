import network
import time
import mp_modbus_master as mmm
import struct

w = network.WLAN()
w.active(True)
w.connect("SUN2000-BT20C0141259", "changeme")

while not w.isconnected():
    time.sleep(1)
    print(".")

m = mmm.modbus_tcp_client("192.168.200.1", 502)
m.connect()

for _ in range(10):
    time.sleep(1)
    f = m.read_holding_registers(32069, 1)
    v = struct.unpack(">h", f.data)[0]/10
    print(v)