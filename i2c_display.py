from machine import I2C, Pin
# from ssd1306 import SSD1306_I2C
import sh1106

# set up the I2C for screen
sdaPIN=Pin(14)
sclPIN=Pin(15)
i2c=I2C(1,sda=sdaPIN, scl=sclPIN)
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
displayline4 = "This is line 4"
displayline5 = "This is line 5"
displayline6 = "This is line 6"
display.fill(0)

def update_display():
    global displayline1,displayline2,displayline3,displayline4,displayline5,displayline6
    bufferline1 = displayline1
    bufferline2 = displayline2
    bufferline3 = displayline3
    bufferline4 = displayline4
    bufferline5 = displayline5
    bufferline6 = displayline6            
    display.fill(0)
    #display.text(emptyline, 1, 1, 1)
    #display.text(emptyline, 1, 10, 1)
    #display.text(emptyline, 1, 20, 1)

    display.text(bufferline1, 1, 1, 1)
    display.text(bufferline2, 1, 10, 1)
    display.text(bufferline3, 1, 20, 1)
    display.text(bufferline4, 1, 30, 1)
    display.text(bufferline5, 1, 40, 1)
    display.text(bufferline6, 1, 50, 1)
    display.show()
            
