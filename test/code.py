#%% clickwheel
import touchio
from math import sqrt, atan2, pi
import time
from timetrigger import Timer
from time import monotonic, sleep



def theta_diff(a, b):
    c = a - b
    if c >= pi:
        c -= 2 * pi
    if c < - pi:
        c += 2 * pi
    return c
    
class State:
    def __init__(self, filter_level=None):
        self._now = 0
        self.last = 0
        if filter_level is not None:
            self.filternig = True
            self.alpha = 1 / 2 ** filter_level
        else:
            self.filternig = False
    
    @property
    def now(self):
        return self._now
        
    @now.setter
    def now(self, new):
        self.last = self._now
        if self.filternig:
            self._now = new * self.alpha \
                      + self._now * (1 - self.alpha)
        else:
            self._now = new
        
    @property
    def diff(self):
        return self._now - self.last

class TouchWheel5:
    def __init__(
        self,
        up,
        down,
        left,
        right,
        center,
        pad_max = None,
        pad_min = None,
        n_sec = 8,
    ):
        # touch pads
        self.pads = [touchio.TouchIn(p) for p in [
            up,
            down,
            left,
            right,
            center
        ]]
        # range of touch pads
        if pad_max is None or pad_min is None:
            start_time = monotonic()
            pad_max = [0] * 5
            pad_min = [100000] * 5
            while monotonic() - start_time < 5:
                # run the test for 5s
                # in the mean time, slide on the ring for multiple cycles.
                for i in range(5):
                    value = self.pads[i].raw_value
                    pad_max[i] = max(pad_max[i], value)
                    pad_min[i] = min(pad_min[i], value)
                    # print(ring_max, ring_min)
                    sleep(0.1)
            print('pad_max =', pad_max, ',')
            print('pad_min =', pad_min)
            # cancel running the original script
            import sys
            sys.exit()
        else: 
            self.pad_max, self.pad_min = pad_max, pad_min
        # direction constants
        self.alter_x = [0, 0, -1, 1, 0]
        self.alter_y = [1, -1, 0, 0, 0]
        self.alter_z = [0, 0, 0, 0, 1]
        
        # states
        self.filter_level = 1 # not more than 2
        self.x = State(filter_level=self.filter_level)
        self.y = State(filter_level=self.filter_level)
        self.z = State(filter_level=self.filter_level)
        
        self.r = State()  # amplitude on the plane
        self.l = State()  # amplitude in the space
        self.theta = State()  # angle on the plane
        self.phi = State()  # angle raised
    
    def get_raw(self):
        # read sensor
        pads_now = [r.raw_value for r in self.pads]
        # conver sensor to weights
        w = [
            (pads_now[i] - self.pad_min[i]) / (self.pad_max[i] - self.pad_min[i])
            for i in range(5)
        ]
        # computer vector sum
        self.x.now = sum([w[i] * self.alter_x[i] for i in range(5)])
        self.y.now = sum([w[i] * self.alter_y[i] for i in range(5)])
        self.z.now = sum([w[i] * self.alter_z[i] for i in range(5)])
        # conver to polar axis
        self.r.now = sqrt(
            self.x.now ** 2 + 
            self.y.now ** 2
        )
        self.l.now = sqrt(
            self.r.now +
            self.z.now ** 2
        )
        self.theta.now = atan2(self.y.now, self.x.now)
        self.phi.now = atan2(self.z.now, self.r.now)
        
        return self.x, self.y, self.z, self.l
        
import board
import usb_hid
from adafruit_hid.mouse import Mouse

mouse = Mouse(usb_hid.devices)

wheel = TouchWheel5(
    up=board.D7,
    down=board.D0,
    left=board.D6,
    right=board.D9,
    center=board.D8,
    # comment the following 2 lines to enter range measuring mode
    pad_max = [2160, 2345, 2160, 1896, 2602] ,
    pad_min = [904, 1239, 862, 879, 910]
)
print('startplot:', 'x', 'y')
for i in range(100000):
    sleep(0.01)
    # wheel.get_raw()
    if wheel.l.now > 0.8:
        mouse.move(
            x=int(wheel.x.now*10),
            y=-int(wheel.y.now*10),
        )
    # print(wheel.x.now, wheel.y.now)
