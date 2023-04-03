import i2c_display

def set_pump_callback(reg_type, address, val):
    global client
    global displayline1
    print('pump update received')
    i2c_display.displayline6 = 'Set Pump: {}'.format(client.get_hreg(101))