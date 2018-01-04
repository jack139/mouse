#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, json
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

#  结束鼠笼实验

url = ('/grp_user/finish')

class handler:

    def POST(self):
        web.header("Content-Type", "application/json")
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            return json.dumps({'ret':-1,'msg':'无访问权限'})

        param = web.input(house_id='')

        if param.house_id=='':
            return json.dumps({'ret':-1, 'msg':'参数错误'})

        # 检查house_id
        db_obj=db.house.find_one({
            'house_id': param.house_id,
            'uname'   : helper.get_session_uname(),  # 只能设置自己的鼠笼
        })
        if db_obj==None:
            # 不存在的鼠笼
            return json.dumps({'ret':-2, 'msg':'鼠笼参数错误！'})

        if db_obj['type']!='test':
            return json.dumps({'ret':-3, 'msg':'此鼠笼不是实验笼！'})

        db.house.update_one({'house_id': param.house_id},
            {'$set':{
                'type'       : 'inuse',
                'test_end_d' : time.strftime("%Y%m%d", time.localtime()), # 格式 yyyymmdd
            }}
        )

        return json.dumps({'ret':0,'msg':'结束实验完成'})


