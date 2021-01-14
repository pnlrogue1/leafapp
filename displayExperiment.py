from PIL import Image, ImageDraw, ImageFont
from inky import InkyPHAT, InkyWHAT
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from font_intuitive import Intuitive
from datetime import datetime

colour = "red"
inky_display = InkyPHAT(colour)
scale_size = 1
padding = 0

# inky_display.set_rotation(180)

inky_display.set_border(inky_display.WHITE)

current_charge_percent = "49"
current_crange_miles = "74"
corrected_date = datetime.now()
# Create a new canvas to draw on

img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# Load the fonts

intuitive_font = ImageFont.truetype(Intuitive, int(20 * scale_size))
hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(21 * scale_size))
hanken_medium_font = ImageFont.truetype(HankenGroteskMedium, int(20 * scale_size))

# Top and bottom y-coordinates for the white strip

# battery_charge_bottom = int(inky_display.HEIGHT * (5.0 / 10.0))
battery_charge_bottom = 26
range_available_bottom = 56
# y_bottom = battery_charge_bottom + int(inky_display.HEIGHT * (4.0 / 10.0))
battery_gauge_top = inky_display.HEIGHT - 8
gauge_mark_bottom = battery_gauge_top - 2
gauge_mark_top = gauge_mark_bottom - 4
gauge_mark_major_top = gauge_mark_top - 4

# Draw the stripes

if int(current_charge_percent) >= 50:
    charge_range_background = inky_display.WHITE
    charge_range_text_colour = inky_display.BLACK
    charge_meter_colour = inky_display.BLACK
else:
    charge_range_background = inky_display.RED
    charge_range_text_colour = inky_display.WHITE
    charge_meter_colour = inky_display.RED

battery_gauge_width = round(inky_display.width * (int(current_charge_percent) / 100))

# Battery Charge stripe
# for y in range(0, battery_charge_bottom):
for y in range(0, battery_charge_bottom):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), charge_range_background)

# Available Range stripe
for y in range(battery_charge_bottom, range_available_bottom):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), charge_range_background)

# Date/Time Background
for y in range(range_available_bottom, battery_gauge_top):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.WHITE)

# Battery Gauge
for y in range(battery_gauge_top, inky_display.HEIGHT):
    for x in range(0, battery_gauge_width):
        img.putpixel((x, y), charge_meter_colour)

# Draw the text

# Calculate the positioning and draw the "Battery Charge" text
batt_charge_w, batt_charge_h = hanken_bold_font.getsize("Battery Charge:")
# batt_charge_x = int((inky_display.WIDTH - batt_charge_w) / 2)
batt_charge_x = 0 + padding
batt_charge_y = 0 + padding
draw.text((batt_charge_x, batt_charge_y), "Battery Charge:", charge_range_text_colour, font=hanken_bold_font)

# Calculate the positioning and draw the name text

current_charge = "{}%".format(current_charge_percent)
current_charge_w, current_charge_h = hanken_bold_font.getsize(current_charge)
# current_charge_x = int((inky_display.WIDTH - current_charge_w) / 2)
current_charge_x = int(batt_charge_w + 2)
# current_charge_y = int(battery_charge_bottom + ((battery_gauge_top - battery_charge_bottom - current_charge_h) / 2))
current_charge_y = 0 + padding
draw.text((current_charge_x, current_charge_y), current_charge, charge_range_text_colour, font=hanken_bold_font)

# Calculate the positioning and draw the "Available Range" text
current_range = "{}m".format(current_crange_miles)
available_range_w, available_range_h = hanken_bold_font.getsize("Available Range:")
available_range_x = 0 + padding
available_range_y = 28 + padding
draw.text((available_range_x, available_range_y), "Available Range:", charge_range_text_colour, font=hanken_bold_font)

current_range_w, current_range_h = hanken_bold_font.getsize(current_range)
current_range_x = int(available_range_w + 2)
current_range_y = 28 + padding
draw.text((current_range_x, current_range_y), current_range, charge_range_text_colour, font=hanken_bold_font)

datetime_range_x = 0 + padding
datetime_range_y = range_available_bottom + padding
draw.text((datetime_range_x, datetime_range_y), corrected_date.strftime("%d %b %I:%M %p"), inky_display.BLACK, font=hanken_bold_font)

for x in range(1, 4):
    gauge_mark_x = round(inky_display.WIDTH / 4 * x)
    for gauge_mark_y in range(gauge_mark_major_top, gauge_mark_bottom):
        img.putpixel((gauge_mark_x, gauge_mark_y), inky_display.BLACK)

for x in range(1, 12):
    gauge_mark_x = round(inky_display.WIDTH / 12 * x)
    for gauge_mark_y in range(gauge_mark_top, gauge_mark_bottom):
        img.putpixel((gauge_mark_x, gauge_mark_y), inky_display.BLACK)

# Display the completed image

inky_display.set_image(img)
inky_display.show()
