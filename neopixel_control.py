from neopixel import Neopixel
import time

# set up the neopixels

numpix = 20
brightness = 32

strip_type = "RGB"

# using State Machine 0 and pin 26
strip = Neopixel(numpix, 0, 26, strip_type)

red = (255, 0, 0)
orange = (255, 100, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
indigo = (75, 0, 130)
violet = (138, 43, 226)
white = (255,255,255)
off = (0, 0, 0)
strip.fill(off)
strip.show()
strip.brightness(brightness)
strip.set_pixel(0, red)
strip.set_pixel(1, green)
strip.set_pixel(2, blue)
strip.set_pixel(3, orange)
strip.set_pixel(4, yellow)
strip.set_pixel(5, violet)
strip.set_pixel(6, white)
strip.set_pixel(7, indigo)
strip.show()
time.sleep_ms(1000)

def update_neopixel(red, green, blue, white):
    strip.fill((red * 65535 // 255, green * 65535 // 255, blue * 65535 // 255, white * 65535 // 255))
    strip.show()
    
update_neopixel(255,255,255,255)