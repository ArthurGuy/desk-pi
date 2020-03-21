from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium

inky_display = InkyPHAT('red')


# Fonts
hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(35))


# Canvas
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

inky_display.set_border(inky_display.RED)


for y in range(0, 10):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.RED)

for y in range(11, 20):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.WHITE)

for y in range(21, 30):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.BLACK)


hello_w, hello_h = hanken_bold_font.getsize("Hello")
hello_x = 0
hello_y = 30
draw.text((hello_x, hello_y), "Hello", inky_display.BLACK, font=hanken_bold_font)



inky_display.show()
