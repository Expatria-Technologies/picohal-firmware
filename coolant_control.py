import i2c_display
from machine import Pin

#By default, use GPIOs 20 and 24 for coolant relay control as these allow XY step/dir when cnc shield is populated
#Mist is on GPIO 7 (Relay 1) and Flood is on GPIO 4 (Relay 4).  Pins could also be assigned to outputs on the LED drivers
#to mimic Flexi-HAL I/O

relay1_pin = 24
#relay2_pin = 22
#relay3_pin = 23
relay4_pin = 20

#only assign pins if they are defined.
try :
    if(relay1_pin) :
        mist = Pin(24, Pin.OUT)    
    if(relay4_pin) :
        flood = Pin(20, Pin.OUT)
except NameError:
    mist=0
    flood=0

def update_coolant_pins(pins):
    #only update the pins if they were assigned.
    if(mist) :
        mist.value(pins & 1)
    
    if(flood) :
        flood.value(pins & 2)


def set_coolant_callback(reg_type, address, val):
    global client
    global displayline1
    print('coolant update received {}'.format(val[0]))
    i2c_display.displayline4 = 'Coolant: {}'.format(val[0])
    update_coolant_pins(val[0])
    
update_coolant_pins(0)