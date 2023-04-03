from peristaltic_pump import set_pump_callback
from coolant_control import set_coolant_callback
from event_handler import event_callback
import i2c_display

from machine import Pin

def set_status_callback(reg_type, address, val):
    global client
    print('status update received')
    i2c_display.displayline1 = 'status: {}'.format(client.get_hreg(1))
    
def set_output_callback(reg_type, address, val):
    print('output pin update received')

registers = {
    "HREGS": {
        "STATUS_REGISTER": {
            "register": 1,
            "len": 1,
            "val": 255,
            "on_set_cb": set_status_callback    
        },
        "INPUT_REGISTER": {
            "register": 2,
            "len": 1,
            "val": 255,    
        },
        "OUTPUT_REGISTER": {
            "register": 3,
            "len": 1,
            "val": 0,
            "on_set_cb": set_output_callback    
        },
        "EVENT_REGISTER": {
            "register": 4,
            "len": 1,
            "val": 0,
            "on_set_cb": event_callback    
        },          
        "COOLANT_REGISTER": {
            "register": 100,
            "len": 1,
            "val": 0,
            "on_set_cb": set_coolant_callback    
        },
        "PUMP1_REGISTER": {
            "register": 101,
            "len": 1,
            "val": 255,
            "on_set_cb": set_pump_callback    
        },
        "PUMP2_REGISTER": {
            "register": 102,
            "len": 1,
            "val": 255,
            "on_set_cb": set_pump_callback    
        },        
    }    
}

from umodbus.serial import ModbusRTU
import os
from umodbus import version
import json

import modbus_registers

slave_addr = 10             # address on bus as client
modbus_baud = 19200

# the following definition is for a RP2
rtu_pins = (Pin(12), Pin(13))     # (TX, RX)
uart_id = 0

client = ModbusRTU(
    addr=slave_addr,        # address on bus
    pins=rtu_pins,          # given as tuple (TX, RX)
    baudrate=modbus_baud,        # optional, default 9600
    data_bits=8,          # optional, default 8
    stop_bits=1,          # optional, default 1
    parity=None,          # optional, default None
    ctrl_pin=26,          # optional, control DE/RE
    uart_id=uart_id         # optional, default 1, see port specific documentation
)

# define Modbus Registers here
register_definitions = modbus_registers.registers

print('Setting up registers ...')
# use the defined values of each register type provided by register_definitions
client.setup_registers(registers)
print('Register setup done')

print('Serving as RTU client on address {} at {} baud'.
      format(slave_addr, modbus_baud))

i2c_display.displayline4 = "RTU address: {}".format(10)
i2c_display.displayline5 = "RTU Baud: {}".format(19200)
i2c_display.displayline6 = ""