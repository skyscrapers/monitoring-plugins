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
    print "USAGE " + paramList[0] + " <auto scaling group name>"
    sys.exit(2)

asgName = paramList[1]

cmd = "/usr/local/bin/aws --profile nagiosro autoscaling describe-auto-scaling-groups --auto-scaling-group-names " + asgName
output = commands.getoutput(cmd)

jsondata = json.loads(output)

aLaunchConf = []
for item in jsondata['AutoScalingGroups'][0]['Instances']:
    if item['HealthStatus'] == 'Healthy':
        aLaunchConf.append(str(item['LaunchConfigurationName']))

if len(aLaunchConf) > 0:
    uniqueLaunchConf = set(aLaunchConf)
    if len(uniqueLaunchConf) == 1:
        sys.stdout.write("OK - only one Launch Configuration in use: " + list(uniqueLaunchConf)[0])
        sys.exit(0)
    else:
        sys.stdout.write("CRITICAL - multiple Launch Configurations detected:")
        for lc in list(uniqueLaunchConf):
            sys.stdout.write(" " + lc)
        sys.exit(2)

else:
    print "UNKNOWN - no healthy instances found in " + asgName
    sys.exit(3)
