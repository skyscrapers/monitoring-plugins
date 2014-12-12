#!/usr/bin/env python

# Written by filip@skyscrape.rs
# 2014-05-30

import json
import os
import sys
from pprint import pprint
import commands

paramList = sys.argv
if len(paramList) <= 1:
    print "USAGE " + paramList[0] + " <cloudwatch metric>"
    sys.exit(2)

cwName = paramList[1]

cmd = "/usr/local/bin/aws --profile nagiosro cloudwatch describe-alarms --alarm-names " + cwName
output = commands.getoutput(cmd)

jsondata = json.loads(output)

for item in jsondata['MetricAlarms']:
    if item['StateValue'] == 'OK':
        print "OK - " + item['StateReason']
        sys.exit(0)
    else:
        print "CRITICAL - " + item['StateReason']
        sys.exit(2)
