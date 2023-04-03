import i2c_display

def set_spindle_callback(reg_type, address, val):
    global client
    global displayline1
    print('spindle update received')
    i2c_display.displayline6 = 'Set spindle command'
