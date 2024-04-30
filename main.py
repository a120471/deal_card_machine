from machine import Pin
import rp2
import time

from doudizhu_shuffling import dou_di_zhu_shuffle
from motor_control import Motor, PID

k_ROTATION_RANGE = 180  # degrees


def indices_to_degrees(indices):
  max_i = max(indices)
  degrees = [i * k_ROTATION_RANGE / max_i - k_ROTATION_RANGE / 2 for i in indices]
  return degrees


if __name__ == '__main__':
  lcd_bl = Pin(25, mode=Pin.OUT, value=0)
  while True:
    if rp2.bootsel_button() == 1:
      break
    time.sleep(0.1)

  indices = dou_di_zhu_shuffle()
  degrees = indices_to_degrees(indices)
  # print(indices)
  # print(degrees)

  # PID version
  if False:
    motor_yaw = Motor(5, 4, 1, 0)
    pid_yaw = PID(motor_yaw)
    motor_deal_card = Motor(3, 2)
    for degree in degrees:
      cur_pos = motor_yaw.read_pos() * 360 / pid_yaw.pos_ticks_per_rev
      while abs(cur_pos - degree) > 1:
        pid_yaw.set_position(degree)
        cur_pos = motor_yaw.read_pos() * 360 / pid_yaw.pos_ticks_per_rev
      motor_yaw.stop()

      motor_deal_card.speed_ratio(0.1)
      time.sleep(0.01)
      motor_deal_card.stop()

      time.sleep(1)
  else:
    def _rotate_yaw(motor, delta_degree):
      if delta_degree == 0:
        return

      k_MOTOR_SPEED_RATIO = 0.4
      if delta_degree > 0:
        motor.speed_ratio(k_MOTOR_SPEED_RATIO)
      else:
        motor.speed_ratio(-k_MOTOR_SPEED_RATIO)
      dt = abs(delta_degree) * 0.003 + 0.1
      time.sleep(dt)
      motor.stop()

      time.sleep(1)

    motor_yaw = Motor(5, 4)
    motor_deal_card = Motor(3, 2)
    cur_degree = 0
    for tar_degree in degrees:
      delta_degree = tar_degree - cur_degree
      cur_degree = tar_degree

      _rotate_yaw(motor_yaw, delta_degree)

      motor_deal_card.speed_ratio(0.5)
      time.sleep(0.2)
      motor_deal_card.stop()
      time.sleep(0.5)

    # return to the initial position
    _rotate_yaw(motor_yaw, -cur_degree)
