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

# battery_charge_bottom = int(inky_display.HEIGHT * (5.0 / 10.0))
battery_charge_bottom = 28
range_available_bottom = 56
# y_bottom = battery_charge_bottom + int(inky_display.HEIGHT * (4.0 / 10.0))
y_footer_top = inky_display.HEIGHT - 5

# Draw the red, white, and red strips

# Battery Charge stripe
# for y in range(0, battery_charge_bottom):
for y in range(0, battery_charge_bottom):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.BLACK)

# Available Range stripe
for y in range(battery_charge_bottom, range_available_bottom):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.BLACK)

# White strip
for y in range(range_available_bottom, y_footer_top):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.WHITE)

# Footer
for y in range(y_footer_top, inky_display.HEIGHT):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.RED)

# Calculate the positioning and draw the "Battery Charge" text
batt_charge_w, batt_charge_h = hanken_bold_font.getsize("Battery Charge:")
# batt_charge_x = int((inky_display.WIDTH - batt_charge_w) / 2)
batt_charge_x = 0 + padding
batt_charge_y = 0 + padding
draw.text((batt_charge_x, batt_charge_y), "Battery Charge:", inky_display.WHITE, font=hanken_bold_font)

# Calculate the positioning and draw the "Available Range" text
available_range_w, available_range_h = hanken_bold_font.getsize("Available Range:")
available_range_x = 0 + padding
available_range_y = 30 + padding
draw.text((available_range_x, available_range_y), "Available Range:", inky_display.WHITE, font=hanken_bold_font)

# Calculate the positioning and draw the name text

current_charge = "100%"
current_charge_w, current_charge_h = hanken_bold_font.getsize(current_charge)
# current_charge_x = int((inky_display.WIDTH - current_charge_w) / 2)
current_charge_x = int(batt_charge_w + 2)
# current_charge_y = int(battery_charge_bottom + ((y_footer_top - battery_charge_bottom - current_charge_h) / 2))
current_charge_y = 0 + padding
draw.text((current_charge_x, current_charge_y), current_charge, inky_display.WHITE, font=hanken_bold_font)

# Display the completed name badge

inky_display.set_image(img)
inky_display.show()
