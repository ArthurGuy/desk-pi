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
end_hour = 19
hours_to_track = (end_hour - start_hour)

leds_per_hour = math.floor(ledshim.NUM_PIXELS / hours_to_track)
leds_for_all_hours = leds_per_hour * hours_to_track
extra_leds = ledshim.NUM_PIXELS - leds_for_all_hours

start_extra = math.floor(extra_leds / 2)
end_extra = extra_leds - start_extra

current_time_hew = 0.5
current_time_brightness = 1
work_day_hew = 0.9
work_day_brightness = 0.6
edge_hew = 0.2
edge_brightness = 0
event_hew = 0
event_brightness = 1

event_times = [{'start': '15:00', 'minute_duration': '60'}, {'start': '10:00', 'minute_duration': '100'}]


def set_pixel(x, h, s, v):
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
    ledshim.set_pixel(x, r, g, b, v)


def highlight_time(hour, minute, minute_duration, hew, brightness, saturation=1):
    pixel = None
    num_leds = 1
    if leds_per_hour == 1:
        pixel = start_extra + (leds_per_hour * (hour - start_hour))
        if minute_duration is not None:
            num_leds = math.floor(minute_duration / 60)
    elif leds_per_hour == 2:
        if minute >= 30:
            pixel = start_extra + (leds_per_hour * (hour - start_hour)) + 1
        else:
            pixel = start_extra + (leds_per_hour * (hour - start_hour))
        if minute_duration is not None:
            num_leds = math.floor(minute_duration / 30)
    elif leds_per_hour == 3:
        if minute >= 40:
            pixel = start_extra + (leds_per_hour * (hour - start_hour)) + 2
        elif minute >= 20:
            pixel = start_extra + (leds_per_hour * (hour - start_hour)) + 1
        else:
            pixel = start_extra + (leds_per_hour * (hour - start_hour))
        if minute_duration is not None:
            num_leds = math.floor(minute_duration / 20)

    if pixel is not None:
        for x in range(num_leds):
            set_pixel(pixel + x, hew, saturation, brightness)


def update_led_row():
    current_time = datetime.datetime.now()
    current_time = datetime.datetime.fromisoformat('2020-03-21 14:25')

    if current_time.hour >= start_hour and current_time.hour < end_hour:
        working_hours = True
    else:
        working_hours = False

    # Create the time outline
    for x in range(ledshim.NUM_PIXELS):
        if x < start_extra:
            set_pixel(x, edge_hew, 1, edge_brightness)
        elif x < (start_extra + leds_for_all_hours):
            set_pixel(x, work_day_hew, 1, work_day_brightness)
        else:
            set_pixel(x, edge_hew, 1, edge_brightness)

    # Colour in events
    for event in event_times:
        event_hour = int(event.get('start').split(':')[0])
        event_minute = int(event.get('start').split(':')[1])
        minute_duration = int(event.get('minute_duration'))
        if event_hour < current_time.hour or event_minute < current_time.minute:
            highlight_time(event_hour, event_minute, minute_duration, event_hew, event_brightness * 0.5)
        else:
            highlight_time(event_hour, event_minute, minute_duration, event_hew, event_brightness)

    # Colour in the current time marker
    if working_hours:
        highlight_time(current_time.hour, current_time.minute, None, current_time_hew, current_time_brightness, 0)

    ledshim.show()





if __name__ == '__main__':
    while True:
        update_led_row()
        time.sleep(1)




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