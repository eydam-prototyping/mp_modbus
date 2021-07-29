
def get_device_table(key):
    if key == "OR-WE-514":
        # ORNO OR-WE-514, device address: 1, uart: 9600-8-E-1, 
        return {
            "U" :                   {"register": 305,   "desc": "Voltage",        "type": "uint16", "gain": 100,  "unit": "V"},
            "I" :                   {"register": 313,   "desc": "Current",        "type": "int32",  "gain": 1000, "unit": "A"},
            "Power" :               {"register": 320,   "desc": "Power",          "type": "int32",  "gain": 1000, "unit": "kW"},
            "Power_R" :             {"register": 328,   "desc": "Reactive Power", "type": "int32",  "gain": 1000, "unit": "VA"},
            "Power_A" :             {"register": 336,   "desc": "Apparent Power", "type": "int32",  "gain": 1000, "unit": "VA"},
            "Energie_Total_aktiv" : {"register": 40960, "desc": "Total Energy",   "type": "int32",  "gain": 100,  "unit": "kWh"},
        }