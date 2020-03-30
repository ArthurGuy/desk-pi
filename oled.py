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
slack_status = None


def set_status(status_text, sub_text):
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top), status_text, font=main_font, fill=255)
    if sub_text is not None:
        draw.text((x, top + 25), sub_text, font=font, fill=255)
    disp.image(image)
    disp.show()


def main():
    global slack_status, slack_status_last_fetched
    try:

        init_encoder()

        last_count = -1
        while True:

            # Fetch the current status every 15 minutes and on startup
            if slack_status_last_fetched is None or (datetime.datetime.now() - slack_status_last_fetched).seconds > 900:
                slack_status_last_fetched = datetime.datetime.now()
                _slack_status = get_slack_status()
                # If the status has changed update the system
                if slack_status is not _slack_status:
                    slack_status = _slack_status
                    # Update the screen and reset the counter
                    set_status(slack_status, "Current status")
                    set_encoder_count(0)

            count = encoder_count()
            if count != last_count:
                last_count = count

                if count == 0:
                    set_status(slack_status, "Current status")
                elif count == 1:
                    set_status("Busy", None)
                elif count == 2:
                    set_status("Meeting", "30 minutes")
                elif count == 3:
                    set_status("Lunch", "30 minutes")

    except KeyboardInterrupt:
        encoder_cleanup()


if __name__ == '__main__':
    main()
