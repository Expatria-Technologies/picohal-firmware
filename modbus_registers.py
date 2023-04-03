def set_status_callback(reg_type, address, val):
    global client
    global displayline1
    print('status update received')
    displayline1 = 'status: {}'.format(val)


registers = {
    "HREGS": {
        "STATUS_REGISTER": {
            "register": 1,
            "len": 1,
            "val": 255,
            "on_set_cb": set_status_callback    
        }    
    }
}