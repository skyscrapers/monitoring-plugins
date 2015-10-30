#!/usr/bin/env python
# -*- coding: utf-8; -*-
"""

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

check_couchbase.py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>

Required libs:
- pycurl
- cStringIO
- json
- sys

Warning:    If you use Python 3, change "import cStringIO" to "import io" and any occurences of cStringIO
            to io.StringIO


This plugin implements two checks:
1. Cluster overall status: memory and disk usage (-s option)
2. Per vBucket memory usage (-b option)

See ./check_couchbase.py -h for detailed options list

Author: Grzegorz "You can call me Greg" Adamowicz (gadamowicz@gstlt.info)
URL: http://gstlt.info

Version: 1.0

"""

from optparse import OptionParser
import pycurl
import cStringIO
import json
import sys


nagios_codes = {
    'OK': 0,
    'WARNING': 1,
    'CRITICAL': 2,
    'UNKNOWN': 3,
    'DEPENDENT': 4,
}

# This will save curl response string (json)
curl_response = cStringIO.StringIO()

""" Functions """
""" Run curl """
def run_curl(url, userpwd):
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
    c.setopt(pycurl.VERBOSE, 0)

    c.setopt(pycurl.USERPWD, userpwd)

    c.setopt(pycurl.WRITEFUNCTION, curl_response.write)
    # run it
    c.perform()

    # close connection
    c.close()

    return 0

""" Get all buckets statistics """
def get_all_buckets_stats(server_string, user, password):

    try:
        run_curl(server_string, user + ":" + password)

    except Exception:
        print("CRITICAL - Node %s down"%(server_string))
        sys.exit(nagios_codes['CRITICAL'])

    try:
        # parse json string to python object (array => list)
        j = json.loads(curl_response.getvalue())
    except Exception:
        print("UNKNOWN - got malformed json from server")
        sys.exit(nagios_codes['UNKNOWN'])


    # delete all stringio content
    curl_response.truncate(0)

    return j


"""
    Check overall cluster status
    1. If cluster is balanced
    2. If memory usage is below warning/critical values
    3. If hdd usage is belo warning/critical values

"""
def check_status(hostname, port, user, passwd, warning, critical):

    url = "http://" + hostname + ":" + port + "/pools/nodes"

    try:
        run_curl(url, user + ":" + passwd)

    except Exception:
        print("CRITICAL - Node %s:%s down"%(hostname, port))
        sys.exit(nagios_codes['CRITICAL'])


    try:
        # parse json string to python object (array => list)
        j = json.loads(curl_response.getvalue())
    except Exception:
        print("UNKNOWN - got malformed json from server")
        sys.exit(nagios_codes['UNKNOWN'])

    # get mem usage
    mem_used = float(j['storageTotals']['ram']['used'])
    mem_total = float(j['storageTotals']['ram']['total'])
    mem_percentage = round((mem_used / mem_total) * 100, 2)

    # get hdd usage
    hdd_used = float(j['storageTotals']['hdd']['used'])
    hdd_total = float(j['storageTotals']['hdd']['total'])
    hdd_percentage = round((hdd_used / hdd_total) * 100, 2)

    # get balance status
    try:
        balance_status = j['balanced']
    except Exception:
        print("UNKNOWN - got malformed json from server")
        sys.exit(nagios_codes['UNKNOWN'])

    # We now have all needed data. Do the checking.

    if balance_status == True:
        if mem_percentage >= critical or hdd_percentage >= critical:
            print("CRITICAL - balanced, %0.2f%% mem free, %0.2f%% disk free"%(100.00 - mem_percentage, 100.00 - hdd_percentage))
            sys.exit(nagios_codes['CRITICAL'])
        elif mem_percentage >= warning or hdd_percentage >= warning:
            print("WARNING - balanced, %0.2f%% mem free, %0.2f%% disk free"%(100.00 - mem_percentage, 100.00 - hdd_percentage))
            sys.exit(nagios_codes['WARNING'])
        else:
            print("OK - balanced, %0.2f%% mem free, %0.2f%% disk free"%(100.00 - mem_percentage, 100.00 - hdd_percentage))
            sys.exit(nagios_codes['OK'])

    else:
        print("CRITICAL - UNBALANCED, %0.2f%% mem free, %0.2f%% disk free"%(100.00 - mem_percentage, 100.00 - hdd_percentage))
        sys.exit(nagios_codes['CRITICAL'])


    return 0


"""
    Check all buckets stats
"""
def check_buckets(hostname, port, user, passwd, warning, critical):

    buckets_url = "http://" + hostname + ":" + port + "/pools/nodes/buckets"

    # get all buckets stats
    buckets_stats = get_all_buckets_stats(buckets_url, user, passwd)

    status = nagios_codes['OK']
    status_text = []

    for bucket in buckets_stats:


        if bucket['basicStats']['quotaPercentUsed'] >= critical:
            status_text.append("bucket: " + bucket['name'] + \
                                          " (%0.2f%%)"%(bucket['basicStats']['quotaPercentUsed']) + " is full")
            status = nagios_codes['CRITICAL']

        elif bucket['basicStats']['quotaPercentUsed'] >= warning:
            status_text.append("bucket: " + bucket['name'] + \
                                          " (%0.2f%%)"%(bucket['basicStats']['quotaPercentUsed']) + " is over limit")

            if status <= nagios_codes['WARNING']:
                status = nagios_codes['WARNING']


    if status > nagios_codes['OK']:

        if status == nagios_codes['WARNING']:
            return_str = "WARNING - "

        elif status == nagios_codes['CRITICAL']:
            return_str = "CRITICAL - "

        for info_text in status_text:
            return_str = return_str + info_text + ", "

        print(return_str[:-2])
        sys.exit(status)
    else:
        print("OK - %i buckets ready"%(len(buckets_stats)))
        sys.exit(nagios_codes['OK'])


    return 0


# Check if all required options are there etc.
def check_options(options):

    if options.hostname == None:
        print("UNKNOWN - no hostname provided")
        return 1

    if options.username == None or options.password == None:
        print("UNKNOWN - no username or password")
        return 1

    if options.critical == None or options.warning == None:
        print("UNKNOWN - please provide critical and warning values (percentage used mem or hdd)")
        return 1

    if options.critical < options.warning:
        print("UNKNOWN - critical value must be larger than warning")
        return 1

    if options.check_status != True and options.check_buckets != True:
        print("UNKNOWN - check status or check buckets options must be provided")
        return 1

    return 0



""" Main program """
def main():
    """
    Options definition
    See: http://docs.python.org/2/library/optparse.html
    """
    usage = "usage: %prog -H hostname [-P port] -u username -p password -w XX -c XX [-s|-b]"
    parser = OptionParser(usage=usage)

    parser.add_option("-H", "--hostname", dest="hostname", help="Cluster host name or IP address")
    parser.add_option("-P", "--port", dest="port", default="8091", help="API port, default: 8091")
    parser.add_option("-u", "--username", dest="username", help="User name used to connect to Couchbase server")
    parser.add_option("-p", "--password", dest="password", help="Password")
    parser.add_option("-s", "--check-status", action="store_true", dest="check_status", default="False", help="Check cluster status (MEM and HDD usage)")
    parser.add_option("-b", "--check-buckets", action="store_true", dest="check_buckets", default="False", help="Check buckets MEM usage")

    parser.add_option("-w", "--warning", type="float", dest="warning", help="Warning value % (percent), eg. -w 95")
    parser.add_option("-c", "--critical", type="float", dest="critical", help="Critical value % (percent), eg. -c 98")

    (options, args) = parser.parse_args()

    if check_options(options) > 0:
        sys.exit(nagios_codes['UNKNOWN'])

    if options.check_status == True:
        check_status(options.hostname, options.port, options.username, options.password, options.warning, options.critical)

    if options.check_buckets == True:
        check_buckets(options.hostname, options.port, options.username, options.password, options.warning, options.critical)

    # if we got this far, we probably don't know what's going on
    print("UNKNOWN - not enough options given, see %prog -h for help")
    sys.exit(nagios_codes['UNKNOWN'])



if __name__ == "__main__":
    main()
