#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# 前端代码 公用变量及函数

import time, os, hashlib, base64
import urllib, urllib3, json
import functools
import re
import web
from config import setting

#---------------------------- 标记是否在测试／staging环境，用于区别生成环境的一些设置
IS_TEST = 'dev' in setting.app_host
IS_STAGING = 'dev' in setting.app_host
#----------------------------

if IS_TEST:
    from app_settings_test import * 
elif IS_STAGING:
    from app_settings_stag import * 
else:
    from app_settings import * 

db = setting.db_web

# 时间函数
ISOTIMEFORMAT=['%Y-%m-%d %X', '%Y-%m-%d', '%Y%m%d%H%M', '%Y-%m-%d %H:%M']

def time_str(t=None, format=0):
    return time.strftime(ISOTIMEFORMAT[format], time.localtime(t))

def validateEmail(email):
    if len(email) > 7:
      if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
          return 1
    return 0

RAND_BASE=[
    'abcdefghijklmnopqrstuvwxyz',
    '0123456789',
]

def my_crypt(codestr):
    return hashlib.sha1("sAlT139-"+codestr.encode('utf-8')).hexdigest()

def my_rand(n=4, base=0):
    import random
    return ''.join([random.choice(RAND_BASE[base]) for ch in range(n)])


