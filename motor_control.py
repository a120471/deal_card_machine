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
    def __init__(
        self,
        out1_id,
        out2_id,
        hall_in1_id=None,
        hall_in2_id=None,
        reverse_direction=False,
        freq=50,
    ):
        # Variable for recording the current position of the encoder
        self._pos = 0

        # For this specific motor, the minimum supported speed ratio is around 0.055
        self.MIN_MOTOR_SPEED_RATIO = 0.055

        # Whether the motor should rotate in the reverse direction
        self.REVERSE_DIRECTION = reverse_direction

        self.O1 = PWM(Pin(out1_id, mode=Pin.OUT), freq=freq, duty_u16=U16_MAX)
        self.O2 = PWM(Pin(out2_id, mode=Pin.OUT), freq=freq, duty_u16=U16_MAX)

        if hall_in1_id is not None and hall_in2_id is not None:
            self.H1 = Pin(hall_in1_id, mode=Pin.IN, pull=Pin.PULL_DOWN)
            self.H2 = Pin(hall_in2_id, mode=Pin.IN, pull=Pin.PULL_DOWN)
            # Interrupt initialization
            self.H1.irq(
                handler=self.handle_interrupt, trigger=Pin.IRQ_RISING, hard=True
            )

    # Interrupt handler
    def handle_interrupt(self, _):
        if self.H2.value() == 0:
            self._pos = self._pos - (1 if self.REVERSE_DIRECTION else -1)
        else:
            self._pos = self._pos + (1 if self.REVERSE_DIRECTION else -1)

    # A function for speed control without feedback(Open loop speed control)
    def speed(self, val):
        pwm = _clip(abs(val), U16_MIN, U16_MAX)
        if self.REVERSE_DIRECTION:
            val = -val

        if val > 0:
            self.O1.duty_u16(U16_MAX)
            self.O2.duty_u16(U16_MAX - pwm)
        else:
            self.O1.duty_u16(U16_MAX - pwm)
            self.O2.duty_u16(U16_MAX)

    def speed_ratio(self, val):
        if abs(val) < self.MIN_MOTOR_SPEED_RATIO:
            self.stop()
            return
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
    def __init__(self, motor, kp=1.0, kd=0.0, ki=0.0, max_u=1.0):
        # For the specific motor used here, there are 585 pos-ticks per revolution
        # of output shaft of the motor, then multiplied by any following gear
        # ratios.
        self.pos_ticks_per_rev = 585 * 3 * 5

        self.motor = motor
        self.kp = kp
        self.kd = kd
        self.ki = ki
        self.max_u = max_u
        self.reset_error()

    def reset_error(self):
        self.prev_e = math.nan
        self.integral_e = 0

    def _reset_integral_if_needed(self, curr_e):
        if self.prev_e * curr_e < 0:
            self.integral_e = 0

    # Function for calculating the Feedback signal. It takes the current value,
    # user target value and the delta time.
    def eval_u(self, cur_val, tar_val, dt):
        # Proportional
        e = tar_val - cur_val

        # Derivative
        if math.isnan(self.prev_e):
            self.prev_e = e
        derivative_e = (e - self.prev_e) / dt
        self._reset_integral_if_needed(e)
        self.prev_e = e

        # Integral
        self.integral_e = self.integral_e + e * dt

        # Control signal
        u = self.kp * e + self.kd * derivative_e + self.ki * self.integral_e
        u = (
            max(u, self.motor.MIN_MOTOR_SPEED_RATIO)
            if u > 0
            else min(u, -self.motor.MIN_MOTOR_SPEED_RATIO)
        )
        u = _clip(u, -self.max_u, self.max_u)

        return u

    # Function for closed loop motor position control
    def set_position(self, tar_deg, threshold=0.1, timeout=5.0):
        """
        Args:
            tar_deg: target motor position in degrees
            threshold: threshold for stopping the motor
            timeout: timeout seconds for stopping the motor
        """
        cur_deg = self.motor.read_pos() * 360 / self.pos_ticks_per_rev
        if abs(tar_deg - cur_deg) < threshold:
            return 0

        reaching_target_time = 0
        running_time = 0
        while reaching_target_time < 0.1 and running_time < timeout:
            # Control signal call
            dt = 0.01  # in second
            x = self.eval_u(cur_deg, tar_deg, dt)

            # Set the speed
            self.motor.speed_ratio(x)

            # Constant delay
            time.sleep(dt)

            cur_deg = self.motor.read_pos() * 360 / self.pos_ticks_per_rev
            if abs(tar_deg - cur_deg) < threshold:
                reaching_target_time += dt
            running_time += dt

        self.stop()
        return running_time

    # Function for closed loop speed control. The parameters of this function
    # is not tuned since this function is not used for now.
    # The validity of this function is not tested
    def _set_speed_untested(self, tar_speed):
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
        print(cur_speed, tar_speed)  # For debugging

    def stop(self):
        self.motor.stop()
        self.reset_error()


# if __name__ == '__main__':
#     motor = Motor(5, 4, 1, 0, True)
#     motor.speed_ratio(0.5)
#     time.sleep(1)
#     motor.stop()

#     print("pos", motor.read_pos())

#     time.sleep(0.1)
#     from machine import soft_reset
#     soft_reset()
