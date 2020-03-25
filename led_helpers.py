#!/usr/bin/env python

import time
import datetime
import colorsys
import math
import ledshim

ledshim.set_clear_on_exit()

start_hour = 9
end_hour = 18
hours_to_track = (end_hour - start_hour)

overhang_leds = 2  # Extra LEDs on the right side that are ignored because of alignment
num_leds = ledshim.NUM_PIXELS - overhang_leds
leds_per_hour = math.floor(num_leds / hours_to_track)
leds_for_all_hours = leds_per_hour * hours_to_track
extra_leds = num_leds - leds_for_all_hours

start_extra = math.floor(extra_leds / 2)

current_time_hew = 0.7  # blue
current_time_event_overlap_hew = 0.5  # light blue
current_time_brightness = 0.9

work_day_hew = 0.2  # green/yellow
work_day_brightness = 0.8

edge_hew = 0.2
edge_brightness = 0

event_hew = 0.8  # purple
event_brightness = 1
event_brightness_past = 0.7

working_hours = True

event_pixels = []


def set_pixel(x, hew, saturation, brightness):
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hew, saturation, brightness)]
    if x >= num_leds:
        print("Trying to highlight out of range pixel", x)
        return
    ledshim.set_pixel(x, r, g, b, brightness)


def determine_highlight_pixels(hour, minute, minute_duration):
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
    # If the event is less than 30 minutes make sure its still represented
    if num_leds == 0:
        num_leds = 1

    return list(range(pixel, pixel + num_leds))


def highlight_event_time(hour, minute, minute_duration, hew, brightness, saturation=1):
    pixels = determine_highlight_pixels(hour, minute, minute_duration)

    num_leds = len(pixels)
    if num_leds == 0:
        return
    pixel = pixels[0]

    if pixel is not None:
        for x in range(num_leds):
            if (pixel + x) < num_leds:  # The event might be in the evening and out of range
                set_pixel(pixel + x, hew, saturation, brightness)
                event_pixels.append(pixel + x)


def highlight_current_time(hour, minute):
    pixels = determine_highlight_pixels(hour, minute, None)
    num_leds = len(pixels)
    pixel = pixels[0]

    if pixel is not None:
        for x in range(num_leds):
            if (pixel + x) in event_pixels:
                # We are in an event
                set_pixel(pixel + x, current_time_event_overlap_hew, 1, current_time_brightness)
            else:
                # Normal day marker
                set_pixel(pixel + x, current_time_hew, 1, current_time_brightness)


def work_day_ended():
    current_time = datetime.datetime.now()
    if current_time.hour >= end_hour:
        return True
    else:
        return False


def update_led_row(event_times):
    global working_hours
    current_time = datetime.datetime.now()

    if start_hour <= current_time.hour < end_hour:
        working_hours = True
    else:
        working_hours = False

    # Create the time outline
    for x in range(num_leds):
        if x < start_extra:
            set_pixel(x, edge_hew, 1, edge_brightness)
        elif x < (start_extra + leds_for_all_hours):
            set_pixel(x, work_day_hew, 1, work_day_brightness)
        else:
            set_pixel(x, edge_hew, 1, edge_brightness)

    # Colour in events
    # TODO: If event is outside of working day don't include it
    for event in event_times:
        event_hour = int(event.get('start').split(':')[0])
        event_minute = int(event.get('start').split(':')[1])
        minute_duration = event.get('duration')
        if event_hour < current_time.hour or (event_hour == current_time.hour and event_minute < current_time.minute):
            highlight_event_time(event_hour, event_minute, minute_duration, event_hew, event_brightness_past)
        else:
            highlight_event_time(event_hour, event_minute, minute_duration, event_hew, event_brightness)

    # Colour in the current time marker
    if working_hours:
        highlight_current_time(current_time.hour, current_time.minute)

    ledshim.show()



if __name__ == '__main__':
    while True:
        update_led_row()
        time.sleep(1)
