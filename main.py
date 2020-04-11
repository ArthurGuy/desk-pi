import os
import math
import time
import ledshim
import datetime
import colorsys
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from calendar_helpers import get_all_calendar_items
from led_helpers import update_led_row
from led_helpers import work_day_ended
from led_helpers import set_indicator_led
from slack_screen import check_update_slack
from slack_screen import setup_slack_screen
from slack_screen import update_slack_screen_error
from encoder import set_led

PATH = os.path.dirname(__file__)

ledshim.set_clear_on_exit()

# Initialise the eink display
# inky_display = InkyPHAT('black')
inky_display = InkyPHAT('red')
# inky_display.h_flip = True
# inky_display.v_flip = True


# Fonts
# bold_font = ImageFont.truetype(HankenGroteskBold, int(15))
# label_font = ImageFont.truetype('Screenstar-Small-Regular.otf', int(13))  # displays correctly at 12

# label_font = ImageFont.truetype(HankenGroteskMedium, int(13))
bold_font = ImageFont.truetype('SubVario-Condensed-Medium.otf', int(17))

label_font = inky_display.ImageFont(inky_display.fonts.AmaticSCBold, 13)


# Canvas
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)


# Led day display, initialise variables and calculate details
start_hour = 9
end_hour = 18
hours_to_track = (end_hour - start_hour)

leds_per_hour = math.floor(ledshim.NUM_PIXELS / hours_to_track)
leds_for_all_hours = leds_per_hour * hours_to_track
extra_leds = ledshim.NUM_PIXELS - leds_for_all_hours

start_extra = math.floor(extra_leds / 2)


# Colour settings for the led day display
current_time_hew = 0.5  # light blue
current_time_brightness = 1

work_day_hew = 0.2  # green/yellow
work_day_brightness = 0.6

edge_hew = 0.2
edge_brightness = 0

event_hew = 0.8  # purple
event_brightness = 1
event_brightness_past = 0.7


def create_mask(source, mask=(inky_display.WHITE, inky_display.BLACK, inky_display.RED)):
    """Create a transparency mask.
    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.
    :param mask: Optional list of Inky pHAT colours to allow.
    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image


def draw_text(position, text, font=None, colour=inky_display.BLACK, rotation=0):
    # x, y = position
    if font is None:
        font = label_font
    w, h = font.getsize(text)
    mask = Image.new('1', (w, h))
    draw = ImageDraw.Draw(mask)
    draw.text((0, 0), text, 1, font)
    mask = mask.rotate(rotation, expand=True)
    img.paste(colour, position, mask)


def generate_calendar_text(event):
    """
    Generate a text string based on a calendar event
    :param event:
    :return string:
    """
    start_time = datetime.datetime.fromisoformat(event.get('start_time'))
    if event.get('duration') == 0:
        text = 'All day: '
    else:
        text = start_time.strftime("%H:%M ")
    return text + event.get('summary')


led_event_list = []


def clean_display():
    # inky_display.set_border(inky_display.WHITE)
    for x in range(inky_display.WIDTH):
        for y in range(inky_display.HEIGHT):
            img.putpixel((x, y), inky_display.WHITE)
    inky_display.set_image(img)
    inky_display.show()


def update_calendar():
    today = datetime.datetime.now()
    global led_event_list

    _work_day_ended = work_day_ended()

    # Fetch todays events or tomorrows events
    try:
        events = get_all_calendar_items(tomorrow_only=_work_day_ended, today_only=not _work_day_ended)
        show_tomorrows_events = _work_day_ended
        if not _work_day_ended and len(events) is 0:
            # Nothing left for today, show tomorrows stuff
            show_tomorrows_events = True
            events = get_all_calendar_items(tomorrow_only=True)
    except:
        # Error fetching calendars, probably network error
        return False

    # Write over the text with a white box
    draw.rectangle((0, 0, inky_display.width - 1, 83), fill=inky_display.WHITE)
    # for y in range(0, 83):
    #     for x in range(0, inky_display.width):
    #         img.putpixel((x, y), inky_display.WHITE)


    led_event_list = []

    if not _work_day_ended and not show_tomorrows_events:
        # If we are still in the working day and we haven't switch to tomorrow capture todays events for the led display
        for event in events:
            start_time = datetime.datetime.fromisoformat(event.get('start_time'))
            start_hour = str(start_time.time().hour) + ':' + str(start_time.time().minute)
            led_event_list.append({'start': start_hour, 'duration': event.get('duration')})

    y = 0
    y += 5

    # If we have some events for tomorrow display a heading
    if show_tomorrows_events and len(events):
        draw_text((2, y - 3), "Tomorrow")
        y += 20

    # Display the list of events
    for event in events:
        draw_text((5, y), generate_calendar_text(event))
        y += 18

    bottom_info_row_y_start = 86

    # Display the date in the bottom right on a black background
    for y in range(79, inky_display.height):
        for x in range(137 - (y - 79), inky_display.width):
            img.putpixel((x, y), inky_display.BLACK)
    date_text = today.strftime("%d/%m/%Y")
    draw_text((138, bottom_info_row_y_start + 3), date_text, colour=inky_display.WHITE)

    # Bottom left corner markings
    for y in range(bottom_info_row_y_start, inky_display.height):
        for x in range(0, (y - bottom_info_row_y_start)):
            img.putpixel((x, y), inky_display.BLACK)

    # Display the day in the bottom space
    day_text = today.strftime("%A")
    draw_text((22, bottom_info_row_y_start), day_text, colour=inky_display.RED, font=bold_font)

    # bottom dividing line
    # for y in range(84, 86):
    #     for x in range(0, inky_display.width):
    #         img.putpixel((x, y), inky_display.BLACK)


    inky_display.set_border(inky_display.BLACK)
    inky_display.set_image(img)
    inky_display.show()

    return True


screen_last_updated = None
screen_day_last_updated = None
leds_last_updated = None
error_fetching_calendar_count = 0

if __name__ == '__main__':
    setup_slack_screen()

    while True:
        update_eink_screen = False

        if leds_last_updated is None or (datetime.datetime.now() - leds_last_updated).seconds > 10:
            # Every 10 seconds update the LED's
            update_led_row(led_event_list)
            leds_last_updated = datetime.datetime.now()

        if screen_day_last_updated is None or datetime.datetime.now().day != screen_day_last_updated:
            clean_display()
            update_eink_screen = True
            # Update each morning to correct today/tomorrow and the date

        if screen_last_updated is None or (datetime.datetime.now() - screen_last_updated).seconds > 1800:
            update_eink_screen = True
            # Update every 30 minutes in case of new events

        if update_eink_screen:
            update_success = update_calendar()
            if update_success:
                screen_last_updated = datetime.datetime.now()
                screen_day_last_updated = datetime.datetime.now().day
                error_fetching_calendar_count = 0
            else:
                # Error fetching calendars, probably network error so wait and try again
                error_fetching_calendar_count += 1
                time.sleep(5)

            if error_fetching_calendar_count > 5:
                update_slack_screen_error("Error fetching calendar")
                time.sleep(5)

        check_update_slack()
