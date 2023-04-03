import i2c_display

def set_coolant_callback(reg_type, address, val):
    global client
    global displayline1
    print('coolant update received')
    i2c_display.displayline1 = 'status: {}'.format(client.get_hreg(100))