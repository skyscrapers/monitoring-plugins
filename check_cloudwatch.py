#!/usr/bin/env python

import json
import os
import boto3
import argparse

OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3

parser = argparse.ArgumentParser(description='Check cloud watch alarms.')
parser.add_argument('--alarmnames', metavar='an', dest='alarmNames', nargs='*', help='Alarm names for filtering')
parser.add_argument('--region', metavar='r', dest='region', help='AWS Region', default='eu-west-1' )
args = parser.parse_args()

client = boto3.client('cloudwatch',region_name=args.region)

alarms = client.describe_alarms(AlarmNames=args.alarmNames)
output = ""
countAlarms=0
code = 0
for alarm in alarms["MetricAlarms"]:
    if alarm["StateValue"] == "ALARM":
        output += "CRITICAL - " + alarm["StateValue"] + " - in cloudwatch\n"
        code = CRITICAL
    elif alarm["StateValue"] in ["OK","INSUFFICIENT_DATA"] :
        output += "OK - " + alarm["StateValue"] + " - in cloudwatch\n"
        if code == 0: code = OK
    else:
        output += "WARNING - " + alarm["StateValue"] + " - in cloudwatch\n"
        if code != CRITICAL: code = WARNING
    output += "  ALARM NAME:" + alarm["AlarmName"] + "\n"
    output += "  ALARM DESCRIPTION:" + str(alarm["AlarmDescription"]) + "\n"

    countAlarms += 1

print (output)
exit(code)
