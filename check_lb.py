#!/usr/bin/env python

import boto3
import getopt
import sys
import botocore


def main(argv):
    helptext = 'check_lb.py -l <loadbalancer_name>'

    try:
        opts, args = getopt.getopt(argv, "hl:", ["loadbalancer-name="])
    except getopt.GetoptError:
        print helptext
        sys.exit(2)

    if opts:
        for opt, arg in opts:
            if opt == '-h':
                print helptext
                sys.exit(2)
            elif opt in ("-l", "--loadbalancer-name"):
                lb_name = arg
    else:
        print helptext
        sys.exit(2)

    global albClient
    global elbClient
    session = botocore.session.get_session()
    session.user_agent_name = 'check_lb'
    session.set_config_variable('profile', 'nagiosro')
    albClient = session.create_client('elbv2')
    elbClient = session.create_client('elb')

    messages = []
    criticalExit = False
    warningExit = False
    okExit = False

    lb_health = GetLbHealth(lb_name)

    if alb_exist(lb_name):
        for targetGroup, health in lb_health["targetGroups"].iteritems():

            if health["healthyCount"] == 0 and health["instanceCount"] > 0:
                messages.append('CRITICAL - Loadbalancer %s has Targetgroup %s with %s healthy targets out of %s instances' % (lb_name, targetGroup, health["healthyCount"], health["instanceCount"]))
                criticalExit = True

            elif health["healthyCount"] > 0 and health["unHealthyCount"] > 0:
                messages.append('WARNING - Loadbalancer %s has Targetgroup %s with %s healthy targets out of %s instances' % (lb_name, targetGroup, health["healthyCount"], health["instanceCount"]))
                warningExit = True

            elif health["unHealthyCount"] == 0:
                messages.append('OK - Loadbalancer %s has Targetgroup %s with %s healthy targets out of %s instances' % (lb_name, targetGroup, health["healthyCount"], health["instanceCount"]))
                okExit = True
    elif elb_exist(lb_name):
        if lb_health["healthyCount"] == 0 and lb_health["instanceCount"] > 0:
            messages.append('CRITICAL - Loadbalancer %s has %s healthy instances out of %s instances' % (lb_name, lb_health["healthyCount"], lb_health["instanceCount"]))
            criticalExit = True
        elif lb_health["unHealthyCount"] > 0:
            messages.append('WARNING - Loadbalancer %s has %s healthy instances out of %s instances' % (lb_name, lb_health["healthyCount"], lb_health["instanceCount"]))
            warningExit = True
        elif lb_health["unHealthyCount"] == 0:
            messages.append('OK - Loadbalancer %s has %s healthy instances out of %s instances' % (lb_name, lb_health["healthyCount"], lb_health["instanceCount"]))
            okExit = True
    else:
        print "CRITICAL - elb or alb not found"
        sys.exit(2)

    print "\n".join(messages)
    if criticalExit:
        sys.exit(2)
    elif warningExit:
        sys.exit(1)
    elif okExit:
        sys.exit(0)

    sys.exit(2)


def alb_exist(lb_name):
    try:
        response = albClient.describe_load_balancers(Names=[lb_name])
    except botocore.exceptions.ClientError as e:
        if 'LoadBalancerNotFound' in e.response['Error']['Code']:
            return False
    else:
        return True


def elb_exist(lb_name):
    try:
        response = elbClient.describe_load_balancers(LoadBalancerNames=[lb_name])
    except botocore.exceptions.ClientError as e:
        if 'LoadBalancerNotFound' in e.response['Error']['Code']:
            return False
    else:
        return True


def GetLbHealth(lb_name):
    healthyCount = 0
    unHealthyCount = 0
    instanceCount = 0
    targetGroupCount = 0
    targetGroups = {}
    data = {}

    if alb_exist(lb_name):
        alb_arn = albClient.describe_load_balancers(Names=[lb_name]).get('LoadBalancers', [])[0].get('LoadBalancerArn', [])
        for target_group in albClient.describe_target_groups(LoadBalancerArn=alb_arn)["TargetGroups"]:
            targetGroups[target_group["TargetGroupName"]] = {"healthyCount": 0, "unHealthyCount": 0, "instanceCount": 0}
            TargetGroupArn = target_group["TargetGroupArn"]
            for target_group_health in albClient.describe_target_health(TargetGroupArn=TargetGroupArn)["TargetHealthDescriptions"]:
                health = target_group_health["TargetHealth"]["State"]
                if health == "healthy":
                    healthyCount += 1
                    targetGroups[target_group["TargetGroupName"]]["healthyCount"] += 1
                elif health == "unhealthy":
                    unHealthyCount += 1
                    targetGroups[target_group["TargetGroupName"]]["unHealthyCount"] += 1
                instanceCount += 1
                targetGroups[target_group["TargetGroupName"]]["instanceCount"] += 1
            targetGroupCount += 1

        data["healthyCount"] = healthyCount
        data["unHealthyCount"] = unHealthyCount
        data["instanceCount"] = instanceCount
        data["lbName"] = lb_name
        data["targetGroups"] = targetGroups
        return data

    elif elb_exist(lb_name):
        elbHealth = elbClient.describe_instance_health(LoadBalancerName=lb_name).get("InstanceStates", [])
        for instanceHealth in elbHealth:
            health = instanceHealth["State"]
            if health == "InService":
                healthyCount += 1
            elif health == "OutOfService":
                unHealthyCount += 1
            instanceCount += 1

        data["healthyCount"] = healthyCount
        data["unHealthyCount"] = unHealthyCount
        data["instanceCount"] = instanceCount
        data["lbName"] = lb_name
        return data

    print "CRITICAL - elb or alb not found"
    sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
