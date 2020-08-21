#!/usr/bin/env python

import logging
import re
import sys
import time
from datetime import datetime, timedelta

import argparse
import pycarwings2
from configparser import ConfigParser

configParser = ConfigParser()
candidates = ['config.ini', 'my_config.ini']
found = configParser.read(candidates)

username = configParser.get('get-leaf-info', 'username')
password = configParser.get('get-leaf-info', 'password')
region = configParser.get('get-leaf-info', 'region')
sleep_timer = 10  # Time to wait before polling Nissan servers for update

# Command line arguments to set Inky display type and colour

argParser = argparse.ArgumentParser()
argParser.add_argument('--type', '-t', type=str, required=True, default="phat",
                       choices=["what", "phat", "skip"], help="type of display. Use 'skip' to bypass the display")
argParser.add_argument('--colour', '-c', type=str, required=False, default="red",
                       choices=["red", "black", "yellow"], help="ePaper display colour")
args = argParser.parse_args()

if args.type != "skip":
    from PIL import Image, ImageDraw, ImageFont
    from inky import InkyPHAT, InkyWHAT
    from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
    from font_intuitive import Intuitive

    if args.type == "what":
        print("")
        print("This script does not currently support the InkyWHAT. Sorry!")
        print("")
        exit()


def update_battery_status(leaf, wait_time=1):
    total_wait = 0
    key = leaf.request_update()
    status = leaf.get_status_from_update(key)
    # Currently the nissan servers eventually return status 200 from get_status_from_update(), previously
    # they did not, and it was necessary to check the date returned within get_latest_battery_status().
    while status is None:
        total_wait += sleep_timer
        print("Waiting {0} seconds".format(sleep_timer))
        time.sleep(wait_time)
        status = leaf.get_status_from_update(key)
        if status is None and total_wait >= 40:
            status = 99
    return status


def print_info(info):
    # info.charging_status possibilities:
    #     "NORMAL_CHARGING" = charging on an L3 charger at home

    print("+----------------------------+-------------------+")
    print("| Operation Date and Time    | {}".format(
        info.answer["BatteryStatusRecords"]["OperationDateAndTime"]))
    print("| Notification Date and Time | {}".format(
        info.answer["BatteryStatusRecords"]["NotificationDateAndTime"]))
    print("| Battery Capacity           | {}/{}".format(
        info.battery_remaining_amount, info.battery_capacity))
    print("| Charging Status            | {}".format(info.charging_status))
    print("| Charging?                  | {}".format(info.is_charging))
    print("| Connected                  | {}".format(info.is_connected))
    batteryPercent = "| Battery Percent            | {}%".format(round(
        info.battery_percent))
    print(batteryPercent)
    range_km = float(info.answer["BatteryStatusRecords"]["CruisingRangeAcOff"]) / 1000
    print("| Range                      | {}km".format(
        round(range_km)))
    print("| Range                      | {} miles".format(
        round(range_km * 0.62137)))
    print("+----------------------------+-------------------+")

    # Options that I stopped using:

    # print("| Battery Capacity           | %s" % info.battery_capacity)
    # print("| Capacity Remaining         | %s" % info.battery_remaining_amount)
    # print("  battery_capacity2 %s" % info.answer["BatteryStatusRecords"]["BatteryStatus"]["BatteryCapacity"])
    # print("  is_quick_charging %s" % info.is_quick_charging)
    # print("  Connected?         | %s" % info.plugin_state)
    # print("  is_connected_to_quick_charger %s" % info.is_connected_to_quick_charger)
    # print("  time_to_full_trickle %s" % info.time_to_full_trickle)
    # print("  time_to_full_l2            | %s" % info.time_to_full_l2)
    # print("  time_to_full_l2_6kw %s" % info.time_to_full_l2_6kw)
    # print("| Battery Percent            | %s" % round(info.battery_percent))
    # print("  state_of_charge            | %s" % info.state_of_charge)


def query_battery_status(my_leaf, sleep_timer):
    update_status = update_battery_status(my_leaf, sleep_timer)
    while update_status == 99:
        print("Waiting 10 seconds and retrying")
        time.sleep(10)
        update_status = update_battery_status(my_leaf, sleep_timer)


# Main program

print("Prepare Session")
s = pycarwings2.Session(username, password, region)
print("Login...")
leaf = s.get_leaf()

# Give the nissan servers a bit of a delay so that we don't get stale data
time.sleep(1)

print("get_latest_battery_status from servers")
leaf_info = leaf.get_latest_battery_status()
start_date = leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]
print("start_date=", start_date)
print_info(leaf_info)

# Give the nissan servers a bit of a delay so that we don't get stale data
time.sleep(1)

print()
print("Getting the latest information from the car")

# query_battery_status(leaf, sleep_timer)
# update_status = update_battery_status(leaf, sleepsecs)
# while update_status == 99:
#     print("Retrying")
#     update_status = update_battery_status(leaf, sleepsecs)

# latest_leaf_info = leaf.get_latest_battery_status()
# latest_date = latest_leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]
latest_date = start_date
print("")

while leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"] == latest_date:
    print("Contacting the car...")
    query_battery_status(leaf, sleep_timer)
    latest_leaf_info = leaf.get_latest_battery_status()
    latest_date = latest_leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]

print("latest_date=", latest_date)
print_info(latest_leaf_info)
# Parse out the date
parsed_date = re.split('-| |:', latest_date) # Use re to split on "-", " " & ":"
month_converter = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}
compiled_date = datetime(
    int(parsed_date[2]),
    month_converter[parsed_date[1]],
    int(parsed_date[0]),
    int(parsed_date[3]),
    int(parsed_date[4]),
)
corrected_date = compiled_date - timedelta(hours = 1)

# Now for the e-ink display...
if args.type == "skip":
    exit()

colour = args.colour

if args.type == "phat":
    inky_display = InkyPHAT(colour)
    scale_size = 1
    padding = 0
# elif args.type == "what":
#     inky_display = InkyWHAT(colour)
#     scale_size = 2.20
#     padding = 15

# inky_display.set_rotation(180)

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
battery_charge_bottom = 26
range_available_bottom = 56
# y_bottom = battery_charge_bottom + int(inky_display.HEIGHT * (4.0 / 10.0))
y_footer_top = inky_display.HEIGHT - 5

# Draw the stripes

if latest_leaf_info.battery_percent >= 50:
    charge_range_background = inky_display.WHITE
    charge_range_text_colour = inky_display.BLACK
    charge_meter_colour = inky_display.BLACK
else:
    charge_range_background = inky_display.RED
    charge_range_text_colour = inky_display.WHITE
    charge_meter_colour = inky_display.RED

charge_meter_width = round(inky_display.width * (latest_leaf_info.battery_percent / 100))

# Battery Charge stripe
# for y in range(0, battery_charge_bottom):
for y in range(0, battery_charge_bottom):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), charge_range_background)

# Available Range stripe
for y in range(battery_charge_bottom, range_available_bottom):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), charge_range_background)

# White strip
for y in range(range_available_bottom, y_footer_top):
    for x in range(0, inky_display.width):
        img.putpixel((x, y), inky_display.WHITE)

# Footer
for y in range(y_footer_top, inky_display.HEIGHT):
    for x in range(0, charge_meter_width):
        img.putpixel((x, y), charge_meter_colour)

# Draw the text

# Calculate the positioning and draw the "Battery Charge" text
batt_charge_w, batt_charge_h = hanken_bold_font.getsize("Battery Charge:")
# batt_charge_x = int((inky_display.WIDTH - batt_charge_w) / 2)
batt_charge_x = 0 + padding
batt_charge_y = 0 + padding
draw.text((batt_charge_x, batt_charge_y), "Battery Charge:", charge_range_text_colour, font=hanken_bold_font)

# Calculate the positioning and draw the name text

current_charge = "{}%".format(round(latest_leaf_info.battery_percent))
current_charge_w, current_charge_h = hanken_bold_font.getsize(current_charge)
# current_charge_x = int((inky_display.WIDTH - current_charge_w) / 2)
current_charge_x = int(batt_charge_w + 2)
# current_charge_y = int(battery_charge_bottom + ((y_footer_top - battery_charge_bottom - current_charge_h) / 2))
current_charge_y = 0 + padding
draw.text((current_charge_x, current_charge_y), current_charge, charge_range_text_colour, font=hanken_bold_font)

# Calculate the positioning and draw the "Available Range" text
available_range_w, available_range_h = hanken_bold_font.getsize("Available Range:")
available_range_x = 0 + padding
available_range_y = 28 + padding
draw.text((available_range_x, available_range_y), "Available Range:", charge_range_text_colour, font=hanken_bold_font)

current_range = "{}m".format(
    round((float(latest_leaf_info.answer["BatteryStatusRecords"]["CruisingRangeAcOff"]) / 1000) * 0.62137)
)
current_range_w, current_range_h = hanken_bold_font.getsize(current_range)
current_range_x = int(available_range_w + 2)
current_range_y = 28 + padding
draw.text((current_range_x, current_range_y), current_range, charge_range_text_colour, font=hanken_bold_font)

datetime_range_x = 0 + padding
datetime_range_y = range_available_bottom + padding
draw.text((datetime_range_x, datetime_range_y), corrected_date.strftime("%d %b %I:%M %p"), inky_display.BLACK, font=hanken_bold_font)

# Display the completed image

inky_display.set_image(img)
inky_display.show()
