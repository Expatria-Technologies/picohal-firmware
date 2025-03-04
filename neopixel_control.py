from neopixel import Neopixel
import time

# set up the neopixels

numpix = 20
brightness = 255

strip_type = "GRB"

# using State Machine 0 and pin 26
strip = Neopixel(numpix, 0, 20, strip_type)
strip0 = Neopixel(numpix, 1, 21, strip_type)

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
strip0.fill(off)
strip0.show()
strip0.brightness(brightness)
strip0.set_pixel(0, red)
strip0.set_pixel(1, green)
strip0.set_pixel(2, blue)
strip0.set_pixel(3, orange)
strip0.set_pixel(4, yellow)
strip0.set_pixel(5, violet)
strip0.set_pixel(6, white)
strip0.set_pixel(7, indigo)
strip0.show()
time.sleep_ms(500)
strip0.fill((50, 50, 50))
strip0.show()

def update_neopixel(red, green, blue, white):
    strip.fill((red, green, blue))
    strip.show()
    
update_neopixel(25,25,25,25)