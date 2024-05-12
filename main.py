from machine import Pin
import rp2
import time

from doudizhu_shuffling import dou_di_zhu_shuffle
from motor_control import Motor, PID

k_ROTATION_RANGE = 180  # degrees (from -90 to 90)


def indices_to_degrees(indices):
    max_i = max(indices)
    degrees = [i * k_ROTATION_RANGE / max_i - k_ROTATION_RANGE / 2 for i in indices]
    return degrees


if __name__ == "__main__":
    lcd_bl = Pin(25, mode=Pin.OUT, value=0)
    while True:
      if rp2.bootsel_button() == 1:
        break
      time.sleep(0.1)

    indices = dou_di_zhu_shuffle()
    degrees = indices_to_degrees(indices)
    # print(indices)
    # print(degrees)

    motor_yaw = Motor(5, 4, 1, 0, True)
    pid_yaw = PID(motor_yaw, kp=0.03, max_u=0.9)
    # motor_deal_card = Motor(3, 2)
    # for tar_deg in degrees:
    for tar_deg in [-30, -90, 90, 30]:
        pid_yaw.set_position(tar_deg, threshold=0.1)

        # motor_deal_card.speed_ratio(0.1)
        # time.sleep(0.01)
        # motor_deal_card.stop()

        time.sleep(1)
        print(
            "cur_deg_later: ",
            motor_yaw.read_pos() * 360 / pid_yaw.pos_ticks_per_rev,
            "tar_deg: ",
            tar_deg,
        )
        print()
        # break

    # # return to the initial position
    # pid_yaw.set_position(0, threshold=1)
