from machine import I2C, Pin
from machine import Timer
import time
# from ssd1306 import SSD1306_I2C
import sh1106
import _thread

from neopixel import Neopixel

from umodbus.serial import ModbusRTU

#while True:
#    time.sleep(1)

tick_timer_period = 20 # Hz
systick = 0

# the following definition is for a RP2
rtu_pins = (Pin(12), Pin(13))     # (TX, RX)
uart_id = 0

slave_addr = 10             # address on bus as client

client = ModbusRTU(
    addr=slave_addr,        # address on bus
    pins=rtu_pins,          # given as tuple (TX, RX)
    baudrate=115200,        # optional, default 9600
    data_bits=8,          # optional, default 8
    stop_bits=1,          # optional, default 1
    parity=None,          # optional, default None
    ctrl_pin=26,          # optional, control DE/RE
    uart_id=uart_id         # optional, default 1, see port specific documentation
)

# set up the I2C for screen
sdaPIN=machine.Pin(14)
sclPIN=machine.Pin(15)
i2c=machine.I2C(1,sda=sdaPIN, scl=sclPIN)
# display = SSD1306_I2C(128, 64, i2c)
display = sh1106.SH1106_I2C(128, 64, i2c, None, 0x3c)
display.flip()
display.init_display()
# Print "Hello world!" 1 pixel from top left, in colour 1 (on)
# .text(text, x, y, c)
display.contrast(255)  # bright
emptyline =    "                 "
displayline1 = "This is line 1"
displayline2 = "This is line 2"
displayline3 = "This is line 3"
bufferline1 = displayline1
bufferline2 = displayline2
bufferline3 = displayline3
display.text(bufferline1, 1, 1, 1)
display.text(bufferline2, 1, 10, 1)
display.text(bufferline3, 1, 20, 1)
display.show()

screen_update_period = 5 # update screen every 250ms
screen_update_counter = 0 

# Set up the action timer.
tim = Timer()

# Set up heartbeat
led = Pin(1, Pin.OUT)
onboard_led_count = 10

# set up the neopixels

numpix = 3
strip = Neopixel(numpix, 0, 22, "GRB")
red = (255, 0, 0)
orange = (255, 165, 0)
yellow = (255, 150, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
indigo = (75, 0, 130)
violet = (138, 43, 226)
off = (0, 0, 0)
colors_rgb = (red, orange, yellow, green, blue, indigo, violet)
colors = colors_rgb
strip.brightness(42)
jogled = 2
screenled = 1
haltled = 0
strip.set_pixel(jogled, red)
strip.set_pixel(screenled, blue)
strip.set_pixel(haltled, green)

led_update_period = 2 # update leds every 100ms
led_update_counter = 0 

# Main Timer ISR
def tick(timer):                # we will receive the timer object when being called
    global systick
    global onboard_led_count
    global led
    global screen_update_counter, led_update_counter
    if onboard_led_count == 0:
        led.toggle()                # toggle the LED
        onboard_led_count = 10
    else:
        onboard_led_count = onboard_led_count - 1
        
    screen_update_counter = screen_update_counter - 1
    if screen_update_counter < 0:
        screen_update_counter = 0
        
    led_update_counter = led_update_counter - 1
    if led_update_counter < 0:
        led_update_counter = 0
        
    systick = systick + 1
        
tim.init(freq=tick_timer_period, mode=Timer.PERIODIC, callback=tick)  # 50ms timer period

# Main Loop - this will be used to poll jog buttons and joystick for continuous movement
while True:

    if led_update_counter == 0:
        strip.show()
        led_update_counter = led_update_period
        
    if screen_update_counter == 0:
        if (bufferline1 != displayline1) | (bufferline2 != displayline2) | (bufferline3 != displayline3) :
            bufferline1 = displayline1
            bufferline2 = displayline2
            bufferline3 = displayline3
            display.fill(0)
            #display.text(emptyline, 1, 1, 1)
            #display.text(emptyline, 1, 10, 1)
            #display.text(emptyline, 1, 20, 1)
            
            display.text(bufferline1, 1, 1, 1)
            display.text(bufferline2, 1, 10, 1)
            display.text(bufferline3, 1, 20, 1)
            display.show()
        screen_update_counter = screen_update_period
    
    displayline3 = "tick " + str(systick)
        
        
