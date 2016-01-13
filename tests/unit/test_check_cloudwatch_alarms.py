from tests import mock, BaseTestCase
# from mock import Mock 
import boto3
# import placebo
# import types
# import logging

from skymonitoringplugins import check_cloudwatch_alarms
# from awscli.testutils import mock

class TestCheckCloudWatchAlarms(BaseTestCase):

    OK=0
    WARNING=1
    CRITICAL=2
    UNKNOWN=3
#    def filter_1(StateValue):
#        name = 'name'
#        filterResult = []
#        filterResult.append({name: "testName", "city": "San Francisco"})
#        return filterResult
 
#    def test_tmp1(self):
#        def test_func(): print 'wow'
#        dynf = types.FunctionType(test_func.func_code, {})
#        dynf()
    class Object(object):
        pass
    
        
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
