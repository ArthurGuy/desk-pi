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
import datetime

PATH = os.path.dirname(__file__)

ledshim.set_clear_on_exit()

# Initialise the eink display
inky_display = InkyPHAT('black')
# inky_display.h_flip = True
# inky_display.v_flip = True


# Fonts
hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(15))
hanken_label_font = ImageFont.truetype(HankenGroteskMedium, int(13))


# Canvas
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)


# Led day display, initialise variables and calculate details
start_hour = 8
end_hour = 19
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
        font = hanken_label_font
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



# for y in range(0, 10):
#     for x in range(0, inky_display.width):
#         img.putpixel((x, y), inky_display.RED)

# for y in range(11, 20):
#     for x in range(0, inky_display.width):
#         img.putpixel((x, y), inky_display.WHITE)
#
# for y in range(21, 30):
#     for x in range(0, inky_display.width):
#         img.putpixel((x, y), inky_display.BLACK)

# tree = Image.open(os.path.join(PATH, "tree.png"))
# tree_mask = create_mask(tree, mask=(inky_display.WHITE, inky_display.BLACK))
# img.paste(tree, (60, 60), tree_mask)

# hello_w, hello_h = hanken_bold_font.getsize("Hello")
# hello_x = 0
# hello_y = 30
# draw.text((hello_x, hello_y), "Hello", inky_display.BLACK, font=hanken_bold_font)
#
# busy_w, busy_h = hanken_label_font.getsize("Busy")
# busy_x = 0
# busy_y = 0
# draw.text((busy_x, busy_y), "Busy", inky_display.BLACK, font=hanken_label_font)

# draw_text((20, 20), "Hello", colour=inky_display.RED, rotation=45)
# draw_text((80, 20), "World", rotation=90)



# draw_text((5, y), "Today 14:00", colour=inky_display.RED, font=hanken_bold_font)
# draw_text((5, y + 14), "Project A review meeting", colour=inky_display.RED, font=hanken_bold_font)

# y = 0
# draw_text((0, y), "All day Mother's Day")

# y += 18
# draw_text((0, y), "13:00 Interview 2")
#
# y += 18
# draw_text((0, y), "14:00 Project A review meeting", font=hanken_bold_font)
# y += 3
#
# y += 18
# draw_text((0, y), "16:00 1 to 1 - John & Smith")

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
    tomorrow = today + datetime.timedelta(days=1)
    global led_event_list, work_day_ended

    # Fetch todays events or tomorrows events
    try:
        events = get_all_calendar_items(tomorrow_only=work_day_ended, today_only=not work_day_ended)
        show_tomorrows_events = work_day_ended
        if not work_day_ended and len(events) is 0:
            # Nothing left for today, show tomorrows stuff
            show_tomorrows_events = True
            events = get_all_calendar_items(tomorrow_only=True)
    except RuntimeError:
        return False

    clean_display()

    led_event_list = []

    if not work_day_ended and not show_tomorrows_events:
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

    # Display the date in the bottom right on a black background
    date_text = today.strftime("%d/%m/%Y")
    for y in range(86, inky_display.height):
        for x in range(138 - (y - 86), inky_display.width):
            img.putpixel((x, y), inky_display.BLACK)
    draw_text((138, 88), date_text, colour=inky_display.WHITE)

    # Experiments with fancy sci-fi bits!
    for y in range(86, inky_display.height):
        for x in range(0, 20 + (y - 86)):
            img.putpixel((x, y), inky_display.BLACK)

    inky_display.set_border(inky_display.BLACK)
    inky_display.set_image(img)
    inky_display.show()

    return True


screen_last_updated = None
screen_day_last_updated = None


if __name__ == '__main__':
    while True:
        update_screen = False
        update_led_row(led_event_list)

        if screen_day_last_updated is None or datetime.datetime.now().day != screen_day_last_updated:
            update_screen = True
            # Update each morning to correct today/tomorrow

        if screen_last_updated is None or (datetime.datetime.now() - screen_last_updated).seconds > 3600:
            update_screen = True
            # Update every hour in case of new events

        if update_screen:
            update_success = update_calendar()
            if update_success:
                screen_last_updated = datetime.datetime.now()
                screen_day_last_updated = datetime.datetime.now().day

        time.sleep(10)
