import math
import random
from . import globals

def add_shake(amount):
    globals.shake_intensity = min(globals.shake_intensity + amount, 25)

def update_shake():
    if globals.shake_intensity > 0:
        globals.shake_intensity *= 0.9
        angle = random.uniform(0, math.pi * 2)
        offset = globals.shake_intensity # radius
        globals.shake_offset[0] = math.cos(angle) * offset
        globals.shake_offset[1] = math.sin(angle) * offset
        if globals.shake_intensity < 0.5:
            globals.shake_intensity = 0
            globals.shake_offset = [0, 0]
    else:
        globals.shake_offset = [0, 0]
