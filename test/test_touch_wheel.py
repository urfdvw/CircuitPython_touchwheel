import board
import usb_hid
from adafruit_hid.mouse import Mouse
from touchwheel import TouchWheelPhysics, TouchWheelEvents

mouse = Mouse(usb_hid.devices)

wheel_phy = TouchWheelPhysics(
    up=board.D7,
    down=board.D0,
    left=board.D6,
    right=board.D9,
    center=board.D8,
    # comment the following 2 lines to enter range measuring mode
    pad_max = [2160, 2345, 2160, 1896, 2602] ,
    pad_min = [904, 1239, 862, 879, 910]
)

"""
# print('startplot:', 'x', 'y')
for i in range(100000):
    sleep(0.01)
    raw = wheel_phy.get()
    if wheel_phy.l.now > 0.8:
        mouse.move(
            x=int(raw.x*10),
            y=-int(raw.y*10),
        )
    # print(raw.x, raw.y)
"""

wheel_events = TouchWheelEvents(
    wheel_phy,
    N=10,
)
N = 0
for i in range(100000):
    event = wheel_events.get()
    if event:
        if event.name == 'dial':
            N += event.val
            print(N)
        else:
            print(event)