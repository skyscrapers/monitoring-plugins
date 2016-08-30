#!/usr/bin/env python

# Written by luca@skyscrape.rs
# 30-08-2016

import json
import sys
import requests
import argparse

status={"crit":2,"warn":1,"ok":0}

parser = argparse.ArgumentParser(description='This is a demo script by nixCraft.')
parser.add_argument('-H','--host', help='Marathon hostname', default="10.0.10.11")
parser.add_argument('-p','--port',help='Output file name', default="8080")
parser.add_argument('-w','--warn',help='% of unhealthy app that is considered a warning', default=20)
parser.add_argument('-c','--crit',help='% of unhealthy app that is considered critical', default=30)
parser.add_argument('-a','--app_list',help='List of apps to be monitored comma separated #TODO')
parser.add_argument('-W','--unmonit_warn',help='% of app without healthchecks with less task than desired running considered a warning',default=30)
parser.add_argument('-C','--unmonit_crit',help='% of app without healthchecks with less task than desired running considered critical',default=60)

args = parser.parse_args()
url="http://"+args.host+":"+args.port+"/v2/apps?embed=apps.counts"
r=requests.get(url)
curr_status = 0
msg=""

if r.status_code != 200:
    msg = "request exited with status code %s" % r.status_code
    curr_status = status["crit"]
else:
    apps_details=json.loads(r.text)
    for app in apps_details['apps']:
        if app['tasksUnhealthy'] > 0:
            xcent_unhealthy=(float(app["tasksUnhealthy"]/float(app["instances"]))*100)
            msg += "app %s has %s unhealthy tasks; " % (app["id"], app["tasksUnhealthy"])
            if curr_status<status["crit"]:
                if xcent_unhealthy >= args.crit:
                    curr_status = status["crit"]
                elif xcent_unhealthy >= args.warn:
                    curr_status = status["warn"]

        elif app['tasksHealthy'] is 0 and app['instances'] > app['tasksRunning']:
            msg += "app %s has less tasks running than expected: desired %s, current %s ; " % (app["id"],app['instances'], app['tasksRunning'])
            xcent_unhealthy=(float(app['instances'])- float(app['tasksRunning']))/float(app["instances"])*100
            if curr_status<status["crit"]:
                if xcent_unhealthy >= args.unmonit_crit:
                    curr_status = status["crit"]
                elif xcent_unhealthy >= args.unmonit_warn:
                    curr_status = status["warn"]

        print("%s tasksUnhealthy %s, tasksHealthy %s, tasksStaged %s, tasksRunning %s, instances %s" % (app["id"], app['tasksUnhealthy'], app['tasksHealthy'], app['tasksStaged'], app['tasksRunning'], app['instances']))


if curr_status is status["crit"]:
    print("CRITICAL - " + msg)
    sys.exit(2)
elif curr_status is status["warn"]:
    print "WARNING - " + msg
    sys.exit(1)
else:
    print "OK - all %s apps are running correctly" % len(apps_details['apps'])
    sys.exit(0)
