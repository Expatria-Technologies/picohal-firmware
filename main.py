from machine import I2C, Pin
from machine import Timer
import time
import _thread

tick_timer_period = 20 # Hz
systick = 0

from modbus_registers import client
import i2c_display
import neopixel_control

screen_update_period = 5 # update screen every 250ms
screen_update_counter = 0 

# Set up the action timer.
tim = Timer()



led_update_period = 2 # update leds every 100ms
led_update_counter = 0 

# Main Timer ISR
def tick(timer):                # we will receive the timer object when being called
    global systick
    global led
    global screen_update_counter, led_update_counter
        
    screen_update_counter = screen_update_counter - 1
    if screen_update_counter < 0:
        screen_update_counter = 0
        
    led_update_counter = led_update_counter - 1
    if led_update_counter < 0:
        led_update_counter = 0
        
    systick = systick + 1
        
tim.init(freq=tick_timer_period, mode=Timer.PERIODIC, callback=tick)  # 50ms timer period

# Main Loop
while True:
    
    result = client.process()
    i2c_display.displayline2 = 'status: {}'.format(client.get_hreg(1))
    i2c_display.displayline3 = "tick " + str(systick)

    if led_update_counter == 0:
        neopixel_control.strip.show()
        led_update_counter = led_update_period
        
    if screen_update_counter == 0:
        i2c_display.update_display()
        screen_update_counter = screen_update_period
        
        
