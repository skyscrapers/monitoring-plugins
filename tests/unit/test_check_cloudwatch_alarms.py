from tests import mock, BaseTestCase
# from mock import Mock 
import boto3
import base64
# import placebo
# import types
import logging

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
        
    def test_get_alarm_filter_expression(self):
        class MockArgs:
            alarmFilterExpressionEncoded = None
            alarmFilterExpression = None
            def __init__(self, alarmFilterExpression, alarmFilterExpressionEncoded):
                self.alarmFilterExpression = alarmFilterExpression
                self.alarmFilterExpressionEncoded = alarmFilterExpressionEncoded
        expression = r'\bsky-cw\b | \bstaging\b'        
        exprEncoded = base64.b64encode(expression)
        # encoded: XGJza3ktY3dcYiB8IFxic3RhZ2luZ1xi
        args = MockArgs(None,exprEncoded)
        self.assertEquals(expression, check_cloudwatch_alarms.get_alarm_filter_expression(args))
        args = MockArgs(expression, None)
        self.assertEquals(expression, check_cloudwatch_alarms.get_alarm_filter_expression(args))
