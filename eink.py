import os
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium


PATH = os.path.dirname(__file__)

inky_display = InkyPHAT('black')

# inky_display.h_flip = True
# inky_display.v_flip = True


# Fonts
hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(15))
hanken_label_font = ImageFont.truetype(HankenGroteskMedium, int(13))


# Canvas
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)



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
    x, y = position
    if font is None:
        font = hanken_label_font
    w, h = font.getsize(text)
    mask = Image.new('1', (w, h))
    draw = ImageDraw.Draw(mask)
    draw.text((0, 0), text, 1, font)
    mask = mask.rotate(rotation, expand=True)
    img.paste(colour, position, mask)


inky_display.set_border(inky_display.BLACK)


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

y = 0

# draw_text((5, y), "Today 14:00", colour=inky_display.RED, font=hanken_bold_font)
# draw_text((5, y + 14), "Project A review meeting", colour=inky_display.RED, font=hanken_bold_font)

y = 0
draw_text((0, y), "All day Mother's Day")

y += 18
draw_text((0, y), "13:00 Interview 2")

y += 18
draw_text((0, y), "14:00 Project A review meeting", font=hanken_bold_font)
y += 3

y += 18
draw_text((0, y), "16:00 1 to 1 - John & Smith")


# Dispay the date in the bottom right on a black background
date_text = "22/03/2020"
for y in range(84, inky_display.height):
    for x in range(135 - (y - 84), inky_display.width):
        img.putpixel((x, y), inky_display.BLACK)
draw_text((135, 87), date_text, colour=inky_display.WHITE)


inky_display.set_image(img)
inky_display.show()
