from machine import Pin, PWM

led_R=PWM(Pin(4))
led_G=PWM(Pin(3))
led_B=PWM(Pin(0))
led_W=PWM(Pin(1))
led_R.freq(1000)
led_G.freq(1000)
led_B.freq(1000)
led_W.freq(1000)

def update_pwm_leds(red, green, blue, white):
  led_R.duty_u16(red * 65535 // 255)
  led_G.duty_u16(green * 65535 // 255)
  led_B.duty_u16(blue * 65535 // 255)
  led_W.duty_u16(white * 65535 // 255)
    
