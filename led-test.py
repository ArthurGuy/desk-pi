#!/usr/bin/env python

import time
import datetime
import colorsys
import math
import ledshim

FALLOFF = 1.9
SCAN_SPEED = 4

ledshim.set_clear_on_exit()

ledshim.NUM_PIXELS // 28

start_time = time.time()

start_hour = 8
end_hour = 18

target_time = 14

hours_to_track = (end_hour - start_hour) + 1

leds_per_hour = math.floor(ledshim.NUM_PIXELS / hours_to_track)
leds_for_all_hours = leds_per_hour * hours_to_track
extra_leds = ledshim.NUM_PIXELS - leds_for_all_hours

start_extra = math.floor(extra_leds / 2)
end_extra = extra_leds - start_extra


time = datetime.datetime.now()


def set_pixel(x, h, s, v):
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
    ledshim.set_pixel(x, r, g, b, v)


while True:
    for x in range(ledshim.NUM_PIXELS):
        if (x < start_extra):
            set_pixel(x, 0.2, 1, 0.4)
        elif (x < start_extra + leds_for_all_hours):
            set_pixel(x, 0.9, 1, 0.7)
        else:
            set_pixel(x, 0.2, 1, 0.4)

        set_pixel(start_extra + (leds_per_hour * (time.hour - start_hour)), 0.5, 1, 0.9)

    ledshim.show()

    time.sleep(0.1)


while True:
    for x in range(ledshim.NUM_PIXELS):
        if x == target_time:
            val = 0.8
        elif x > target_time:
            val = 0.4
        else:
            val = 0.5

        sat = 1.0
        hue = 0.5

        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, sat, val)]
        ledshim.set_pixel(x, r, g, b, val)

    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(0.2, 1.0, 1)]
    ledshim.set_pixel(20, r, g, b, 0.8)

    ledshim.show()

    time.sleep(0.1)





#
# while True:
#     delta = (time.time() - start_time)
#
#     # Offset is a sine wave derived from the time delta
#     # we use this to animate both the hue and larson scan
#     # so they are kept in sync with each other
#     offset = (math.sin(delta * SCAN_SPEED) + 1) / 2
#
#     # Use offset to pick the right colour from the hue wheel
#     hue = int(round(offset * 360))
#
#     # Maximum number basex on NUM_PIXELS
#     max_val = ledshim.NUM_PIXELS - 1
#
#     # Now we generate a value from 0 to max_val
#     offset = int(round(offset * max_val))
#
#     for x in range(ledshim.NUM_PIXELS):
#         sat = 1.0
#
#         val = max_val - (abs(offset - x) * FALLOFF)
#         val /= float(max_val)   # Convert to 0.0 to 1.0
#         val = max(val, 0.0)     # Ditch negative values
#
#         xhue = hue              # Grab hue for this pixel
#         xhue += (1 - val) * 10  # Use the val offset to give a slight colour trail variation
#         xhue %= 360             # Clamp to 0-359
#         xhue /= 360.0           # Convert to 0.0 to 1.0
#
#         r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(xhue, sat, val)]
#
#         ledshim.set_pixel(x, r, g, b, val / 4)
#
#     ledshim.show()
#
#     time.sleep(0.001)