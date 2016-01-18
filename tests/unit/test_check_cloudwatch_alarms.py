from tests import mock, BaseTestCase
# from mock import Mock 
import boto3
# import placebo
# import types
# import logging

import check_cloudwatch_alarms	

class TestCheckCloudWatchAlarms(BaseTestCase):

    OK=0
    WARNING=1
    CRITICAL=2
    UNKNOWN=3



    def test_filter_alarms(self):
        class MockAlarm:
            def __init__(self, name):
                self.name = name
        filter1 = r'\bsky-cw\b | \bstaging\b'
        alarms = [MockAlarm('sky-cw-addapp-ecs-staging-01')]
        self.assertEquals(1, len(check_cloudwatch_alarms.filter_alarms(alarms)))
        self.assertEquals(1, len(check_cloudwatch_alarms.filter_alarms(alarms, filter1)))
        alarms.append(MockAlarm('other-cw-addapp-ecs-staging-01'))
        self.assertEquals(1, len(check_cloudwatch_alarms.filter_alarms(alarms, filter1)))
        alarms.append(MockAlarm('sky-cw-text-addapp-ecs-staging-02'))
        self.assertEquals(2, len(check_cloudwatch_alarms.filter_alarms(alarms, filter1)))
        
    def test_check_status(self):
        
        alarms = [ ]
        cloudwatch = boto3.resource('cloudwatch')
        alarm = cloudwatch.Alarm('name')
        alarms.append(alarm)
        self.assertEquals(check_cloudwatch_alarms.CRITICAL, check_cloudwatch_alarms.check_status(alarms,"ERROR"))
        self.assertEquals(check_cloudwatch_alarms.WARNING, check_cloudwatch_alarms.check_status(alarms,"ERROR",True))

        self.assertEquals(check_cloudwatch_alarms.WARNING, check_cloudwatch_alarms.check_status(alarms,"OK"))
        alarms = [ ]
        self.assertEquals(check_cloudwatch_alarms.OK, check_cloudwatch_alarms.check_status(alarms,"ERROR"))

	