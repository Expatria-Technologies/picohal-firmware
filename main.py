from machine import Timer
import time
import _thread
import gc

tick_timer_period = 1000 # Hz
systick = 0

from modbus_registers import client
import indicator_lights
from event_handler import process_event

screen_update_period = 10 # update screen every 250ms
screen_update_counter = 0 

# Set up the action timer.
tim = Timer()

led_update_period = 10 # update leds every 100ms
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

# 2nd core devoted to modbus client
def modbus_thread():
    while True:
        result = client.process()
        time.sleep_ms(10)
        gc.collect()
        
mb_thread = _thread.start_new_thread(modbus_thread, ())

print('Deploying')
indicator_lights.finish_flag()
while True:
    time.sleep_ms(10)
    process_event()

    if led_update_counter == 0:
        indicator_lights.process_indicators()
        led_update_counter = led_update_period
        


        