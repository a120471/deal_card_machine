# Reference doc: https://docs.micropython.org/en/latest/library/machine.html
# Reference doc: https://www.waveshare.net/wiki/RP2040-LCD-0.96
from machine import Pin, PWM, SPI
import time

# ========================================
# define a normal output
E2A = Pin(0, mode=Pin.IN)  # physical pin 1
E2B = Pin(1, mode=Pin.IN)  # physical pin 2

# AIN2 = Pin(2, mode=Pin.OUT, value=0)  # physical pin 4
# AIN1 = Pin(3, mode=Pin.OUT, value=0)  # physical pin 5
BIN2 = Pin(4, mode=Pin.OUT, value=0)  # physical pin 6
BIN1 = Pin(5, mode=Pin.OUT, value=0)  # physical pin 7

# AIN1.value(1)
BIN1.value(1)
time.sleep(1)
# AIN1.value(0)
BIN1.value(0)

# init/set value
# gp0.value(1)
# gp output can be toggled
# gp0.toggle()

# # ========================================
# # define a PWM output
# gp4 = PWM(dest=Pin(4), freq=1000, duty_u16=32768)  # physical pin 6

# # ========================================
# # if a pin is used as the input, and it's connected to 3V3(OUT), i.e. physical pin 36,
# # we'd usually have the following code
# gp28 = Pin(28, mode=Pin.IN, pull=Pin.PULL_DOWN)  # physical pin 34
# # Similarly, if a pin is connected to GND, we'd have the following code
# gp27 = Pin(27, mode=Pin.IN, pull=Pin.PULL_UP)  # physical pin 32

# # register an interrupt for gp28
# def interrupt_handler(pin):
#     print('Interrupt Detected')
# gp28.irq(handler=interrupt_handler, trigger=Pin.IRQ_RISING)
