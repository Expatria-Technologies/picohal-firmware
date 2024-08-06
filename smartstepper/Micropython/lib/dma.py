# -*- coding: utf-8 -*-

""" DMA.

Original code by Tim Collins
See: https://github.com/drtimcollins/RP2040-DMA
"""

import time
import machine


class PIO:
    """
    """
    BASE = None

    # Register indices into the array of 32 bit registers
    CTRL    = const(0)
    FSTAT   = const(1)
    FLEVEL  = const(3)

    TXF0 = const(0x10)
    TXF1 = const(0x14)
    TXF2 = const(0x18)
    TXF3 = const(0x1c)
    RXF0 = const(0x20)
    RXF1 = const(0x24)
    RXF2 = const(0x28)
    RXF3 = const(0x2c)


class PIO_0(PIO):
    """
    """
    BASE = 0x50200000


class PIO_1(PIO):
    """
    """
    BASE = 0x50300000


class SM:
    """
    """
    
    # Start of the SM state tables
    REG_BASE = const(0x32)

    # Register offsets into the per-SM state table
    CLKDIV    = const(0)
    EXECCTRL  = const(1)
    SHIFTCTRL = const(2)
    ADDR      = const(3)
    INSTR     = const(4)
    PINCTRL   = const(5)
    SIZE      = const(6)

    FIFO_RXFULL  = const(0x00000001)
    FIFO_RXEMPTY = const(0x00000100)
    FIFO_TXFULL  = const(0x00010000)
    FIFO_TXEMPTY = const(0x01000000)


class DMA:
    """
    """
    BASE = const(0x50000000)

    EN              = const(0x01 <<  0)
    HIGH_PRIORITY   = const(0x01 <<  1)

    SIZE_BYTE       = const(0x00 <<  2)
    SIZE_SHORT      = const(0x01 <<  2)
    SIZE_WORD       = const(0x02 <<  2)
    
    INCR_READ       = const(0x01 <<  4)
    INCR_WRITE      = const(0x01 <<  5)
    
    DREQ_PIO0_TX0   = const(0x00 << 15)
    DREQ_PIO0_TX1   = const(0x01 << 15)
    DREQ_PIO0_TX2   = const(0x02 << 15)
    DREQ_PIO0_TX3   = const(0x03 << 15)
    DREQ_PIO0_RX0   = const(0x04 << 15)
    DREQ_PIO0_RX1   = const(0x05 << 15)
    DREQ_PIO0_RX2   = const(0x06 << 15)
    DREQ_PIO0_RX3   = const(0x07 << 15)
    DREQ_PIO1_TX0   = const(0x08 << 15)
    DREQ_PIO1_TX1   = const(0x09 << 15)
    DREQ_PIO1_TX2   = const(0x0A << 15)
    DREQ_PIO1_TX3   = const(0x0B << 15)
    DREQ_PIO1_RX0   = const(0x0C << 15)
    DREQ_PIO1_RX1   = const(0x0D << 15)
    DREQ_PIO1_RX2   = const(0x0E << 15)
    DREQ_PIO1_RX3   = const(0x0F << 15)
    DREQ_SPI0_TX    = const(0x10 << 15)
    DREQ_SPI0_RX    = const(0x11 << 15)
    DREQ_SPI1_TX    = const(0x12 << 15)
    DREQ_SPI1_RX    = const(0x13 << 15)
    DREQ_UART0_TX   = const(0x14 << 15)
    DREQ_UART0_RX   = const(0x15 << 15)
    DREQ_UART1_TX   = const(0x16 << 15)
    DREQ_UART1_RX   = const(0x17 << 15)
    DREQ_PWM_WRAP0  = const(0x18 << 15)
    DREQ_PWM_WRAP1  = const(0x19 << 15)
    DREQ_PWM_WRAP2  = const(0x1A << 15)
    DREQ_PWM_WRAP3  = const(0x1B << 15)
    DREQ_PWM_WRAP4  = const(0x1C << 15)
    DREQ_PWM_WRAP5  = const(0x1D << 15)
    DREQ_PWM_WRAP6  = const(0x1E << 15)
    DREQ_PWM_WRAP7  = const(0x1F << 15)
    DREQ_I2C0_TX    = const(0x20 << 15)
    DREQ_I2C0_RX    = const(0x21 << 15)
    DREQ_I2C1_TX    = const(0x22 << 15)
    DREQ_I2C1_RX    = const(0x23 << 15)
    DREQ_ADC        = const(0x24 << 15)
    DREQ_XIP_STREAM = const(0x25 << 15)
    DREQ_XIP_SSITX  = const(0x26 << 15)
    DREQ_XIP_SSIRX  = const(0x27 << 15)
    TREQ_TMR0       = const(0x3B << 15)
    TREQ_TMR1       = const(0x3C << 15)
    TREQ_TMR2       = const(0x3D << 15)
    TREQ_TMR3       = const(0x3E << 15)
    TREQ_PERMANENT  = const(0x3F << 15)
    
    IRQ_QUIET       = const(0x01 << 21)
    BUSY            = const(0x01 << 24)

    CHAN_ABORT      = const(0x50000444)

    def __init__(self, chan):
        """
        """
        self._chan  = chan
        
        self.READ_ADDR   = DMA.BASE + 0x00 + chan * 0x40
        self.WRITE_ADDR  = DMA.BASE + 0x04 + chan * 0x40
        self.TRANS_COUNT = DMA.BASE + 0x08 + chan * 0x40
        self.CTRL_TRIG   = DMA.BASE + 0x0C + chan * 0x40
        self.AL1_CTRL    = DMA.BASE + 0x10 + chan * 0x40

    @property
    def transCount(self):
        """
        """
        return machine.mem32[self.TRANS_COUNT]

    @property
    def busy(self):
        """
        """
        if machine.mem32[self.CTRL_TRIG] & DMA.BUSY:
            return True
        else:
            return False

    def config(self, *, readAddr, writeAddr, transCount, readInc, writeInc, treqSel=None, chainTo=None, dataSize=SIZE_BYTE):
        """
        """
        if treqSel is None:
            treqSel = DMA.TREQ_PERMANENT

        if chainTo is None:
            chainTo = self._chan

        machine.mem32[self.CTRL_TRIG]   = 0
        machine.mem32[self.READ_ADDR]   = readAddr
        machine.mem32[self.WRITE_ADDR]  = writeAddr
        machine.mem32[self.TRANS_COUNT] = transCount

        ctrl = 0
        if readInc:
            ctrl  = DMA.INCR_READ

        if writeInc:
            ctrl |= DMA.INCR_WRITE

        machine.mem32[self.CTRL_TRIG] = ctrl | (chainTo << 11) | treqSel | DMA.IRQ_QUIET | dataSize

    def enable(self):
        """
        """
        machine.mem32[self.CTRL_TRIG] |= DMA.EN

    def enableNotrigger(self):
        """
        """
        machine.mem32[self.AL1_CTRL] |= DMA.EN

    def disable(self):
        """
        """
        machine.mem32[self.CTRL_TRIG] = 0

    def abort(self):
        """
        """
        machine.mem32[DMA.CHAN_ABORT] = 1 << self._chan
        while machine.mem32[CHAN_ABORT]:
            time.sleep_us(10)

    @staticmethod
    def abortAll():
        """
        """
        machine.mem32[DMA.CHAN_ABORT] = 0xFFFF
        while machine.mem32[CHAN_ABORT]:
            time.sleep_us(10)
