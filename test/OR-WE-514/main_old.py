from machine import Pin
from neopixel import NeoPixel
import network
import esp32
import json
import time
import mp_modbus
import mp_device_lib

STATE_DEFAULT               = 0x00

STATE_NW_NO_INIT              = 0x00
STATE_NW_WLAN_IF_ACTIVE       = 0x01
STATE_NW_WLAN_IF_CONNECTED    = 0x02
STATE_NW_WLAN_GOT_IP          = 0x03
STATE_NW_WLAN_IF_DISCONNECTED = 0x04
STATE_NW_WLAN_FAILED        = 0x04
STATE_NW_LAN_IF_ACTIVE      = 0x10
STATE_NW_LAN_IF_CONNECTED   = 0x20
STATE_NW_LAN_IF_GOT_IP      = 0x40
STATE_NW_LAN_FAILED         = 0x80

STATE_ST_WPS_START          = 0x01
STATE_ST_WPS_SUCCESS        = 0x02
STATE_ST_WPS_FAILED         = 0x03
STATE_ST_WPS_TIMEOUT        = 0x04

STATE_ST_MQTT_SEND          = 0x05
STATE_ST_MQTT_ERR           = 0x06

STATE_MB_MSGSEND            = 0x01
STATE_MB_MSGRECV            = 0x02
STATE_MB_ERRRECV            = 0x04
STATE_MB_TIMEOUT            = 0x08

WIFI_CONFIG_FILE = "/config/wifi.json"

LAN_TIMEOUT  = 5
WLAN_TIMEOUT = 30
WPS_TIMEOUT  = 60

class controller:
    def __init__(self):
        self.np = NeoPixel(Pin(4,Pin.OUT), 4)
        self.np_intens = 20
        for i in range(4):
            self.np[i] = (0,0,0)
        self.np.write()

        self.state = {
            "network": STATE_NW_NO_INIT,
            "state": STATE_DEFAULT,
            "modbus": STATE_DEFAULT
        }

        self.wlan = network.WLAN()

        esp32.register_event_handler(handler=lambda x: self._wifi_event_callback(x), event_base=esp32.EVENT_BASE_WIFI)
        esp32.register_event_handler(handler=lambda x: self._ip_event_callback(x), event_base=esp32.EVENT_BASE_IP)
        self.wps_button = Pin(12, Pin.IN, Pin.PULL_UP)
        self.wps_button.irq(lambda p: self.start_wps())

    def connect_wlan(self):
        self.wlan.active(True)

        wifi_cfg = {}

        try:
            with open(WIFI_CONFIG_FILE, "r") as fp:
                wifi_cfg = json.load(fp)
        except:
            print("No config file found")
            return

        for key in wifi_cfg:
            ssid = wifi_cfg[key]["ssid"]
            pw = wifi_cfg[key]["pass"]

            if self._connect_wlan(ssid, pw):
                return 

    def _connect_wlan(self, ssid, pw):
        self.wlan.connect(ssid, pw)
        i = 0
        while not self.wlan.isconnected():
            time.sleep(1)
            i += 1
            print(".")
            if i > WLAN_TIMEOUT:
                self.wlan.disconnect()
                break
        return self.wlan.isconnected()

    def start_wps(self):
        if self.state["state"] == STATE_ST_WPS_START:
            return
        self._set_state({"state":STATE_ST_WPS_START})
        self.wlan.active(True)
        if self.wlan.isconnected():
            self.wlan.disconnect()
        self.wlan.connect(wps=True)

    def _set_state_bit(self, key, mask):
        new_state = self.state[key] | mask
        self._set_state({key:new_state})

    def _reset_state_bit(self, key, mask):
        new_state = self.state[key] & ~mask
        self._set_state({key:new_state})

    def _set_state(self, new_state):
        for key in new_state:
            self.state[key] = new_state[key]
            if self.np is not None:
                if key == "network":
                    # not init - LED off
                    if new_state[key] == STATE_NW_NO_INIT:
                        self.np[0] = (0,0,0)
                    # wlan if active - LED blue
                    elif new_state[key] == STATE_NW_WLAN_IF_ACTIVE:
                        self.np[0] = (0,0,self.np_intens)
                    # wlan if connected - LED yellow
                    elif new_state[key] == STATE_NW_WLAN_IF_CONNECTED:
                        self.np[0] = (self.np_intens,self.np_intens,0)
                    # wlan if got ip - LED green
                    elif new_state[key] == STATE_NW_WLAN_GOT_IP:
                        self.np[0] = (0,self.np_intens,0)
                    # wlan if got ip - LED red
                    elif new_state[key] == STATE_NW_WLAN_IF_DISCONNECTED:
                        self.np[0] = (self.np_intens,0,0)

                if key == "modbus":
                    # nothing special = LED off
                    if new_state[key] == STATE_DEFAULT:
                        self.np[1] = (0,0,0)  
                    # msg send = LED green
                    elif new_state[key] == STATE_MB_MSGSEND:
                        self.np[1] = (0,0,self.np_intens)  
                    elif new_state[key] == STATE_MB_MSGRECV:
                        self.np[1] = (0,self.np_intens,0)  
                    elif new_state[key] == STATE_MB_ERRRECV:
                        self.np[1] = (self.np_intens,0,0)  
                    
                if key == "state":
                    # nothing special = LED off
                    if new_state[key] == STATE_DEFAULT:
                        self.np[2] = (0,0,0)
                    # wps probing = LED purple
                    elif new_state[key] == STATE_ST_WPS_START:
                        self.np[2] = (self.np_intens,0,self.np_intens)
                    elif new_state[key] == STATE_ST_WPS_SUCCESS:
                        self.np[2] = (0,self.np_intens,0)
                    elif new_state[key] in [STATE_ST_WPS_FAILED, STATE_ST_WPS_TIMEOUT]:
                        self.np[2] = (self.np_intens,0,0)
                    elif new_state[key] in [STATE_ST_MQTT_SEND]:
                        self.np[2] = (0,self.np_intens,0)
                    elif new_state[key] == STATE_ST_MQTT_ERR:
                        self.np[2] = (self.np_intens,0,0)
                
                self.np.write()

    def _wifi_event_callback(self, event_id):
        print("WIFI: {}".format(event_id))
        if event_id == 2:   # wifi active
            self._set_state({"network": STATE_NW_WLAN_IF_ACTIVE})
        elif event_id == 4:   # wifi connected
            self._set_state({"network": STATE_NW_WLAN_IF_CONNECTED})
        elif event_id == 5:   # wifi disconnected
            self._set_state({"network": STATE_NW_WLAN_IF_DISCONNECTED})
            if self.wlan.status()==205: # disconnected because auth failed
                self.wlan.disconnect()
        elif event_id == 7:   # wps succsess
            self._set_state({"state": STATE_ST_WPS_SUCCESS})
            try:
                with open(WIFI_CONFIG_FILE, "r") as fp:
                    wifi_cfg = json.load(fp)
            except:
                print("No config file found")
            wifi_cfg = {}
            wifi_cfg["WPS"] = {
                "ssid": self.wlan.config("essid"),
                "pass": self.wlan.config("password"),
                "mac": self.wlan.config("mac"),
                "comment": "WPS"
            }
            with open(WIFI_CONFIG_FILE, "w") as fp:
                json.dump(wifi_cfg, fp)
            
        elif event_id == 8:   # wps failed
            self._set_state({"state": STATE_ST_WPS_FAILED})
        elif event_id == 9:   # wps timeout
            self._set_state({"state": STATE_ST_WPS_TIMEOUT})

    def _ip_event_callback(self, event_id):
        if event_id == 0:   # wifi active
            self._set_state({"network": STATE_NW_WLAN_GOT_IP})
        

c = controller()
c.connect_wlan()

mc = mp_modbus.modbus_controller({"parity":0})
ms = mc.create_slave(1, mp_device_lib.get_device_table("OR-WE-514"))

print(ms.read_value_by_name("U"))

