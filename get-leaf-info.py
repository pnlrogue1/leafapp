#!/usr/bin/env python

import time
import logging
import sys

import argparse
import pycarwings2
from configparser import ConfigParser

from PIL import Image, ImageDraw
from inky import InkyPHAT, InkyWHAT

configParser = ConfigParser()
candidates = ['config.ini', 'my_config.ini']
found = configParser.read(candidates)

username = configParser.get('get-leaf-info', 'username')
password = configParser.get('get-leaf-info', 'password')
region = configParser.get('get-leaf-info', 'region')
sleepsecs = 10     # Time to wait before polling Nissan servers for update

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
    key = leaf.request_update()
    status = leaf.get_status_from_update(key)
    # Currently the nissan servers eventually return status 200 from get_status_from_update(), previously
    # they did not, and it was necessary to check the date returned within get_latest_battery_status().
    while status is None:
        print("Waiting {0} seconds".format(sleepsecs))
        time.sleep(wait_time)
        status = leaf.get_status_from_update(key)
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

update_status = update_battery_status(leaf, sleepsecs)

latest_leaf_info = leaf.get_latest_battery_status()
latest_date = latest_leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]
print("latest_date=", latest_date)
print_info(latest_leaf_info)
