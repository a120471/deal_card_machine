# Modified from https://github.com/rakesh-i/MicroPython-Encoder-motor, for the
# purpose of controlling "Motor Drive Module(AT8236)".
"""
MIT License

Copyright (c) 2022 rakesh-i

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from machine import Pin, PWM, disable_irq, enable_irq
import math
import time

U16_MIN = 0
U16_MAX = 65535


def _clip(val, min_v, max_v):
    return max(min_v, min(max_v, val))


class Motor:
    # Constructor for initializing the motor pins
    def __init__(self, out1_id, out2_id, hall_in1_id=None, hall_in2_id=None, freq=50):
        # Variable for recording the current position of the encoder
        self._pos = 0

        self.O1 = PWM(Pin(out1_id, mode=Pin.OUT), freq=freq, duty_u16=U16_MIN)
        self.O2 = PWM(Pin(out2_id, mode=Pin.OUT), freq=freq, duty_u16=U16_MIN)

        if hall_in1_id is not None and hall_in2_id is not None:
            self.H1 = Pin(hall_in1_id, mode=Pin.IN, pull=Pin.PULL_DOWN)
            self.H2 = Pin(hall_in2_id, mode=Pin.IN, pull=Pin.PULL_DOWN)
            # Interrupt initialization
            # self.H1.irq(handler=self.handle_interrupt, trigger=Pin.IRQ_RISING)

            from machine import Timer
            Timer(mode=Timer.PERIODIC, freq=100, callback=self.handle_interrupt)

    # Interrupt handler
    def handle_interrupt(self, _):
        # TODO, test the validity of the following code
        print("H", self.H1.value(), self.H2.value())
        # if self.H2.value() == 0:
        #     self._pos = self._pos + 1
        # else:
        #     self._pos = self._pos - 1

    # A function for speed control without feedback(Open loop speed control)
    def speed(self, val):
        pwm = _clip(abs(val), U16_MIN, U16_MAX)

        if val > 0:
            self.O1.duty_u16(pwm)
            self.O2.duty_u16(U16_MIN)
        else:
            self.O1.duty_u16(U16_MIN)
            self.O2.duty_u16(pwm)

    def speed_ratio(self, val):
        pwm = math.floor(_clip(val, -1, 1) * U16_MAX)
        self.speed(pwm)

    def stop(self):
        self.O1.duty_u16(U16_MAX)
        self.O2.duty_u16(U16_MAX)

    def read_pos(self):
        # Disable the interrupt to read the position of the encoder(encoder tick)
        state = disable_irq()
        pos = self._pos
        # Enable the interrupt after reading the position value
        enable_irq(state)
        return pos


# A class for closed loop speed and position control
class PID:
    # Constructor for initializing PID values
    def __init__(self, motor, kp=1, kd=0, ki=0, max_u=20000, prev_e=0, integral_e=0):
        # For the specific motor used here, there are 585 pos-ticks per revolution
        # of output shaft of the motor
        self.pos_ticks_per_rev = 585

        self.motor = motor
        self.kp = kp
        self.kd = kd
        self.ki = ki
        self.max_u = max_u
        self.prev_e = prev_e
        self.integral_e = integral_e

    # Function for calculating the Feedback signal. It takes the current value,
    # user target value and the delta time.
    def eval_u(self, cur_val, tar_val, dt):
        # Proportional
        e = tar_val - cur_val

        # Derivative
        derivative_e = (e - self.prev_e) / dt
        self.prev_e = e

        # Integral
        self.integral_e = self.integral_e + e * dt

        # Control signal
        u = self.kp * e + self.kd * derivative_e + self.ki * self.integral_e
        u = _clip(u, -self.max_u, self.max_u)

        return u

    # Function for closed loop motor position control
    def set_position(self, tar_motor_rot_deg):
        """
        Args:
            tar_motor_rot_deg: target motor position in degrees
        """
        tar_pos = tar_motor_rot_deg * self.pos_ticks_per_rev / 360

        cur_pos = self.motor.read_pos()
        cur_motor_rot_deg = cur_pos * 360 / self.pos_ticks_per_rev

        dt = 0.01  # 10ms

        # Control signal call
        x = int(self.eval_u(cur_pos, tar_pos, dt))

        # Set the speed
        self.motor.speed(x)
        print(cur_motor_rot_deg, tar_motor_rot_deg) # For debugging

        # Constant delay
        time.sleep(dt)

    # Function for closed loop speed control. The parameters of this function
    # is not tuned since this function is not used for now.
    def _set_speed(self, tar_speed):
        """
        Args:
            tar_speed: target speed in RPM
        """
        # Set a large delta time because small value causes drastic speed stepping.
        dt = 0.05  # 50ms

        pos1 = self.motor.read_pos()
        # Constant delay
        time.sleep(dt)
        pos2 = self.motor.read_pos()

        # Current encoder tick rate
        pos_speed = (pos2 - pos1) / dt

        # Converted to RPM
        cur_speed = pos_speed * 60 / self.pos_ticks_per_rev

        # Call for control signal
        x = int(self.eval_u(cur_speed, tar_speed, dt))

        # Set the motor speed
        self.motor.speed(x)
        print(cur_speed, tar_speed)   # For debugging


# if __name__ == '__main__':
#     motor = Motor(5, 4, 1, 0)
#     motor.speed_ratio(0.5)
#     time.sleep(1)
#     motor.stop()

#     print("pos", motor.read_pos())

#     time.sleep(0.1)
#     from machine import soft_reset
#     soft_reset()
