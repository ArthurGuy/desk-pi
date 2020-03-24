#!/usr/bin/env python

import time
import datetime
import colorsys
import math
import ledshim

ledshim.set_clear_on_exit()

start_hour = 8
end_hour = 19
hours_to_track = (end_hour - start_hour)

leds_per_hour = math.floor(ledshim.NUM_PIXELS / hours_to_track)
leds_for_all_hours = leds_per_hour * hours_to_track
extra_leds = ledshim.NUM_PIXELS - leds_for_all_hours

start_extra = math.floor(extra_leds / 2)

current_time_hew = 0.5  # light blue
current_time_brightness = 1

work_day_hew = 0.2  # green/yellow
work_day_brightness = 0.6

edge_hew = 0.2
edge_brightness = 0

event_hew = 0.8  # purple
event_brightness = 1
event_brightness_past = 0.7

working_hours = True
work_day_ended = False

# event_times = [{'start': '15:00', 'duration': 60}, {'start': '12:00', 'duration': 100}]

event_pixels = []


def set_pixel(x, hew, saturation, brightness):
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hew, saturation, brightness)]
    if x >= ledshim.NUM_PIXELS:
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
            if (pixel + x) < ledshim.NUM_PIXELS:  # The event might be in the evening and out of range
                set_pixel(pixel + x, hew, saturation, brightness)
                event_pixels.append(pixel + x)


def highlight_current_time(hour, minute):
    pixels = determine_highlight_pixels(hour, minute, None)
    num_leds = len(pixels)
    pixel = pixels[0]

    if pixel is not None:
        for x in range(num_leds):
            if (pixel + x) in event_pixels:
                set_pixel(pixel + x, current_time_hew, 1, current_time_brightness)
            else:
                set_pixel(pixel + x, current_time_hew, 0, current_time_brightness)


def update_led_row(event_times):
    global working_hours, work_day_ended
    current_time = datetime.datetime.now()
    # current_time = datetime.datetime.fromisoformat('2020-03-21 14:25')

    if start_hour <= current_time.hour < end_hour:
        working_hours = True
    else:
        working_hours = False

    if current_time.hour >= end_hour:
        work_day_ended = True
    else:
        work_day_ended = False

    # Create the time outline
    for x in range(ledshim.NUM_PIXELS):
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
