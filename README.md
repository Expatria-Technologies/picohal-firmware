# picohal-firmware
Micropython firmware for the PicoHAL

This is designed to work with the PicoHAL GRBLHAL plugin but the events could be sent by any Modbus host like LinuxCNC or similar.

https://github.com/Expatria-Technologies/Plugins_picoHAL

Copied from above:
#### The PicoHAL has the following characteristics:
  - Familiar Arduino Uno inspired form factor
  - RS485 input and pass-through
  - 5-24V power input (can be USB powered)
  - Works with CNC shield
  - Works with Relay shield
  - Works with stackable relay shields

#### Shield I/O:
  - 9 true 5V outputs
  - 9 true 5V inputs
  - 5V UART interface
  - 5V I2C interface
  - 2 5V tolerant analog inputs

In addition, there are plug headers for the following:
  - 4 2 amp relay drivers (Labelled Red/Green/Blue/White
  - Buffered 5V Neopixel driver
  - 5V tolerant user input
  
Finally it has I2C exposed to mount a small 1.3 inch OLED for more visual feedback.

![image](https://user-images.githubusercontent.com/6061539/231016314-3fe6b36d-4816-46b0-a46a-63353316b156.png)
