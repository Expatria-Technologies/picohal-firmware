from peristaltic_pump import set_pump_callback
from coolant_control import set_coolant_callback
from event_handler import event_callback
from spindle_control import set_spindle_callback
from indicator_lights import set_status_callback
import i2c_display

from nuts_bolts import enum

from machine import Pin

slave_addr = 10             # address on bus as client
modbus_baud = 9600
    
def set_output_callback(reg_type, address, val):
    print('output pin update received')

registers = {
    "HREGS": {
        "STATUS_REGISTER": {
            "register": 0x01,
            "len": 1,
            "val": 255,
            "on_set_cb": set_status_callback    
        },
        "ALARM_REGISTER": {
            "register": 0x02,
            "len": 1,
            "val": 0,   
        },         
        "INPUT_REGISTER": {
            "register": 0x03,
            "len": 1,
            "val": 255,    
        },
        "OUTPUT_REGISTER": {
            "register": 0x04,
            "len": 1,
            "val": 0,
            "on_set_cb": set_output_callback    
        },
        "EVENT_REGISTER": {
            "register": 0x05,
            "len": 1,
            "val": 0,
            "on_set_cb": event_callback    
        },          
        "COOLANT_REGISTER": {
            "register": 0x100,
            "len": 1,
            "val": 0,
            "on_set_cb": set_coolant_callback    
        },
        "PUMP1_REGISTER": {
            "register": 0x101,
            "len": 1,
            "val": 255,
            "on_set_cb": set_pump_callback    
        },
        "PUMP2_REGISTER": {
            "register": 0x102,
            "len": 1,
            "val": 255,
            "on_set_cb": set_pump_callback    
        },
        "SPINDLE_RUN_REGISTER": {
            "register": 0x200,
            "len": 1,
            "val": 0,
            "on_set_cb": set_spindle_callback    
        },
        "SPINDLE_SET_RPM_REGISTER": {
            "register": 0x201,
            "len": 1,
            "val": 0,
            "on_set_cb": set_spindle_callback    
        },        
        "ACTIVE_SPINDLE_REGISTER": {
            "register": 0x202,
            "len": 1,
            "val": 0,
            "on_set_cb": set_spindle_callback    
        },
        "ACTIVE_SPINDLE_RPM_REGISTER": {
            "register": 0x203,
            "len": 1,
            "val": 0,    
        },
        "ACTIVE_TOOL_REGISTER": {
            "register": 0x300,
            "len": 1,
            "val": 0,    
        },
        "NEXT_TOOL_REGISTER": {
            "register": 0x301,
            "len": 1,
            "val": 0,    
        },
        "ACTIVE_TOOL_POCKET": {
            "register": 0x301,
            "len": 1,
            "val": 0,    
        },
        "NEXT_TOOL_POCKET": {
            "register": 0x301,
            "len": 1,
            "val": 0,    
        },         
    }    
}

from umodbus.serial import ModbusRTU
import os
from umodbus import version
import json

import modbus_registers

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
i2c_display.displayline4 = ""
i2c_display.displayline5 = "RTU address: {}".format(slave_addr)
i2c_display.displayline6 = "RTU Baud: {}".format(modbus_baud)
