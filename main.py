from machine import Timer
import time
import _thread
import program_steppers

tick_timer_period = 20 # Hz
systick = 0

from modbus_registers import client 
from event_handler import process_event
from nuts_bolts import current_state, program_flow




# Set up the action timer.
tim = Timer()

led_update_period = 2 # update leds every 100ms
led_update_counter = 0 

# Main Timer ISR
def tick(timer):                # we will receive the timer object when being called
    global systick
    global led
    global screen_update_counter, led_update_counter
           
    led_update_counter = led_update_counter - 1
    if led_update_counter < 0:
        led_update_counter = 0
        
    systick = systick + 1
        
tim.init(freq=tick_timer_period, mode=Timer.PERIODIC, callback=tick)  # 50ms timer period

# Main Loop
while True:
    
    result = client.process()
    process_event()

    if led_update_counter == 0:
        led_update_counter = led_update_period
        