#!/usr/bin/python

import sys
import argparse
import boto
import boto.sqs
import boto.ec2.cloudwatch
import datetime

def printUsage():
    print
    print "Example:    ", sys.argv[0], "--name myqueue --region us-east-1 --warn 10 --crit 20"
    print

metrics = {
    'queue_length': 'Messages in queue',
    'oldest_message': 'ApproximateAgeOfOldestMessage'
}

#Parse command line arguments
parser = argparse.ArgumentParser(description='This script is a Nagios check that \
                                    monitors the number of messages in Amazon SQS \
                                    queues')

parser.add_argument('--name', dest='name', type=str, required=True,
                        help='Name of SQS queue. This can be a wildcard match. \
                              For example a name of blah_ would match blah_1, \
                              blah_2, blah_foobar. To monitor a single queue, enter \
                              the exact name of the queue.')

parser.add_argument('--region', dest='region', type=str, default='us-east-1',
                        help='AWS Region hosting the SQS queue. \
                              Default is us-east-1.')

parser.add_argument('--warn', dest='warn', type=int, required=True,
                        help='Warning level for queue depth.')

parser.add_argument('--crit', dest='crit', type=int, required=True,
                        help='Critical level for queue depth.')

parser.add_argument('--metric', dest='metric', type=str, required=True, help='metric to check: [%s]' % ', '.join(metrics.keys()))

parser.add_argument('--debug', action='store_true', help='Enable debug output.')

args = parser.parse_args()

# Assign command line args to variable names
queue_name = args.name
region = args.region
warn_depth = args.warn
crit_depth = args.crit
if args.metric not in metrics.keys():
    print "ERROR: Metric value not available."
    printUsage()
    exit(2)

if crit_depth <= warn_depth:
    print
    print "ERROR: Critical value must be larger than warning value."
    printUsage()
    exit(2)


q_list = []
depth_list = []

# Make SQS connection
# conn = boto.sqs.connect_to_region(region)
conn = boto.sqs.connect_to_region(region)
rs = conn.get_all_queues(prefix=queue_name)

def get_metric(queue, metric, start_time, end_time, step):
    """Get SQS metric from CloudWatch"""
    cw_conn = boto.ec2.cloudwatch.connect_to_region(region)
    result = cw_conn.get_metric_statistics(
        step,
        start_time,
        end_time,
        metric,
        'AWS/SQS',
        'Average',
        dimensions={'QueueName': queue}
    )

    if result:
        if len(result) > 1:
            # Get the last point
            result = sorted(result, key=lambda k: k['Timestamp'])
            result.reverse()

        result = float('%.2f' % result[0]['Average'])
    return result


# Loop through each queue and get message count
# Push the queue name and depth to lists
now = datetime.datetime.utcnow()
oldest_messages = []
for qname in rs:
    namelist = str(qname.id).split("/") # Split out queue name
    if args.metric == 'queue_length':
        q_list.append(namelist[2])
        depth_list.append(int(qname.count()))
    elif args.metric == 'oldest_message':
        points = 5
        retries = 0
        def get_oldest_message():
            return get_metric(namelist[2],"ApproximateAgeOfOldestMessage",now - datetime.timedelta(seconds=points * 60), now, 60*points)
        queue_metric=get_oldest_message()
        def isfloat(text):
            try:
                float(text)
                return True
            except:
                return False
        while retries < 10 and not isfloat(str(queue_metric)):
            print(queue_metric)
            retries = retries +1
            time.sleep(retries*10)
            queue_metric=get_oldest_message()
        print(queue_metric)
        oldest_messages.append({"queue_name":namelist[2], "oldest_message": queue_metric, "queue_length": int(qname.count())})

def return_queue_length(q_list,depth_list):
    status_msg_list = []
    status_msg = ""
    msg_line = ""
    perfdata_msg = ""
    warn_count = 0
    crit_count = 0
    exit_code = 3
    for index in range(len(q_list)):
        if depth_list[index] >= warn_depth and depth_list[index] < crit_depth:
            warn_count += 1
        if depth_list[index] >= crit_depth:
            crit_count += 1
        #print index, ": ", q_list[index], depth_list[index]
        msg_line = q_list[index] + ":" + str(depth_list[index])
        status_msg_list.append(msg_line)

    # Set exit code based on number of warnings and criticals
    if warn_count == 0 and crit_count == 0:
        status_msg_list.insert(0, "OK - Queue depth (")
        exit_code = 0
    elif warn_count > 0 and crit_count == 0:
        status_msg_list.insert(0, "WARNING - Queue depth (")
        exit_code = 1
    elif crit_count > 0:
        status_msg_list.insert(0, "CRITICAL - Queue depth (")
        exit_code = 2
    else:
        status_msg_list.insert(0, "UNKNOWN - Queue depth (")
        exit_code = 3

    # Build status message output
    for msg in status_msg_list:
        status_msg += msg + " "

    # Build perfdata output
    for index in range(len(q_list)):
        perfdata_msg += q_list[index] + "=" + str(depth_list[index]) + ";" + str(warn_depth) + ";" + str(crit_depth) + "; "

    # Finalize status message
    status_msg += ") [W:" + str(warn_depth) + " C:" + str(crit_depth) + "]"

    # Print final output for Nagios
    print status_msg + "|" + perfdata_msg

    # Exit with appropriate code
    exit(exit_code)
def return_oldest_messages(oldest_messages):
    status_msg_list = []
    status_msg = ""
    msg_line = ""
    perfdata_msg = ""
    warn_count = 0
    crit_count = 0
    exit_code = 3
    for queue in oldest_messages:
        if queue['oldest_message'] >= warn_depth and queue['oldest_message'] < crit_depth:
            warn_count += 1
        if queue['oldest_message'] >= crit_depth:
            crit_count += 1
        msg_line = queue['queue_name'] + ":" + str(queue['oldest_message'])
        status_msg_list.append(msg_line)
        perfdata_msg +=  queue['queue_name'] + "=" + str(queue['oldest_message']) + ";" + str(warn_depth) + ";" + str(crit_depth) + "; "

    # Set exit code based on number of warnings and criticals
    if warn_count == 0 and crit_count == 0:
        status_msg_list.insert(0, "OK - Oldest Message (")
        exit_code = 0
    elif warn_count > 0 and crit_count == 0:
        status_msg_list.insert(0, "WARNING - Oldest Message (")
        exit_code = 1
    elif crit_count > 0:
        status_msg_list.insert(0, "CRITICAL - Oldest Message (")
        exit_code = 2
    else:
        status_msg_list.insert(0, "UNKNOWN - Oldest Message (")
        exit_code = 3

    # Build status message output
    for msg in status_msg_list:
        status_msg += msg + " "

    # Finalize status message
    status_msg += ") [W:" + str(warn_depth) + " C:" + str(crit_depth) + "]"

    # Print final output for Nagios
    print status_msg + "|" + perfdata_msg
    exit(exit_code)

if args.metric == 'queue_length':
    return_queue_length(q_list,depth_list)
elif args.metric == 'oldest_message':
    return_oldest_messages(oldest_messages)
