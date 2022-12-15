"""
This script is the entry point of all scripts.
Please check the .url files for more help

Github: https://github.com/urfdvw/Password-Keeper/

Platform: Password Keeper Xiao 2040
CircuitPython: 7.2.5

Author: River Wang
Contact: urfdvw@gmail.com
License: GPL3
Date updated: 2022/06/21 (YYYY/MM/DD)
"""
import board

#%% buzzer
from driver import Buzzer
buzzer = Buzzer(board.D10)

#%% clickwheel
from driver import Ring, Button
center = Button(board.D8)
ring = Ring(
    [
        board.D6, # left
        board.D7, # up
        board.D0, # down
        board.D9, # right
    ],
    center,
)

#%% find the range of raw_value for ring pad.
# run this code if you are testing a new PCB design
if False:
    from time import monotonic, sleep
    tic = monotonic()
    ring_max = [0] * 4
    ring_min = [100000] * 4
    while monotonic() - tic < 5:
        # run the test for 5s
        # in the mean time, slide on the ring for multiple cycles.
        for i in range(4):
            value = ring.ring[i].raw_value
            ring_max[i] = max(ring_max[i], value)
            ring_min[i] = min(ring_min[i], value)
            # print(ring_max, ring_min)
            sleep(0.1)
    print(ring_max, ',', ring_min)
    # cancel running the original script
    import sys
    sys.exit()

#%% use pre measured max and min
ring.max, ring.min = [1830, 1769, 2070, 1603], [841, 920, 1238, 880]

#%% define screen
import busio
import displayio
import adafruit_displayio_ssd1306

displayio.release_displays()
oled_reset = None
i2c = busio.I2C(board.SCL, board.SDA, frequency=int(1e6))
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C, reset=oled_reset)
WIDTH = 128
HEIGHT = 64
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=180)

#%% USB HID
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse

while True:
    try:
        # Keep trying connect to USB untill success
        # This useful for computer log in after boot.
        mouse = Mouse(usb_hid.devices)
        keyboard = Keyboard(usb_hid.devices)
        break
    except:
        print('\n' * 10 + 'USB not ready\nPlease Wait')

#%% Background apps
from background import FpsControl, FpsMonitor

frame_app = FpsControl(fps=30)
fpsMonitor_app = FpsMonitor(period=10, fps_app=frame_app)

#%% apps
from iPodApp import iPod
app_ipod = iPod()

app = app_ipod # app to start from

#%% Main logic
print('init done')
memo = {}
while True:
    # Background procedures
    fpsMonitor_app()

    # FPS control
    if not frame_app():
        continue

    # logic
    shift, message, broadcast = app.update(ring.get())
    memo.update(broadcast)
    if shift:
        app.receive(message, memo)

    # display changes
    app.display(display, buzzer)
