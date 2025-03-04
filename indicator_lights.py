from nuts_bolts import current_state, program_flow
from machine import Pin
#from pwm_led_control import update_pwm_leds
from neopixel_control import update_neopixel
from time import sleep_ms

#define the user button here
user_button = 16

#only assign pins if they are defined.
try :
    if(user_button) :
        inspection_light = Pin(user_button, Pin.IN, Pin.PULL_UP)    
except NameError:
    inspection_light=0

def update_led_state():
    from modbus_registers import client
    
    if type(inspection_light) != int :
        if inspection_light.value() == 1:
            update_neopixel(255, 255, 255, 255)
            return        
        
    if client.get_hreg(1) == current_state.STATE_ALARM :
        update_neopixel(255,0,0,0)
        return
    elif client.get_hreg(1) == current_state.STATE_CYCLE :
        update_neopixel(0,255,0,255)
        return
    elif client.get_hreg(1) == current_state.STATE_HOLD :
        update_neopixel(128,128,0,255)
        return
    elif client.get_hreg(1) == current_state.STATE_IDLE :
        update_neopixel(0,0,0,255)
        return
    elif client.get_hreg(1) == current_state.STATE_TOOL_CHANGE :
        update_neopixel(0,0,255,255)
        return
    elif client.get_hreg(1) == current_state.STATE_HOMING :
        update_neopixel(0,0,255,255)
        return
    elif client.get_hreg(1) == current_state.STATE_JOG :
        update_neopixel(0,255,0,0)
        return    
    else :
        update_neopixel(25,25,25,25)
    
    #update_neopixel(255, 255, 255, 255)
    
        
def process_indicators():
    #print("updating indicators")
    update_led_state()
    
def set_status_callback(reg_type, address, val):
    #just update the LEDs quickly when the event is received.
    process_indicators()
    
def finish_flag():
    #flash the LEDs at program end.  Is ok to block since not much is going on
    #update_pwm_leds(0,0,0,0)
    update_neopixel(0, 0, 0, 0)
    sleep_ms(300)
    update_neopixel(255, 255, 255, 255)
    sleep_ms(300)
    update_neopixel(0, 0, 0, 0)
    sleep_ms(300)
    update_neopixel(255, 255, 255, 255)
    sleep_ms(300)
    update_neopixel(0, 0, 0, 0)
    sleep_ms(300)
    update_neopixel(255, 255, 255, 255)
    sleep_ms(300)
    update_neopixel(0, 0, 0, 0)
    sleep_ms(300)
    update_neopixel(255, 255, 255, 255)
    sleep_ms(300)    
