from machine import I2C, Pin
# from ssd1306 import SSD1306_I2C
import sh1106

# set up the I2C for screen
sdaPIN=Pin(14)
sclPIN=Pin(15)
i2c=I2C(1,sda=sdaPIN, scl=sclPIN)
# display = SSD1306_I2C(128, 64, i2c)
try:
    display = sh1106.SH1106_I2C(128, 64, i2c, None, 0x3c)
    display.flip()
    display.init_display()
    display.contrast(255)  # bright
    display.fill(0)
except OSError:
    display = 0    
emptyline =    "                 "
displayline1 = 'PicoHAL uPython Modbus'
displayline2 = emptyline
displayline3 = emptyline
displayline4 = emptyline
displayline5 = emptyline
displayline6 = emptyline

def update_display():
    if display :
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
            
