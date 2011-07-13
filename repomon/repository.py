#!/usr/bin/env python
# encoding: utf-8
"""
repomon/repository.py

Created by Jeremiah Shirk on 2011-07-12.
Copyright (c) 2011 Monitis. All rights reserved.
"""

import sys
import getopt
import repomon
from git import *

class Repository():
    def __init__(self, path):
        self.path = path
        
class GitRepository(Repository):
    def __init__(self, path):
        self.path = path
        self.repo = Repo(self.path)
        print self.repo.index.diff(None)



