#!/usr/bin/env python

# Written by filip@skyscrape.rs
# 2014-02-11

import json
import os
import sys
from pprint import pprint
import commands

paramList = sys.argv
if len(paramList) <= 1:
    print "USAGE " + paramList[0] + " <auto scaling group name>"
    sys.exit(2)

asgName = paramList[1]

cmd = "/usr/local/bin/aws --profile nagiosro autoscaling describe-auto-scaling-groups --auto-scaling-group-names " + asgName
output = commands.getoutput(cmd)

jsondata = json.loads(output)
desiredCapacity = int(jsondata['AutoScalingGroups'][0]['DesiredCapacity'])
MinSize = int(jsondata['AutoScalingGroups'][0]['MinSize'])
MaxSize = int(jsondata['AutoScalingGroups'][0]['MaxSize'])

counterH = 0
instancesH = ""
counterUH = 0
instancesUH = ""
for item in jsondata['AutoScalingGroups'][0]['Instances']:
    if item['HealthStatus'] == 'Healthy':
        counterH += 1
	instancesH += " " + item['InstanceId']
    else:
        counterUH += 1
        instancesUH += " " + item['InstanceId']

if not instancesH:
    instancesH = " none"

if not instancesUH:
    instancesUH = " none"

msg = "Desired capacity " + str(desiredCapacity) + ". MinSize " + str(MinSize) + ". MaxSize " + str(MaxSize) + ". Healthy instances " + str(counterH) + ":" + instancesH + ". Unhealthy instances " + str(counterUH) + ":" + instancesUH

if counterH < desiredCapacity:
    print "CRITICAL - " + msg
    sys.exit(2)
elif counterUH > 0:
    print "WARNING - " + msg
    sys.exit(1)
else:
    print "OK - " + msg
    sys.exit(0)
