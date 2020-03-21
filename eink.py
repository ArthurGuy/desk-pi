import os
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium


PATH = os.path.dirname(__file__)

inky_display = InkyPHAT('black')


# Fonts
hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(35))
hanken_label_font = ImageFont.truetype(HankenGroteskBold, int(15))


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



inky_display.set_border(inky_display.BLACK)


# for y in range(0, 10):
#     for x in range(0, inky_display.width):
#         img.putpixel((x, y), inky_display.RED)

for y in range(11, 20):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.WHITE)

for y in range(21, 30):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.BLACK)

# tree = Image.open(os.path.join(PATH, "tree.png"))
# tree_mask = create_mask(tree, mask=(inky_display.WHITE, inky_display.BLACK))
# img.paste(tree, (60, 60), tree_mask)

hello_w, hello_h = hanken_bold_font.getsize("Hello")
hello_x = 0
hello_y = 30
draw.text((hello_x, hello_y), "Hello", inky_display.BLACK, font=hanken_bold_font)

busy_w, busy_h = hanken_label_font.getsize("Busy")
busy_x = 0
busy_y = 0
draw.text((busy_x, busy_y), "Busy", inky_display.BLACK, font=hanken_label_font)


inky_display.set_image(img)
inky_display.show()
