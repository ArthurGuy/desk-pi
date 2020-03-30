import time

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
import datetime
from encoder import init_encoder
from encoder import encoder_cleanup
from encoder import encoder_count
from encoder import set_encoder_count

from slack_helpers import get_slack_status
from slack_helpers import set_slack_status_busy
from slack_helpers import set_slack_status_lunch
from slack_helpers import set_slack_status_empty
from slack_helpers import set_slack_status


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()
main_font = ImageFont.truetype(HankenGroteskMedium, int(20))

slack_status_last_fetched = None
slack_status_message = None
encoder_last_changed = None
draft_status = False
slack_status_id = 0
desired_slack_status_id = 0


def set_display_status(status_text, sub_text=None):
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    if status_text is not None:
        draw.text((x, top), status_text, font=main_font, fill=255)
    if sub_text is not None:
        draw.text((x, top + 25), sub_text, font=font, fill=255)
    disp.image(image)
    disp.show()


def main():
    global slack_status_message, slack_status_last_fetched, draft_status, encoder_last_changed, slack_status_id, desired_slack_status_id
    try:

        init_encoder()

        last_count = -1
        while True:

            # Fetch the current status every 5 minutes and on startup
            if slack_status_last_fetched is None or (datetime.datetime.now() - slack_status_last_fetched).seconds > 300:
                try:
                    set_display_status(slack_status_message, "Checking slack...")
                    _slack_status_message = get_slack_status()

                    slack_status_last_fetched = datetime.datetime.now()

                    # If the status has changed update the system
                    if slack_status_message is not _slack_status_message:
                        slack_status_message = _slack_status_message
                        # Update the screen and reset the counter
                        set_display_status(slack_status_message, "Current status")
                        set_encoder_count(0)
                except RuntimeError:
                    set_display_status(slack_status_message, "Error checking slack")
                    # Wait a few seconds as the next time around it will try again
                    time.sleep(5)

            # Check the encoder to see if its been changed
            count = encoder_count()
            if count != last_count:
                last_count = count
                encoder_last_changed = datetime.datetime.now()

                # Encoder changed, update the screen
                if count == 0:
                    set_display_status(slack_status_message, "Current status")
                    desired_slack_status_id = 0
                elif count == 1:
                    set_display_status("Clear status", None)
                    desired_slack_status_id = 1
                    draft_status = True
                elif count == 2:
                    set_display_status("Busy", None)
                    desired_slack_status_id = 2
                    draft_status = True
                elif count == 3:
                    set_display_status("Lunch", None)
                    desired_slack_status_id = 3
                    draft_status = True

            # If the status has been changed and we have been waiting 5 seconds make the update
            if draft_status and (datetime.datetime.now() - encoder_last_changed).seconds > 5:
                if slack_status_id == desired_slack_status_id:
                    # No change in status
                    draft_status = False
                else:
                    slack_status_id = desired_slack_status_id
                    draft_status = False
                    try:
                        if slack_status_id == 1:
                            slack_status_message = None
                            set_display_status(slack_status_message, "Updating slack...")
                            set_slack_status(slack_status_message)
                        elif slack_status_id == 2:
                            slack_status_message = "Busy"
                            set_display_status(slack_status_message, "Updating slack...")
                            set_slack_status(slack_status_message)
                        elif slack_status_id == 3:
                            slack_status_message = "Lunch"
                            set_display_status(slack_status_message, "Updating slack...")
                            set_slack_status(slack_status_message)
                        # Reset the selector back to viewing the current status
                        set_encoder_count(0)
                    except RuntimeError:
                        print("Error setting slack status")

    except KeyboardInterrupt:
        encoder_cleanup()


if __name__ == '__main__':
    main()
