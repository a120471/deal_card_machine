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
  lcd_bl = Pin(25, mode=Pin.OUT, value=1)

  # while True:
  #   if rp2.bootsel_button() == 1:
  #     break
  #   time.sleep(0.1)

  indices = dou_di_zhu_shuffle()
  print(indices)
  degrees = indices_to_degrees(indices)
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
    motor_yaw = Motor(5, 4)
    motor_deal_card = Motor(3, 2)
    cur_degree = 0
    motor_speed_ratio = 0.4
    i = 0
    for tar_degree in degrees:
      delta_degree = tar_degree - cur_degree
      delta_degree = 180
      cur_degree = tar_degree

      # if delta_degree > 0:
      #   motor_yaw.speed_ratio(motor_speed_ratio)
      # else:
      #   motor_yaw.speed_ratio(-motor_speed_ratio)
      # dt = abs(delta_degree) * 0.004 + 0.05
      # time.sleep(dt)
      # motor_yaw.stop()

      motor_deal_card.speed_ratio(1)
      time.sleep(0.1)
      motor_deal_card.stop()

      time.sleep(0.5)
      i = i + 1
      if i >= 10:
        break

    # # return to the initial position
    # if -cur_degree > 0:
    #   motor_yaw.speed_ratio(motor_speed_ratio)
    # else:
    #   motor_yaw.speed_ratio(-motor_speed_ratio)
    # cur_degree = 0
    # dt = abs(delta_degree) * 0.005
    # time.sleep(dt)
    # motor_yaw.stop()
