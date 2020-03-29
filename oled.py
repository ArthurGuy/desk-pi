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


def main():
    global slack_status, slack_status_last_fetched
    try:

        init_encoder()

        last_count = -1
        while True:

            if slack_status_last_fetched is None or (datetime.datetime.now() - slack_status_last_fetched).seconds > 3600:
                slack_status_last_fetched = datetime.datetime.now()
                slack_status = get_slack_status()

            count = encoder_count()
            if count != last_count:
                last_count = count
                # Draw a black filled box to clear the image.
                draw.rectangle((0, 0, width, height), outline=0, fill=0)

                if count == 0:
                    draw.text((x, top), slack_status, font=main_font, fill=255)
                    draw.text((x, top + 25), "Current status", font=font, fill=255)
                elif count == 1:
                    draw.text((x, top), "Busy", font=main_font, fill=255)
                    draw.text((x, top + 25), "60 minutes", font=font, fill=255)
                elif count == 2:
                    draw.text((x, top), "Meeting", font=main_font, fill=255)
                    draw.text((x, top + 25), "30 minutes", font=font, fill=255)
                elif count == 3:
                    draw.text((x, top), "Lunch", font=main_font, fill=255)

                disp.image(image)
                disp.show()

    except KeyboardInterrupt:
        encoder_cleanup()


if __name__ == '__main__':
    main()
