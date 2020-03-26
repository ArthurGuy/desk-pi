import time

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium

from encoder import init_encoder
from encoder import encoder_cleanup
from encoder import encoder_count


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


def main():
    try:

        init_encoder()
        while True:
            count = encoder_count()
            # Draw a black filled box to clear the image.
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            if count == 0:
                draw.text((x, top), "Out for lunch", font=main_font, fill=255)
                draw.text((x, top + 25), "60 minutes", font=font, fill=255)
            elif count == 1:
                draw.text((x, top), "Busy", font=main_font, fill=255)
                draw.text((x, top + 25), "60 minutes", font=font, fill=255)
            elif count == 2:
                draw.text((x, top), "Meeting", font=main_font, fill=255)
                draw.text((x, top + 25), "30 minutes", font=font, fill=255)
            elif count == 3:
                draw.text((x, top), "Working", font=main_font, fill=255)

            # Display image.
            disp.image(image)
            disp.show()
            time.sleep(0.1)

    except KeyboardInterrupt:  # Ctrl-C to terminate the program
        encoder_cleanup()


if __name__ == '__main__':
    main()
