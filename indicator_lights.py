from nuts_bolts import current_state, program_flow
from pwm_led_control import update_pwm_leds

def update_led_state():
    from modbus_registers import client
    if client.get_hreg(1) == current_state.STATE_ALARM :
        update_pwm_leds(255,0,0,0)
        return
    elif client.get_hreg(1) == current_state.STATE_CYCLE :
        update_pwm_leds(0,255,0,255)
        return
    elif client.get_hreg(1) == current_state.STATE_HOLD :
        update_pwm_leds(128,128,0,255)
        return
    elif client.get_hreg(1) == current_state.STATE_IDLE :
        update_pwm_leds(0,0,0,255)
        return
    elif client.get_hreg(1) == current_state.STATE_TOOL_CHANGE :
        update_pwm_leds(0,0,255,255)
        return
    elif client.get_hreg(1) == current_state.STATE_HOMING :
        update_pwm_leds(0,0,255,255)
        return
    elif client.get_hreg(1) == current_state.STATE_JOG :
        update_pwm_leds(0,255,0,0)
        return    
    else :
        update_pwm_leds(0,0,0,0)
        
def process_indicators():
    #print("updating indicators")
    update_led_state()
    
def set_status_callback(reg_type, address, val):
    # global client
    #print('status update received')
    process_indicators()