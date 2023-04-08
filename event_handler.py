from nuts_bolts import program_flow
from collections import deque
import modbus_registers

from indicator_lights import finish_flag

event_queue = deque((),16)

def process_event():
    global event_queue
    try:
        event = event_queue.popleft()
        print('Processing {}'.format(event))
    except IndexError as e:
        return
    
    if int(event) == int(program_flow.PROGRAM_COMPLETED) :
        print('finish flag')
        finish_flag()
        return

def event_callback(reg_type, address, val):
    global event_queue
    print('event received')
    event_queue.append(val[0])
    