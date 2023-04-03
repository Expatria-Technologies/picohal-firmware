from neopixel import Neopixel

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