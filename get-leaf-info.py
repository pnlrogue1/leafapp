#!/usr/bin/env python

import time
import logging
import sys

import argparse
import pycarwings2
from configparser import ConfigParser

from PIL import Image, ImageDraw
from inky import InkyPHAT, InkyWHAT
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from font_intuitive import Intuitive

configParser = ConfigParser()
candidates = ['config.ini', 'my_config.ini']
found = configParser.read(candidates)

username = configParser.get('get-leaf-info', 'username')
password = configParser.get('get-leaf-info', 'password')
region = configParser.get('get-leaf-info', 'region')
sleep_timer = 10  # Time to wait before polling Nissan servers for update

# Command line arguments to set Inky display type and colour

argParser = argparse.ArgumentParser()
argParser.add_argument('--type', '-t', type=str, required=True,
                       choices=["what", "phat"], help="type of display")
argParser.add_argument('--colour', '-c', type=str, required=True,
                       choices=["red", "black", "yellow"], help="ePaper display colour")
args = argParser.parse_args()

colour = args.colour

# Set up the correct display and scaling factors

if args.type == "phat":
    inky_display = InkyPHAT(colour)
    scale_size = 1
    padding = 0
elif args.type == "what":
    inky_display = InkyWHAT(colour)
    scale_size = 2.20
    padding = 15
    print("")
    print("This script does not currently support the InkyWHAT. Sorry!")
    print("")
    exit()


# inky_display.set_rotation(180)


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
        if status is None and total_wait >= 60:
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
        print("Retrying")
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

query_battery_status(leaf, sleep_timer)
# update_status = update_battery_status(leaf, sleepsecs)
# while update_status == 99:
#     print("Retrying")
#     update_status = update_battery_status(leaf, sleepsecs)

latest_leaf_info = leaf.get_latest_battery_status()
latest_date = latest_leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]

while leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"] == latest_date:
    print("")
    print("Didn't get new data from the car. Retrying...")
    print("")
    query_battery_status(leaf, sleep_timer)
    latest_leaf_info = leaf.get_latest_battery_status()
    latest_date = latest_leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]

print("latest_date=", latest_date)
print_info(latest_leaf_info)

# Now for the e-ink display...

inky_display.set_border(inky_display.WHITE)

# Create a new canvas to draw on

img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# Load the fonts

intuitive_font = ImageFont.truetype(Intuitive, int(22 * scale_size))
hanken_bold_font = ImageFont.truetype(HankenGroteskBold, int(35 * scale_size))
hanken_medium_font = ImageFont.truetype(HankenGroteskMedium, int(16 * scale_size))

# Grab the name to be displayed

name = args.name

# Top and bottom y-coordinates for the white strip

y_top = int(inky_display.HEIGHT * (5.0 / 10.0))
y_bottom = y_top + int(inky_display.HEIGHT * (4.0 / 10.0))

# Draw the red, white, and red strips

#for y in range(0, y_top):
#    for x in range(0, inky_display.width):
#        img.putpixel((x, y), inky_display.RED)
#
#for y in range(y_top, y_bottom):
#    for x in range(0, inky_display.width):
#        img.putpixel((x, y), inky_display.WHITE)
#
#for y in range(y_bottom, inky_display.HEIGHT):
#    for x in range(0, inky_display.width):
#        img.putpixel((x, y), inky_display.RED)

# Calculate the positioning and draw the "Hello" text

batt_charge_w, batt_charge_h = hanken_bold_font.getsize("Battery Charge:")
batt_charge_x = int((inky_display.WIDTH - batt_charge_w) / 2)
batt_charge_y = 0 + padding
draw.text((batt_charge_x, batt_charge_y), "Battery Charge:", inky_display.WHITE, font=hanken_bold_font)

# Calculate the positioning and draw the "my name is" text

# mynameis_w, mynameis_h = hanken_medium_font.getsize("my name is")
# mynameis_x = int((inky_display.WIDTH - mynameis_w) / 2)
# mynameis_y = batt_charge_h + padding
# draw.text((mynameis_x, mynameis_y), "my name is", inky_display.WHITE, font=hanken_medium_font)

# Calculate the positioning and draw the name text

current_charge = "{}%".format(latest_leaf_info.battery_percent)
current_charge_w, current_charge_h = intuitive_font.getsize(current_charge)
current_charge_x = int((inky_display.WIDTH - current_charge_w) / 2)
current_charge_y = int(y_top + ((y_bottom - y_top - current_charge_h) / 2))
draw.text((current_charge_x, current_charge_y), current_charge, inky_display.BLACK, font=intuitive_font)

# Display the completed name badge

inky_display.set_image(img)
inky_display.show()
