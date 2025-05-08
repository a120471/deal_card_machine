from machine import Pin
import rp2
import time

from card_shuffling import dou_di_zhu_shuffle, n_player_shuffle
from motor_control import Motor, PID
from LCD_0inch96 import display_text

k_DOUBLE_CLICK_TIME = 200  # double click time window in ms
k_ROTATION_RANGE = 180  # degrees (from -90 to 90)


def check_button_click():
    def _wait_button_release():
        while rp2.bootsel_button() == 1:
            time.sleep(0.01)

    while True:
        if rp2.bootsel_button() == 1:  # 第一次按下
            _wait_button_release()

            # 等待可能的第二次点击
            timeout = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), timeout) < k_DOUBLE_CLICK_TIME:
                if rp2.bootsel_button() == 1:  # 如果在时间窗口内又按下，判定为双击
                    _wait_button_release()
                    return "double"
                time.sleep(0.01)

            # 超时未收到第二次点击
            return "single"

        time.sleep(0.01)


def indices_to_degrees(indices):
    max_i = max(indices)
    degrees = [-i * k_ROTATION_RANGE / max_i - k_ROTATION_RANGE / 2 for i in indices]
    return degrees


if __name__ == "__main__":
    display_text("1: Dou Di Zhu\n2: Xuan Hong Qiang", y=20, line_spacing=20)
    click_type = check_button_click()
    # print(click_type)
    lcd_bl = Pin(25, mode=Pin.OUT, value=0)  # turn off lcd backlight
    if click_type == "single":
        indices = dou_di_zhu_shuffle()
    elif click_type == "double":
        indices = n_player_shuffle(player_num=4)
    else:
        indices = n_player_shuffle(player_num=4)

    degrees = indices_to_degrees(indices)
    # print(indices)
    # print(degrees)

    motor_yaw = Motor(5, 4, 1, 0)
    pid_yaw = PID(motor_yaw, kp=0.03, max_u=0.9)
    motor_deal_card = Motor(3, 2)
    start_time = time.time()
    rotation_angle = 0
    for tar_deg in degrees:
        rotation_angle += 100
        pid_yaw.set_position(rotation_angle, threshold=0.3)
        # pid_yaw.set_position(tar_deg, threshold=0.3)

        motor_deal_card.speed_ratio(0.4)
        time.sleep(0.4)
        motor_deal_card.speed_ratio(-0.4)
        time.sleep(0.3)
        motor_deal_card.stop()

        # print(
        #     f"{motor_yaw.read_pos() * 360 / pid_yaw.pos_ticks_per_rev:.3f} -> {tar_deg}"
        # )

    print("Total time:", time.time() - start_time)
    # return to the initial position
    pid_yaw.set_position(0, threshold=0.1)
