import mp_modbus_master as mmm
import mp_modbus_slave as mms
import mp_modbus_frame as mmf
import network
import machine
import time
import struct


p = machine.Pin(5, machine.Pin.OUT)
p.value(1)

l = network.LAN(mdc = machine.Pin(23), mdio = machine.Pin(18), phy_type = network.PHY_RTL8201, phy_addr=0)
l.active(True)

tcp_server = mms.modbus_tcp_server(host="0.0.0.0", port=502)
rtu_master = mmm.modbus_rtu_master(uart_no=2, parity=0, tx_pin=12, rx_pin=13, en_pin=32)

err_cntr = 0
msg_cntr = 0

def forward_message(frame):
    global err_cntr
    global msg_cntr
    try:
        msg_cntr += 1
        if frame.func_code == 3:
            res = rtu_master.read_holding_registers(frame.register, frame.length)
            print("{}/{}".format(err_cntr, msg_cntr))
            return mmf.modbus_tcp_frame(unit_id=frame.unit_id, transaction_id=frame.transaction_id, 
                            func_code=frame.func_code, fr_type="response", data=res.data)
    except:
        err_cntr += 1
        print("ERROR")

tcp_server.forward_message = forward_message

tcp_server.run()