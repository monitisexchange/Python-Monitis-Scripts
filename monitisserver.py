#!/usr/bin/env python
# encoding: utf-8
"""
MonitisServer.py

Created by Jeremiah Shirk on 2011-06-13.
Copyright (c) 2011 Monitis. All rights reserved.
"""

import sys
import os
import unittest
import urllib2
from elementtree.ElementTree import ElementTree # not in the standard library
import StringIO
import hashlib
import hmac
import base64

class MonitisServer():
    def __init__(self, apiKey, apiSecret, 
                 url='http://monitis.com/customMonitorApi',
                 output='xml',version='2'):
        self.url = url
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.output = output
        self.version = version
            
    def requestMonitorId(self,monitorTag):
        req = urllib2.Request(str('{0}/?apikey={1}&output={2}'+\
                                  '&version={3}&action=getMonitors&tag={4}')\
            .format(self.url,self.apiKey,self.output,self.version,monitorTag))
        res = urllib2.urlopen(req)
        xml = res.read()
        root = ElementTree(file=StringIO.StringIO(xml)).getroot()
        return root.find('./monitor/id').text
    
    def listMonitors(self):
        ret = list()
        req = urllib2.Request(str('{0}/?apikey={1}&output={2}'+\
                                  '&version={3}&action=getMonitors')\
            .format(self.url,self.apiKey,self.output,self.version))
        res = urllib2.urlopen(req)
        xml = res.read()
        root = ElementTree(file=StringIO.StringIO(xml)).getroot()
        for monitor in list(root):
            ret.append((monitor.find('id').text,monitor.find('tag').text,
                   monitor.find('name').text))
        return ret        
    
    def checkSum(self, **kwargs):
        args = kwargs.items()
        args.sort()
        checksumStr = ''
         # sort on the key, concatenate the keys and values,
         # and base64 the SHA1 HMAC of that
        for key,value in args:
            checksumStr += key
            checksumStr +=value
        return base64.b64encode(str(hmac.new(self.apiSecret,checksumStr,
                                             hashlib.sha1).digest()))
    
    def formatCurlPostData(self, **kwargs):
        args = kwargs.items()
        args.sort()
        postArgs = ''
        for key,value in args:
            postArgs += '--data-urlencode "{k}={v}" '.format(k=key,v=value)
        return postArgs.rstrip()
    
    def timestamp(self):
        return os.popen('date -u +"%F %T"').read().rstrip()
        
    def checktime(self):
        return os.popen('date -u +"%s"000').read().rstrip()
    
    def monitisPost(self,postArgs):
        # API key, version, etc. will be the same across all calls
        postArgs['apikey'] = self.apiKey
        postArgs['version'] = self.version
        postArgs['timestamp'] = self.timestamp()
        
        # calculate a checksum based on the values and secret key
        checkSum=self.checkSum(**postArgs)
        
        # use curl to post the values, including the calculated checksum
        postArgs['checksum'] = checkSum
        postData = self.formatCurlPostData(**postArgs)

        curlCmd = "curl -s " + postData + " " + self.url
        return os.popen(curlCmd).read().rstrip()

    def addMonitor(self,name=None,resultParams=None,tag=None):
        postArgs = {'action':'addMonitor',
                    'apikey':self.apiKey,
                    'name':name,
                    'resultParams':resultParams,
                    'tag':tag}
        return self.monitisPost(postArgs)

    def deleteMonitor(self,monitorTag=None,monitorId=None):
        if monitorId is None:
            monitorId = self.requestMonitorId(monitorTag)
        postArgs = {'action':'deleteMonitor',
                    'monitorId':monitorId}
        return self.monitisPost(postArgs)
        
    # use local curl for the UserAgent
    def addResult(self, monitorId=None, monitorTag=None,
                  result=None, checkTime=None):
        action = 'addResult'
        # time stamp always set to time metric is sent to monitis
        timeStamp = self.timestamp()
        
        # set a checkTime to now if none was provided
        if checkTime is None:
            checkTime = self.checktime()
        
        # if no monitorId was given, retrieve it based on the monitorTag
        monitorId = self.requestMonitorId(monitorTag)
        
        # arguments for the post to monitis
        postArgs = {'version':self.version,'action':action,
                    'apikey':self.apiKey,'checktime':checkTime,
                    'monitorId':monitorId,'results':result}

        return self.monitisPost(postArgs)

class MonitisServerTests(unittest.TestCase):
    def setUp(self):
        self.monitis = MonitisServer(None,"notReallyASecret")
    
    def testCheckSum(self):
        self.assertEquals(self.monitis.checkSum(key2="foo",key1="bar"),
                          "ML1TdJ/wQc06CdIREtddB19wsKM=")
    

if __name__ == '__main__':
    unittest.main()