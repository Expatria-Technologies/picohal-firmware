# -*- coding: utf-8 -*-

""" Pulse counter.

Original code by davehylands
See: https://github.com/dhylands/upy-examples/blob/master/pico/pio_pulse_counter.py
"""

import machine
import rp2


class PulseCounter:
    """

    _num is used as State Machine ID (4 to 7 to use PIO 1)
    """
    _num = 4 - 1
    
    def __init__(self, stepPin):
        """

        pin should be a machine.Pin instance.
        """
        PulseCounter._num += 1
        if PulseCounter._num > 7:
            raise RuntimeError("Too many PulseCounter instances")
        
        if not isinstance(stepPin, machine.Pin):
            stepPin = machine.Pin(stepPin, machine.Pin.IN)
            
        self._stepPin = stepPin

        self._sm = rp2.StateMachine(PulseCounter._num)
        
        self.value = 0
        self.direction = 'up'
        
    @staticmethod
    @rp2.asm_pio()
    def _pioCodeUp():
        """
        """
        label("loop")
        
        # Wait for a rising edge
        wait(0, pin, 0)
        wait(1, pin, 0)
        
        # Inc X (invert -> dec -> invert)
        label("inc")
        mov(x, invert(x))
        jmp(x_dec, "next")
        label("next")
        mov(x, invert(x))
        
    @staticmethod
    @rp2.asm_pio()
    def _pioCodeDown():
        """
        """
        label("loop")
        
        # Wait for a rising edge
        wait(0, pin, 0)
        wait(1, pin, 0)
        
        # Dec X
        jmp(x_dec, "loop")

    @property
    def value(self):
        """
        """
        self._sm.exec("mov(isr, x)")
        self._sm.exec("push()")
        
        return self._sm.get() - 2147483648

    @value.setter
    def value(self, val):
        """
        """
        
        # Stop the StateMachine
        self._sm.active(0)
        
        # Initialize to val
        self._sm.put(2147483648 + val)
        self._sm.exec("pull()")
        self._sm.exec("mov(x, osr)")
        
        # Start the StateMachine
        self._sm.active(1)

    @property
    def direction(self):
        """
        """
        return self._direction
    
    @direction.setter
    def direction(self, dir_):
        """
        """
        
        # Stop the StateMachine
        self._sm.active(0)

        self._direction = dir_

        if dir_ == 'up':
            self._sm.init(self._pioCodeUp, in_base=self._stepPin)
            
        elif  dir_ == 'down':
            self._sm.init(self._pioCodeDown, in_base=self._stepPin)
        
        # Start the StateMachine
        self._sm.active(1)


def main():
    """
    """
    stepPin = machine.Pin(2, machine.Pin.OUT)
    stepPin.low()
    
    counter = PulseCounter(stepPin)
    print(counter.value)
    
    counter.value = 1000
    for i in range(10):
        stepPin.high()
        stepPin.low()
    print(counter.value)
    
    counter.direction = 'down'
    for i in range(100):
        stepPin.high()
        stepPin.low()
    print(counter.value)


if __name__ == "__main__":
    main()
    
    