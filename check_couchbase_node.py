#!/usr/bin/python

##### LICENSE

# Copyright (c) Skyscrapers (iLibris bvba) 2015 - http://skyscrapers.eu
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


import requests
import json
import sys
import getopt


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hu:p:",["username=","password="])
    except getopt.GetoptError:
        print 'check_couchbase_node.py -u <username> -p <password>'
        sys.exit(3)

    if opts:
        for opt, arg in opts:
            if opt == '-h':
                print 'check_couchbase_node.py -u <username> -p <password>'
                sys.exit()
            elif opt in ("-u", "--username"):
                username = arg
            elif opt in ("-p", "--password"):
                password = arg
    else:
        print 'check_couchbase_node.py -u <username> -p <password>'
        sys.exit(3)
    status = get_status(username, password)
    node_status(status)
    print status


def get_status(username, password):
    try:
        r = requests.get("http://127.0.0.1:8091/pools/default", timeout=10, auth=(username, password))
    except requests.Timeout, e:
        print 'Time-out when querying for status'
        exit(0)
    if r.status_code != 200:
        print 'HTTP response is not 200 when requesting status'
        try:
            response = r.json()
            print response['error']
        except ValueError:
            print 'No JSON response'
        exit(3)

    response = r.json()
    return response

def node_status(status):
    output = ''
    code = 0
    for node in status['nodes']:
        if node['clusterMembership'] != 'active':
            output += 'Node ' + node['hostname'] + ' cluster membership is' + node['clusterMembership']
            code = 2

    if code == 0:
        output = 'Everything ok with the cluster'
    print output
    exit(code)

if __name__ == "__main__":
   main(sys.argv[1:])
