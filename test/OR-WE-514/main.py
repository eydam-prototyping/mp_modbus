import mp_modbus_master as mmm
import time
import struct

d1 = mmm.modbus_rtu_master(uart_no=2, parity=0, tx_pin=12, rx_pin=13, en_pin=32)
l = {
    "U" :                   {"register": 305,   "desc": "Voltage",        "type": "uint16", "gain": 100,  "unit": "V"},
    "I" :                   {"register": 313,   "desc": "Current",        "type": "int32",  "gain": 1000, "unit": "A"},
    "Power" :               {"register": 320,   "desc": "Power",          "type": "int32",  "gain": 1000, "unit": "kW"},
    "Power_R" :             {"register": 328,   "desc": "Reactive Power", "type": "int32",  "gain": 1000, "unit": "VA"},
    "Power_A" :             {"register": 336,   "desc": "Apparent Power", "type": "int32",  "gain": 1000, "unit": "VA"},
    "Energie_Total_aktiv" : {"register": 40960, "desc": "Total Energy",   "type": "int32",  "gain": 100,  "unit": "kWh"},
}

for i in range(3):
    time.sleep(1)
    for e in l:        
        try:
            #time.sleep(0.1)
            #print(e)
            print(d1.uart.read(10))
            if l[e]["type"] == "uint16":
                f = d1.read_holding_registers_async(l[e]["register"], 1)
                #print(f)
                v = struct.unpack(">h", f.data)[0]/l[e]["gain"]
            if l[e]["type"] == "int32":
                f = d1.read_holding_registers(l[e]["register"], 2)
                #print(f)
                v = struct.unpack(">I", f.data)[0]/l[e]["gain"]
            print("{}: {} {}".format(e, v, l[e]["unit"]))
        except:
            time.sleep(0.1)
            print("ERROR")
            print(d1.uart.read(10))
            while d1.uart.any() > 0:
                print(d1.uart.read(10))