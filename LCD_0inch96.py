# Reference: https://www.waveshare.net/w/upload/e/e2/ST7735S_V1.1_20111121.pdf
from machine import Pin, SPI
import framebuf
import time

# SLPIN (10h): Sleep In, need to wait 0.12s
# SLPOUT (11h): Sleep Out, need to wait 0.12s
# DISPOFF (28h): Display Off
# DISPON (29h): Display On

k_BLACK = 0x0000
k_WHITE = 0xFFFF
k_RED = 0x00F8  # D0~D15: [11111 000000 00000]. D8~D15+D0~D7: [0x00F8]
k_GREEN = 0xE007  # D0~D15: [00000 111111 00000]. D8~D15+D0~D7: [0xE007]
k_BLUE = 0x1F00  # D0~D15: [00000 000000 11111]. D8~D15+D0~D7: [0x1F00]

k_WIDTH = 160
k_HEIGHT = 80
k_X_START = 1
k_X_END = 160
k_Y_START = 26
k_Y_END = 105


# The original width and height of this controller is 132 * 162
class LCD_0inch96(framebuf.FrameBuffer):
    def __init__(self):
        self.buffer = bytearray(k_WIDTH * k_HEIGHT * 2)
        super().__init__(self.buffer, k_WIDTH, k_HEIGHT, framebuf.RGB565)

        self.spi = SPI(id=1, baudrate=10_000_000, sck=Pin(10), mosi=Pin(11), miso=None)
        self.dc = Pin(8, mode=Pin.OUT, value=0)  # physical pin 11
        self.cs = Pin(9, mode=Pin.OUT, value=1)  # physical pin 12
        self.rst = Pin(12, mode=Pin.OUT, value=1)  # physical pin 16
        self.bl = Pin(25, mode=Pin.OUT, value=1)  # physical pin 30

        self._init()

    def _reset(self):
        self.rst(0)
        time.sleep(0.2)

        self.rst(1)
        self.bl(1)
        # Software Reset, need to wait 0.12s
        self._write_cmd(0x01)
        time.sleep(0.2)

    def _init(self):
        self._reset()

        # Sleep Out, need to wait 0.12s
        self._write_cmd(0x11)
        time.sleep(0.12)

        # Display On
        self._write_cmd(0x29)

        # Display Inversion On
        self._write_cmd(0x21)

        # Memory Data Access Control
        self._write_cmd(0x36)
        # 10101000
        self._write_data(0xA8)

        # Column Address Set
        self._write_cmd(0x2A)
        self._write_data(0)
        self._write_data(k_X_START)
        self._write_data(0)
        self._write_data(k_X_END)

        # Row Address Set
        self._write_cmd(0x2B)
        self._write_data(0)
        self._write_data(k_Y_START)
        self._write_data(0)
        self._write_data(k_Y_END)

        # Interface Pixel Format
        self._write_cmd(0x3A)
        # 16-bit/pixel
        self._write_data(0x05)

        # Memory Write
        self._write_cmd(0x2C)

    def _write_cmd(self, cmd):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def _write_data(self, buf):
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def refresh_buffer(self):
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)


# if __name__=='__main__':
#     lcd = LCD_0inch96()

#     lcd.fill(k_BLACK)
#     lcd.text("Hello pico!", 35, 15, k_GREEN)
#     lcd.text("This is:", 50, 35, k_GREEN)
#     lcd.text("Pico-LCD-0.96", 30, 55, k_GREEN)

#     lcd.hline(10, 10, 140, k_RED)
#     lcd.hline(10, 70, 140, k_RED)
#     lcd.vline(10, 10, 60, k_RED)
#     lcd.vline(150, 10, 60, k_RED)

#     lcd.hline(0, 0, 160, k_BLUE)
#     lcd.hline(0, 79, 160, k_BLUE)
#     lcd.vline(0, 0, 80, k_BLUE)
#     lcd.vline(159, 0, 80, k_BLUE)

#     lcd.refresh_buffer()
