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
import urllib
import urllib2
from elementtree.ElementTree import ElementTree # not in the standard library
import StringIO
import hashlib
import hmac
import base64
import datetime

class MonitisServer():
    def __init__(self, apiKey, apiSecret, 
                 url='http://monitis.com/customMonitorApi',
                 output='xml',version='2'):
        self.url = url
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.output = output
        self.version = version
            
    def _apiRequestXml(self,apiStr):
        xml = None
        req = urllib2.Request(apiStr)
        try:
            res = urllib2.urlopen(req)
            xml = res.read()
        except urllib2.HTTPError, error:
            msg = error.read()
            raise Exception("API Error: " + msg)
        return xml

    def requestMonitorId(self,monitorTag):
        xml = self._apiRequestXml(str('{0}/?apikey={1}&output={2}'+\
                                  '&version={3}&action=getMonitors&tag={4}')\
            .format(self.url,self.apiKey,self.output,self.version,monitorTag))
        print xml
        root = ElementTree(file=StringIO.StringIO(xml)).getroot()
        monitor = root.find('./monitor/id') # Just the first matching monitor
        # TODO handle multiple monitors with the same tag
        # Dependent code assumes that exactly one is returned
        if monitor is None:
            raise Exception("No monitors matching " + monitorTag)
        return root.find('./monitor/id').text
    
    def dictMonitors(self):
        ret = {}
        req = urllib2.Request(str('{0}/?apikey={1}&output={2}'+\
                                  '&version={3}&action=getMonitors')\
            .format(self.url,self.apiKey,self.output,self.version))
        res = urllib2.urlopen(req)
        xml = res.read()
        root = ElementTree(file=StringIO.StringIO(xml)).getroot()
        for monitor in list(root):
            ret[monitor.find('name').text] = \
            monitor.find('id').text,monitor.find('tag').text
        return ret
    
    def listMonitors(self):
        ret = list()
        xml = self._apiRequestXml(str('{0}/?apikey={1}&output={2}'+\
                                      '&version={3}&action=getMonitors')\
            .format(self.url,self.apiKey,self.output,self.version))
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

    def timestamp(self):
        return datetime.datetime.utcnow().strftime("%F %T")
    
    def checktime(self):
        return datetime.datetime.utcnow().strftime("%s") + "000"
    
    def monitisPost(self,postArgs):
        # API key, version, etc. will be the same across all calls
        postArgs['apikey'] = self.apiKey
        postArgs['version'] = self.version
        postArgs['timestamp'] = self.timestamp()
        
        # calculate a checksum based on the values and secret key
        checkSum=self.checkSum(**postArgs)
        
        # use urllib to post the values
        postArgs['checksum'] = checkSum
        params = urllib.urlencode(postArgs)
        try:
            result = urllib2.urlopen(self.url,params)
        except urllib2.HTTPError, error:
            msg = error.read()
            raise Exception("API Error: " + msg) 
        ret = result.read()
        result.close()
        return ret
    
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
        if monitorId is None:
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
