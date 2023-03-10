from umodbus.serial import ModbusRTU

# RTU Client/Slave setup

# the following definition is for a RP2
rtu_pins = (Pin(15), Pin(16))     # (TX, RX)
uart_id = 0
#
# rtu_pins = (Pin(4), Pin(5))     # (TX, RX)
# uart_id = 1

slave_addr = 10             # address on bus as client

client = ModbusRTU(
    addr=slave_addr,        # address on bus
    pins=rtu_pins,          # given as tuple (TX, RX)
    # baudrate=9600,        # optional, default 9600
    # data_bits=8,          # optional, default 8
    # stop_bits=1,          # optional, default 1
    # parity=None,          # optional, default None
    # ctrl_pin=12,          # optional, control DE/RE
    uart_id=uart_id         # optional, default 1, see port specific documentation
)

register_definitions = {
    "COILS": {
        "EXAMPLE_COIL": {
            "register": 123,
            "len": 1,
            "val": 1
        }
    },
    "HREGS": {
        "EXAMPLE_HREG": {
            "register": 93,
            "len": 1,
            "val": 19
        }
    },
    "ISTS": {
        "EXAMPLE_ISTS": {
            "register": 67,
            "len": 1,
            "val": 0
        }
    },
    "IREGS": {
        "EXAMPLE_IREG": {
            "register": 10,
            "len": 1,
            "val": 60001
        }
    }
}

# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping RTU client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))