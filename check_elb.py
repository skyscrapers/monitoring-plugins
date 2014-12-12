#!/usr/bin/env python

# Written by filip@skyscrape.rs
# 2014-04-29

import json
import os
import sys
from pprint import pprint
import commands

paramList = sys.argv
if len(paramList) <= 1:
    print "USAGE " + paramList[0] + " <ELB name>"
    sys.exit(2)

elbName = paramList[1]

cmd = "/usr/local/bin/aws --profile nagiosro elb describe-instance-health --load-balancer-name " + elbName
output = commands.getoutput(cmd)

jsondata = json.loads(output)

counterH = 0
instancesH = ""
counterUH = 0
instancesUH = ""
for item in jsondata['InstanceStates']:
    if item['State'] == 'InService':
        counterH += 1
        instancesH += " " + item['InstanceId']
    else:
        counterUH += 1
        instancesUH += " " + item['InstanceId']

if not instancesH:
    instancesH = " none"

if not instancesUH:
    instancesUH = " none"

msg = "InService count " + str(counterH) + ":" + instancesH + ". OutOfService count " + str(counterUH) + ":" + instancesUH

if counterH == 0:
    print "CRITICAL - " + msg
    sys.exit(2)
elif counterUH > 0:
    print "WARNING - " + msg
    sys.exit(1)
else:
    print "OK - " + msg
    sys.exit(0)
