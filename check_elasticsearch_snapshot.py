#!/usr/bin/python

##### LICENSE

# Copyright (c) Skyscrapers (iLibris bvba) 2014 - http://skyscrape.rs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import requests
import json
import sys
import getopt
import datetime
from time import mktime
from datetime import timedelta

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hn:a:",["name=","age="])
    except getopt.GetoptError:
        print 'check_elasticsearch_snapshot.py -n <name> -a <max backup age hours>'
        sys.exit(3)

    if opts:
        for opt, arg in opts:
            if opt == '-h':
                print 'check_elasticsearch_snapshot.py -n <name> -a <max backup age hours>'
                sys.exit()
            elif opt in ("-n", "--name"):
                name = arg
            elif opt in ("-a", "--age"):
                age = int(arg)
    else:
        print 'check_elasticsearch_snapshot.py -n <name> -a <max backup age hours>'
        sys.exit(3)

    matched = match_backup(name, age)
    output(matched, age)

def get_snapshots(name):
    try:
        r = requests.get("http://localhost:9200/_snapshot/" + name + "/_all", timeout=10)
    except requests.Timeout, e:
        print 'Time-out when querying for snapshots'
        exit(0)
    if r.status_code != 200:
        print 'HTTP response is not 200 when requesting snapshots'
        try:
            response = r.json()
            print response['error']
        except ValueError:
            print 'No JSON response'
        exit(3)

    response = r.json()
    return response

def match_backup(name, age):
    max_backup_age = datetime.datetime.now() - timedelta(hours=age)
    max_miliseconds_age = 1000*mktime(max_backup_age.timetuple())

    snapshots = get_snapshots(name)

    matched = False
    for snapshot in snapshots['snapshots']:
        if snapshot['end_time_in_millis'] > max_miliseconds_age:
            matched = True
    return matched

def output(matched, age):
    if matched:
        print 'Backup is not older then ' + str(age) + ' hours.'
        exit(0)
    else:
        print 'Backup is older then ' + str(age) + ' hours.'
        exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
