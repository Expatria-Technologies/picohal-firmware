def event_callback(reg_type, address, val):
    global client
    print('status update received')
    i2c_display.displayline1 = 'status: {}'.format(client.get_hreg(1))