#by default, use X and Y step/dir pins

from machine import Pin, Timer
from utime import sleep_us
from rp2 import PIO, StateMachine, asm_pio

enable_pin=Pin(27, Pin.OUT)
#step_pin=Pin(18, Pin.OUT)              # set the output only if using the pump, move to modbus callback
dir_pin=Pin(22, Pin.OUT)              # set the output only if using the pump
#step_pin.value(0)
enable_pin.value(0)
step_timer = Timer()
accel_timer = Timer()

pulse_per_rev = 1600


target_frequency = 100
current_frequency = 0
accel = 20

prev_freq = 0
new_freq = 0

@asm_pio(set_init=PIO.OUT_LOW)
def square():
    pull(noblock)
    mov(x, osr)                     # Shift value from OSR to scratch X (AUTOPULL ENGAGED)
    mov(y, x)
    label("countloop")
    jmp(x_not_y, "skip")        # Loop until X hits 0    
    set(pins, 1) [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    set(pins, 0) [31]
    nop()        [31]
    nop()        [31]
    nop()        [31]
    label("skip")
    jmp(y_dec, "countloop")
    
sm = StateMachine(1, square, freq=50000000, set_base=Pin(18))
sm.put(int((1/target_frequency)*25000000))
    
def accel_callback(accel_timer) :    
    global current_frequency, target_frequency, prev_freq, new_freq
    if current_frequency < target_frequency :
        current_frequency = current_frequency + accel
    elif current_frequency > target_frequency :
        current_frequency = current_frequency - accel
    
    if current_frequency < 0 :
        current_frequency = 0
    
    if current_frequency > 0 :
        new_freq = int((1/current_frequency)*25000000)
        if prev_freq != new_freq :
            #print('prev {}'.format(prev_freq))
            #print('new {}'.format(new_freq))
            sm.put(new_freq)
            prev_freq = new_freq
            if sm.active() == False :
                sm.active(1)
    else :
        if sm.active() :
            sm.active(0)
    
accel_timer.init(freq=200, mode=Timer.PERIODIC, callback=accel_callback)   #initializing the timer

def set_pump_callback(reg_type, address, val):
    global client
    global displayline1
    print('pump update received')