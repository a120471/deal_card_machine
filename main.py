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

    motor_yaw = Motor(5, 4, 1, 0, reverse_direction=True)
    pid_yaw = PID(motor_yaw, kp=0.03, max_u=0.9)
    motor_deal_card = Motor(3, 2)
    elapsed_time = 0
    for tar_deg in degrees:
        elapsed_time += pid_yaw.set_position(tar_deg, threshold=0.2)

        motor_deal_card.speed_ratio(0.4)
        time.sleep(0.4)
        motor_deal_card.speed_ratio(-0.4)
        time.sleep(0.3)
        motor_deal_card.stop()

        # print(
        #     f"{motor_yaw.read_pos() * 360 / pid_yaw.pos_ticks_per_rev:.3f} -> {tar_deg}"
        # )

    print("Total time:", elapsed_time)
    # return to the initial position
    pid_yaw.set_position(0, threshold=0.1)
