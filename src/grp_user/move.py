#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, json
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

#  淘汰鼠笼所有小鼠

url = ('/grp_user/move')

class handler:

    def POST(self):
        web.header("Content-Type", "application/json")
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            return json.dumps({'ret':-1,'msg':'无访问权限'})

        param = web.input(target_house_id='', mice='')

        if param.target_house_id=='' and param.mice=='':
            return json.dumps({'ret':-1, 'msg':'参数错误'})

        # 检查house_id
        db_obj=db.house.find_one({
            'house_id': param.target_house_id,
            'uname'   : helper.get_session_uname(),  # 只能淘汰自己的鼠笼
        })
        if db_obj==None:
            # 不存在的鼠笼
            return json.dumps({'ret':-2, 'msg':'鼠笼参数错误！'})

        mice=json.loads(param.mice)

        mice2 = [ObjectId(i) for i in mice]

        # 移动小鼠
        db_mice = db.mouse.update_many({
            '_id' : {'$in' : mice2}, 
        }, {'$set':{'house_id':param.target_house_id}})

        return json.dumps({'ret':0,'msg':'移动完成'})


