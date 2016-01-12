#!/usr/bin/env python

# Written by juancarlos@skyscrape.rs
# 2016-01-06

import boto3

s3 = boto3.resource('s3')

#for bucket in s3.buckets.all():
#        print(bucket.name)