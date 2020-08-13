from PIL import Image, ImageDraw, ImageFont
from inky import InkyPHAT, InkyWHAT
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from font_intuitive import Intuitive

colour = "red"
inky_display = InkyPHAT(colour)
scale_size = 1
padding = 0
inky_display.set_border(inky_display.WHITE)

# Create a new canvas to draw on

img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# Load the fonts

intuitive_font = ImageFont.truetype(Intuitive, int(20 * scale_size))
hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(21 * scale_size))
hanken_medium_font = ImageFont.truetype(HankenGroteskMedium, int(20 * scale_size))

# Top and bottom y-coordinates for the white strip

y_top = int(inky_display.HEIGHT * (5.0 / 10.0))
y_bottom = y_top + int(inky_display.HEIGHT * (4.0 / 10.0))

# Draw the red, white, and red strips

# for y in range(0, y_top):
for y in range(0, 20):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.RED)

for y in range(y_top, y_bottom):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.WHITE)

for y in range(y_bottom, inky_display.HEIGHT):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.RED)

# Calculate the positioning and draw the "Hello" text

batt_charge_w, batt_charge_h = hanken_bold_font.getsize("Battery Charge:")
# batt_charge_x = int((inky_display.WIDTH - batt_charge_w) / 2)
batt_charge_x = 0 + padding
batt_charge_y = 0 + padding
draw.text((batt_charge_x, batt_charge_y), "Battery Charge:", inky_display.WHITE, font=hanken_bold_font)

# Calculate the positioning and draw the name text

current_charge = "100%"
current_charge_w, current_charge_h = hanken_bold_font.getsize(current_charge)
# current_charge_x = int((inky_display.WIDTH - current_charge_w) / 2)
current_charge_x = int(batt_charge_w + 2)
# current_charge_y = int(y_top + ((y_bottom - y_top - current_charge_h) / 2))
current_charge_y = 0 + padding
draw.text((current_charge_x, current_charge_y), current_charge, inky_display.WHITE, font=hanken_bold_font)

# Display the completed name badge

inky_display.set_image(img)
inky_display.show()
