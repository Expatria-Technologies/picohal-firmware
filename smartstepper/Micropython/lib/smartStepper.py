# -*- coding: utf-8 -*-

""" Stepper control.

TODO:
    x update jog routine
    x allow several (max 4?) instances (share PIO)
    x generate accel slices in speed instead of time CANCELED
    x update position
    x use DMA class
    x move State Machine functions to dedicated module
    - implement timeout
    - implement error management -> status
    - implement enable pin
    x centralize accel computations
    - dynamically compute NB_ACCEL_PTS (which criteria?)
    - remove decel during stop?

BUGS:
    -
"""

import time
import math
import machine

import pulseGenerator
import pulseCounter

NB_ACCEL_PTS   = 100
CONST_SPEED_DT = const(0.1)  # s


class SmartStepperError(Exception):
    """ SmartStepperError class
    """
    pass


class SmartStepper:
    """ SmartStepper class
    """
    def __init__(self, stepPin, dirPin, enablePin=None, accelCurve='smooth2'):
        """ Init SmartStepper object

        accelCurve can be in ('linear', smooth1', 'smooth2', 'sine')
        """
        if not isinstance(stepPin, machine.Pin):
            stepPin = machine.Pin(stepPin, machine.Pin.OUT)

        if not isinstance(dirPin, machine.Pin):
            dirPin = machine.Pin(dirPin, machine.Pin.OUT)

#         if enablePin != None and not isinstance(enablePin, machine.Pin):
#             enablePin = machine.Pin(enablePin,machine.Pin.OUT)

        self._directionPin = dirPin
#         self._enablePin = enablePin

        self._stepsPerUnit = 1    # steps per unit
        self._minSpeed = 10       # minimum speed, in units per second
        self._maxSpeed = 100      # maximum speed, in units per second
        self._acceleration = 100  # acceleration, in units per second square
        self._reverse = False     # reverse dirPin level

        self._target = 0          # target position, in units
        self._direction = None    # current direction

        self._accelTable = []
        self._initAccelTable(accelCurve)

        self._pulseGenerator = pulseGenerator.PulseGenerator(stepPin)
        self._pulseCounter = pulseCounter.PulseCounter(stepPin)

    def _initAccelTable(self, accelCurve='smooth2'):
        """ Init acceleration table
        """
        for i in range(NB_ACCEL_PTS+1):
            t = i / NB_ACCEL_PTS
            y = self._accel(t, accelCurve)
            self._accelTable.append(y)

    def _accel(self, x, accelCurve='smooth2'):
        """ Compute acceleration
        """
        if accelCurve == 'linear':
            return x

        elif accelCurve == 'smooth1':
            return x * x * (3 - 2 * x)

        elif accelCurve == 'smooth2':
            return x * x * x * (x * (x * 6 - 15) + 10)

        elif accelCurve == 'sine':
            return (math.cos((x + 1) * math.pi) + 1) / 2

        else:
            raise SmartStepperError(f"Unknown '{accelCurve}' acceleration curve")

    def _accelPoints(self, maxSpeed):
        """ Compute acceleration points
        """
        points = []

        accelTime = (maxSpeed - self._minSpeed) / self._acceleration
        accelDist = (maxSpeed**2 - self._minSpeed**2) / (2 * self._acceleration)
        accelSteps = round(accelDist * self._stepsPerUnit)

        realSteps = 0
        dt = accelTime / NB_ACCEL_PTS
        for i in range(NB_ACCEL_PTS):
            y = self._accelTable[i]
            speed = maxSpeed * y + self._minSpeed * (1 - y)
            pulses = round(speed * self._stepsPerUnit * dt)
            if pulses:
                points.append((speed * self._stepsPerUnit, pulses))
            realSteps += pulses

        # Correction
        if realSteps < accelSteps:
            points.append((round(maxSpeed * self._stepsPerUnit), accelSteps-realSteps))

        elif realSteps > accelSteps:
            raise RuntimeError("Overshoot!")

        return points

    def _constSpeedPoints(self, speed, constDist):
        """ Compute constant speed points
        """
        points = []

        constSteps = round(constDist * self._stepsPerUnit)
        constTime = constDist / speed

        nbPoints = int(constTime / CONST_SPEED_DT)
        if nbPoints:
            pulses = int(constSteps / nbPoints)
            realSteps = 0
            for i in range(nbPoints):
                if pulses:
                    points.append((speed * self._stepsPerUnit, int(pulses)))
                realSteps += pulses
        else:
            realSteps = 0

        # Correction
        if realSteps < constSteps:
            points.append((speed * self._stepsPerUnit, constSteps-realSteps))

        elif realSteps > constSteps:
            raise RuntimeError("Overshoot!")

        return points

    def _updateDirection(self, direction):
        """ Update dir pin / pulseCounter according to direction
        """
        if direction == 'up':
            self._directionPin.high()
            self._pulseCounter.direction = 'up'

        else:
            self._directionPin.low()
            self._pulseCounter.direction = 'down'

        self._direction = direction

        if self._reverse:
            self._directionPin.toggle()

    @property
    def minSpeed(self):
        """ Get the min speed

        minSpeed is in units per second.
        """
        return self._minSpeed

    @minSpeed.setter
    def minSpeed(self, value):
        """ Set the min speed

        minSpeed is in units per second.
        """
        if self.moving:
            raise SmartStepperError("Can't change 'min speed' while moving")

        if value == 0:
            raise SmartStepperError("min speed must be > 0")

        if value > self._maxSpeed:
            raise SmartStepperError("min speed must be <= max speed")

        self._minSpeed = value

    @property
    def maxSpeed(self):
        """ Get the max speed

        maxSpeed is in units per second.
        """
        return self._maxSpeed

    @maxSpeed.setter
    def maxSpeed(self, value):
        """ Set the max speed

        maxSpeed is in units per second.
        """
        if self.moving:
            raise SmartStepperError("Can't change 'max speed' while moving")

        if value == 0:
            raise SmartStepperError("max speed must be > 0")

        if value < self._minSpeed:
            raise SmartStepperError("max speed must be >= min speed")

        self._maxSpeed = value

    @property
    def speed(self):
        """ Get the current speed

        speed is in units per second.
        """
        return self._pulseGenerator.freq / self._stepsPerUnit

    @property
    def direction(self):
        """ Get the current direction
        """
        return self._direction

    @property
    def acceleration(self):
        """ Get the acceleration

        acceleration is in units per second square.
        """
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value):
        """ Set the acceleration

        acceleration is in units per second square.
        """
        if self.moving:
            raise SmartStepperError("Can't change 'acceleration' while moving")

        self._acceleration = value

    @property
    def stepsPerUnit(self):
        """ Get the number of steps per unit
        """
        return self._stepsPerUnit

    @stepsPerUnit.setter
    def stepsPerUnit(self, value):
        """ Set the number of steps per unit
        """
        if self.moving:
            raise SmartStepperError("Can't change 'steps per unit' while moving")

        self._stepsPerUnit = value

    @property
    def reverse(self):
        """ get the reverse flag
        """
        return self._reverse

    @reverse.setter
    def reverse(self, value):
        """ Set the reverse flag
        """
        if self.moving:
            raise SmartStepperError("Can't change 'reverse' flag while moving")

        self._reverse = value

    @property
    def target(self):
        """ get the target

        Target is in units.
        """
        return self._target

    @property
    def position(self):
        """ Get the current position

        Position is in units.
        """
        return self._pulseCounter.value / self._stepsPerUnit

    @position.setter
    def position(self, value):
        """ Set the current position

        Can be used to reset the position.
        Position is in units.
        """
        if self.moving:
            raise SmartStepperError("Can't change 'position' while moving")

        self._pulseCounter.value = value

    @property
    def moving(self):
        """ Check if moving
        """
        return self.speed != 0

    def jog(self, maxSpeed=None, direction='up'):
        """ Jog at given speed

        maxSpeed is in units per second.
        Handle acceleration.
        Non blocking.
        """
        if self.moving:
            raise SmartStepperError("Can't 'jog' while moving")

        if maxSpeed is None:
            maxSpeed = self._maxSpeed

        elif not self._minSpeed <= maxSpeed <= self._maxSpeed:
            raise SmartStepperError("'maxSpeed' is out of range")

        self._updateDirection(direction)

        points = []

        # Acceleration
        points.extend(self._accelPoints(maxSpeed))

        # Constant speed
        maxDist = 10 * maxSpeed  # 10s
        points.extend(self._constSpeedPoints(maxSpeed, maxDist))

        # Start the generator
        self._pulseGenerator.start(points)

    def moveTo(self, target, relative=False):
        """ Move to target

        target is in units.
        Handle acceleration.
        Non blocking.
        """
        print("\nTRACE::moveTo()")

        if self.moving:
            raise SmartStepperError("Can't 'moveto' while moving")

        if not relative:
            self._target = target
        else:
            self._target = self.position + target

        # Compute direction
        if self._target > self.position:
            self._updateDirection('up')

        else:
            self._updateDirection('down')

        points = []

        # Max speed depends on target distance from current position
        # accelTime = (maxSpeed - self._minSpeed) / self._acceleration
        # accelDist = (maxSpeed + self._minSpeed) / 2 * accelTime
        # -> accelDist = (maxSpeed² - self._minSpeed²) / (2 * self._acceleration)
        # condition: accelDist <= abs(self._target - self.position) / 2
        maxSpeed = math.sqrt((abs(self._target - self.position) * 2 * self._acceleration + 2 * self._minSpeed**2) / 2)
        maxSpeed = min(maxSpeed, self._maxSpeed)

        # Acceleration
        accelPoints = self._accelPoints(maxSpeed)
        points.extend(accelPoints)

        # Constant speed
        if maxSpeed == self._maxSpeed:
            accelDist = (maxSpeed**2 - self._minSpeed**2) / (2 * self._acceleration)
            constDist = abs(self._target - self.position) - 2 * accelDist
            points.extend(self._constSpeedPoints(maxSpeed, constDist))

        # Deceleration
        accelPoints.reverse()
        points.extend(accelPoints)

        # Start the generator
        self._pulseGenerator.start(points)

    def stop(self, emergency=False):
        """ Stop the motor

        Use deceleration unless emergency is True.
        """
        if not self.moving:
            raise SmartStepperError("Can't 'stop' while not moving")

        maxSpeed = self.speed

        if emergency:
            self._pulseGenerator.stop()

        else:
            points = self._accelPoints(maxSpeed)
            points.reverse()
            points.extend(points)

            # Start the DMA
            self._pulseGenerator.start(points)
            #self._pulseGenerator.skip()

    def waitEndOfMove(self):
        """
        """
        while stepper.moving:
            time.sleep_ms(1)


def jog(stepper):
    """
    """
    t0 = time.ticks_ms()
    stepper.position = 0
    stepper.jog(50)

    t = time.ticks_ms()
    while (time.ticks_ms() - t < 1500):
        print("time={:6.3f}s speed={:+6.1f}mm/s pos={:+7.1f}mm".format((time.ticks_ms()-t0)/1000, stepper.speed, stepper.position))

    t = time.ticks_ms()
    stepper.stop()

    t = time.ticks_ms()
    while (time.ticks_ms() - t < 1500):
        print("time={:6.3f}s speed={:+6.1f}mm/s pos={:+7.1f}mm".format((time.ticks_ms()-t0)/1000, stepper.speed, stepper.position))

#     stepper.position = 0
    stepper.jog(40, 'down')

    t = time.ticks_ms()
    while (time.ticks_ms() - t < 1500):
        print("time={:6.3f}s speed={:+6.1f}mm/s pos={:+7.1f}mm".format((time.ticks_ms()-t0)/1000, stepper.speed, stepper.position))

    stepper.stop(emergency=True)

    t = time.ticks_ms()
    while (time.ticks_ms() - t < 500):
        print("time={:6.3f}s speed={:+6.1f}mm/s pos={:+7.1f}mm".format((time.ticks_ms()-t0)/1000, stepper.speed, stepper.position))


def moveTo(stepper):
    """
    """
    print("\nINFO::Testing 'moveto'...")

    t = time.ticks_ms()
    stepper.moveTo(200)

    while (time.ticks_ms() - t < 6000):
        print("time={:6.3f}s speed={:+6.1f}mm/s pos={:+7.1f}mm".format((time.ticks_ms()-t)/1000, stepper.speed, stepper.position))

    t = time.ticks_ms()
    stepper.moveTo(150)

    while (time.ticks_ms() - t < 3000):
        print("time={:6.3f}s speed={:+6.1f}mm/s pos={:+7.1f}mm".format((time.ticks_ms()-t)/1000, stepper.speed, stepper.position))


def moveToRel(stepper):
    """
    """
    print("\nINFO::Testing relative 'moveto'...")

    t = time.ticks_ms()
    stepper.position = 0
    stepper.moveTo(80, relative=True)

    while (time.ticks_ms() - t < 4000):
        print("time={:6.3f}s speed={:+6.1f}mm/s pos={:+7.1f}mm".format((time.ticks_ms()-t)/1000, stepper.speed, stepper.position))

    t = time.ticks_ms()
    stepper.moveTo(-50, relative=True)

    while (time.ticks_ms() - t < 3000):
        print("time={:6.3f}s speed={:+6.1f}mm/s pos={:+7.1f}mm".format((time.ticks_ms()-t)/1000, stepper.speed, stepper.position))


def debug(stepper):
    """
    """
    t = time.ticks_ms()
    stepper.moveTo(50)
    print("\nINFO::starting with target: {:.1f}mm / {:d}steps".format(stepper.target, round(stepper.target*stepper.stepsPerUnit)))

    while not stepper.moving:
        time.sleep_ms(1)
    print("INFO::Moving...")

#     print("  time  speed     pos")
    while stepper.moving:
#         print("{:6.3f} {:+6.1f} {:+7.1f}".format((time.ticks_ms()-t)/1000, stepper.speed, stepper.position))
#
#         if time.ticks_ms()-t >= 5000:
#             stepper.stop()
#             while stepper.moving:
#                 print("{:6.3f} {:+6.1f} {:+7.1f}".format((time.ticks_ms()-t)/1000, stepper.speed, stepper.position))

        time.sleep_ms(1)

    print("\nINFO::done: pulse counter: {:.1f}mm / {:d}steps".format(stepper.position, stepper._pulseCounter.value))

    print("\n  time speed")
    for t, freq in stepper._pulseGenerator.data:
        print("{:6.3f} {:5.1f}".format(t/1000, freq / stepper.stepsPerUnit))


def main():
    """
    """
    print("TRACE::main()")
    stepper = SmartStepper(21, 22, accelCurve='smooth2')
    stepper.stepsPerUnit = 96.
    stepper.minSpeed = 1
    stepper.maxSpeed = 50
    stepper.acceleration = 100

    #jog(stepper)
    #moveTo(stepper)
    #moveToRel(stepper)
    debug(stepper)


if __name__ == "__main__":
    main()
