# -*- coding: utf-8 -*-

""" Pulse generator.
"""

import gc
import time
import array
import uctypes
import machine
import rp2

import dma

SM_FREQ = 10_000_000  # Hz

DMA_DREQ_PIO0_TXn = (
    dma.DMA.DREQ_PIO0_TX0,
    dma.DMA.DREQ_PIO0_TX1,
    dma.DMA.DREQ_PIO0_TX2,
    dma.DMA.DREQ_PIO0_TX3
)

PIO_0_TXFn = (
    dma.PIO_0.BASE + dma.PIO_0.TXF0,
    dma.PIO_0.BASE + dma.PIO_0.TXF1,
    dma.PIO_0.BASE + dma.PIO_0.TXF2,
    dma.PIO_0.BASE + dma.PIO_0.TXF3
)


class PulseGenerator:
    """ Pulses generator

    _num is used as State Machine ID (0 to 3 to use PIO 0) and DMA channel.
    """
    _num = 0 - 1
    
    def __init__(self, pin):
        """
        """
        PulseGenerator._num += 1
        if PulseGenerator._num > 3:
            raise RuntimeError("Too many PulseGenerator instances")
        
        self._pin = pin
        
        self._pulseLength = 0
        
        # Debug
        self._startTime = None
        self._data = None
        
        self._dma = dma.DMA(chan=PulseGenerator._num)
        self._dma.abort()
        
        self._sm = rp2.StateMachine(PulseGenerator._num, self._pioCode, freq=SM_FREQ, sideset_base=pin)
        self._sm.irq(self._pulseLengthISR)
        self._sm.active(1)

    @staticmethod
    @rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
    def _pioCode():
        """

        In the routine, ISR contains pulseLength setpoint, and Y nbPulses counter.
        X is used as pulseLength counter for each level. Y is decremented until 0.
        """
        
        # Get input values (pulseLength, nbPulses)
        # Blocking
        pull().side(0)          # pull pulseLength from TX FIFO to OSR; set output LOW
        mov(x, osr)             # store pulseLength to X
        
        # Update freq
        mov(isr, x)             # store pulseLength to ISR
        push()                  # push back pulseLength in RX FIFO
        irq(noblock, rel(0))    # notify ARM a new pulseLength is available
        
        # Cancel if pulseLength is 0
        mov(y, osr)             # store pulseLength to Y
        pull()                  # pull nbPulses from TX FIFO to OSR
        jmp(y_dec, "end")       # jump to 'end' if Y is 0
        
        mov(y, osr)             # store nbPulses to Y
        mov(osr, x)             # store back pulseLength to OSR

        # Start pulsing (square)
        label("start")
        
        mov(x, osr).side(1)     # put previously saved pulseLength to counter; set output HIGH
        label("loopHigh")
        jmp(x_dec, "loopHigh")  # loop if pulseLength is non 0; decrement pulseLength counter in all cases
        
        mov(x, osr).side(0)     # put previously saved pulseLength to counter; set output LOW
        label("loopLow")
        jmp(x_dec, "loopLow")   # loop if pulseLength is non 0; decrement pulseLength counter in all cases
        
        jmp(y_dec, "start")     # loop if nbPulses is non 0; decrement nbPulses counter in all cases
        
        label("end")

    def _pulseLengthISR(self, smId):
        """
        """
        self._pulseLength = self._sm.get()
        self._data.append((time.ticks_ms(), self._pulseLength))

    @property
    def freq(self):
        """ Return current frequency.
        """
        try:
            freq = round(SM_FREQ / self._pulseLength / 2)
        except ZeroDivisionError:
            freq = 0
        
        return freq

    @property
    def data(self):
        """ Debug
        """
        gc.collect()
        
        if self._data is None:
            raise RuntimeError("No data available yet")
        
        data = []
        for t, pulseLength in self._data:
            if pulseLength != 0:
                data.append((t - self._startTime, round(SM_FREQ / pulseLength / 2)))
                
        return data

    def start(self, points):
        """

        points contains n tuples (freq, nbPulses) values.
        """
        sequence = array.array('I')

        for freq, nbPulses in points:
            sequence.append(round(SM_FREQ / freq / 2))
            sequence.append(nbPulses - 1)
        
        # Add a final fake pulse to tell the State Machine that the sequence is over
        sequence.extend(array.array('I', (0, 0)))

        #print(sequence)

        self._dma.abort()  # stop DMA
        self._dma.config(
            readAddr = uctypes.addressof(sequence),
            writeAddr = PIO_0_TXFn[PulseGenerator._num],
            transCount = len(sequence),
            readInc = True,
            writeInc = False,
            treqSel = DMA_DREQ_PIO0_TXn[PulseGenerator._num],
            dataSize = dma.DMA.SIZE_WORD
        )
        self._dma.enable()  # start DMA
        self._startTime = time.ticks_ms()
        self._data = []

    def skip(self):
        """ Skip current pulse.
        """
        self._sm.exec("mov(y, null)")    # Stop steps loop
        self._sm.exec("mov(osr, null)")  # stop pulseLengh loops
        self._sm.exec("mov(x, null)")    # stop pulseLengh loops
        
    def stop(self):
        """
        """
        self._dma.abort()  # stop DMA
        
        # self._sm.tx_fifo()
        self._sm.exec("pull(noblock)")   # clear TX FIFO
        self._sm.exec("pull(noblock)")   # clear TX FIFO
        self._sm.exec("pull(noblock)")   # clear TX FIFO
        self._sm.exec("pull(noblock)")   # clear TX FIFO
        
        self._sm.exec("mov(y, null)")    # Stop steps loop
        self._sm.exec("mov(osr, null)")  # stop pulseLengh loops
        self._sm.exec("mov(x, null)")    # stop pulseLengh loops
        
        self._sm.exec("nop().side(0)")   # ensure pulse is low

        self._pulseLength = 0  # needed?


def main():
    """
    """
    pulseGenerator = PulseGenerator(machine.Pin(25, machine.Pin.OUT))
    points = ((1, 3), (5, 5))
    pulseGenerator.start(points)
    
    t = time.ticks_ms()
    print("freq TX FIFO")
    while pulseGenerator.freq:
        print("{:04d} {:02d}".format(pulseGenerator.freq, pulseGenerator._sm.tx_fifo()))
        
        if time.ticks_ms()-t > 91200:
            pulses.stop()
            break
        
        time.sleep(0.25)

    print("{:04d} {:02d}".format(pulseGenerator.freq, pulseGenerator._sm.tx_fifo()))
    
    print("\n  time freq")
    for t, freq in pulseGenerator.data:
        print(f"{t:6d} {freq:4d}")
    

if __name__ == "__main__":
    main()
