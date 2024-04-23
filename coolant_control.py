from machine import Pin

#By default, use GPIOs 20 and 24 for coolant relay control as these allow XY step/dir when cnc shield is populated
#Mist is on GPIO 7 (Relay 1) and Flood is on GPIO 4 (Relay 4).

relay1_pin = 24
#relay2_pin = 22
#relay3_pin = 23
relay4_pin = 20

#only assign pins if they are defined.
try :
    if(relay1_pin) :
        mist = Pin(24, Pin.OUT)
        mist.value(0)
    if(relay4_pin) :
        flood = Pin(20, Pin.OUT)
        flood.value(0)
except NameError:
    mist=0
    flood=0

def update_coolant_pins():
    from modbus_registers import client
    #only update the pins if they were assigned.
    if(mist) :
        mist.value(client.get_hreg(0x100) & 1)
    
    if(flood) :
        flood.value(client.get_hreg(0x100) & 2)


def set_coolant_callback(reg_type, address, val):
    global client
    global displayline1
    update_coolant_pins()
    
#update_coolant_pins()