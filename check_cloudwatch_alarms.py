#!/usr/bin/env python

# Written by juancarlos@skyscrapers.eu
# 2016-01-06
# Configuration needed:
# export AWS_ACCESS_KEY_ID=
# export AWS_SECRET_ACCESS_KEY=
# export AWS_DEFAULT_REGION=eu-west-1


import boto3
import json
import sys
import argparse
import os
from wsgiref.validate import check_status
import code
import re
import logging
import base64

################################################################
client = None

OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3

def get_client():
    return boto3.resource('cloudwatch')

def main(argv):
    parser = argparse.ArgumentParser(description='Check cloud watch alarms.')
    parser.add_argument('statevalue', metavar='statevalue', 
                       help='state value to filter')
    parser.add_argument('--alarmnames', metavar='an', dest='alarmNames', 
                        nargs='*',
                       help='Alarm names for filtering')
    parser.add_argument('--nonCritical', metavar='nonCritical', dest='nonCritical', 
                       type=bool, default=False,
                       help='Setting to true CRITICAL state would be never returned')
    
    parser.add_argument('--alarmfilterexpression',dest='alarmFilterExpression', 
                        help='Expression for filter the alarms (python syntax)')

    parser.add_argument('--alarmfilterexpressionenc',dest='alarmFilterExpressionEncoded', 
                        help='Expression for filter the alarms (python syntax), encoded in base64')

    parser.add_argument('--AWS_DEFAULT_REGION',dest='AWS_DEFAULT_REGION', 
                        help='AWS parameter: AWS_DEFAULT_REGION')
    parser.add_argument('--AWS_ACCESS_KEY_ID',dest='AWS_ACCESS_KEY_ID', 
                        help='AWS parameter: AWS_ACCESS_KEY_ID')
    parser.add_argument('--AWS_SECRET_ACCESS_KEY',dest='AWS_SECRET_ACCESS_KEY', 
                        help='AWS parameter: AWS_SECRET_ACCESS_KEY')

    args = parser.parse_args()
    set_aws_params(args)
    code = do_checks(args.statevalue, args.alarmNames, get_alarm_filter_expression(args))
    exit(code)
    
def get_alarm_filter_expression(args):
    if args.alarmFilterExpression:
        return args.alarmFilterExpression
    if args.alarmFilterExpressionEncoded:
        return base64.b64decode(args.alarmFilterExpressionEncoded)
    return None


def do_checks(statevalue, alarmNames, alarmFilterExpression):
    print("Command do_checks:")
    print("stateValue: " + statevalue)
    if alarmFilterExpression:
        print("alarmFilterExpression: " + alarmFilterExpression)
    if alarmNames:
        print("alarmNames: " + alarmNames)

    client = get_client()    
    alarms = get_alarms(client, statevalue, alarmNames)
    alarms = filter_alarms(alarms, alarmFilterExpression)
    code = check_status(alarms, statevalue)
    return code
    
def set_aws_params(args):
    #print("AWS_DEFAULT_REGION-"+os.environ['AWS_DEFAULT_REGION'])
    if args.AWS_DEFAULT_REGION:
        os.environ['AWS_DEFAULT_REGION'] = args.AWS_DEFAULT_REGION
    if args.AWS_ACCESS_KEY_ID:
        os.environ['AWS_ACCESS_KEY_ID'] = args.AWS_ACCESS_KEY_ID
    if args.AWS_SECRET_ACCESS_KEY:
        os.environ['AWS_SECRET_ACCESS_KEY'] = args.AWS_SECRET_ACCESS_KEY

def get_alarms(client, stateValue, alarmNames):
    if alarmNames:
        alarms = client.alarms.filter(
                                      StateValue=stateValue,
                                      AlarmNames=alarmNames,
            )
    else:
        alarms = client.alarms.filter(
                                      StateValue=stateValue,
            )
    return alarms
    
def filter_alarms(alarms, alarmFilterExpression=None):
    if alarmFilterExpression is None:
        return alarms
    else:
        alarmsFiltered = []
        for alarm in alarms:
            r = re.compile(alarmFilterExpression, flags=re.I | re.X)
            match = r.match(alarm.name)
            if match:                      
                alarmsFiltered.append(alarm)
        return alarmsFiltered

def check_status(alarms, stateValue, nonCritical=False):
    output = ''
    code = OK
    #print("alarms " + alarms)
    if not alarms:
        output = 'OK - No alarms in cloudwatch'
    else:
        countAlarms = 0
        for alarm in alarms:
            if stateValue == "ERROR":
                output += "CRITICAL - " + alarm.state_value + " - in cloudwatch\n"
                if nonCritical:
                    code = WARNING
                else:
                    code = CRITICAL
            elif stateValue == "INSUFFICIENT_DATA":
                output += "WARNING - " + alarm.state_value + " - in cloudwatch\n"
                code = WARNING
            elif stateValue == "OK":
                output += "WARNING - " + alarm.state_value + " - in cloudwatch\n"
                code = WARNING
            else:
                output += "WARNING - " + alarm.state_value + " - in cloudwatch\n"
                code = UNKNOWN
            output += "  alarm.name=" + alarm.name + "\n"
            output += "  alarm.alarm_description=" + str(alarm.alarm_description) + "\n"
            output += "  alarm.state_value=" + str(alarm.state_value) + "\n"
            output += "  alarm.state_reason=" + str(alarm.state_reason) + "\n"
            output += "  alarm.state_reason_data=" + str(alarm.state_reason_data) + "\n"
            output += "  alarm.state_updated_timestamp=" + str(alarm.state_updated_timestamp) + "\n"
            output += "  alarm.actions_enabled=" + str(alarm.actions_enabled) + "\n"
            output += "  alarm.alarm_actions=" + str(alarm.alarm_actions) + "\n"
            output += "  alarm.alarm_arn=" + alarm.alarm_arn + "\n"
            output += "  alarm.alarm_configuration_updated_timestamp=" + str(alarm.alarm_configuration_updated_timestamp) + "\n"
            output += "  alarm.comparison_operator=" + str(alarm.comparison_operator) + "\n"
            output += "  alarm.dimensions=" + str(alarm.dimensions) + "\n"
            output += "  alarm.evaluation_periods=" + str(alarm.evaluation_periods) + "\n"
            output += "  alarm.insufficient_data_actions=" + str(alarm.insufficient_data_actions) + "\n"
            output += "  alarm.metric_name=" + str(alarm.metric_name) + "\n"
            output += "  alarm.namespace=" + str(alarm.namespace) + "\n"
            output += "  alarm.ok_actions=" + str(alarm.ok_actions) + "\n"
            output += "  alarm.period=" + str(alarm.period) + "\n"
            output += "  alarm.statistic=" + str(alarm.statistic) + "\n"
            output += "  alarm.threshold=" + str(alarm.threshold) + "\n"
            output += "  alarm.namealarm.unit=" + str(alarm.unit) + "\n"
            countAlarms += 1
        if countAlarms > 0:
            print ("Found " + str(countAlarms) + " alarms found for State - " +stateValue + " - in cloudwatch\n")

    print (output)
    return code

#    print(json.dumps(alarm))
if __name__ == "__main__":
   main(sys.argv[1:])
