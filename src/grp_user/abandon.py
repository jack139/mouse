#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, json
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

#  淘汰鼠笼指定的小鼠

url = ('/grp_user/abandon')

class handler:

    def POST(self):
        web.header("Content-Type", "application/json")
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            return json.dumps({'ret':-1,'msg':'无访问权限'})

        user_data = web.input(house_id='', mice='')

        if user_data['house_id']=='' and user_data.mice=='':
            return json.dumps({'ret':-1, 'msg':'参数错误'})

        # 检查house_id
        db_obj=db.house.find_one({
            'house_id': user_data.house_id,
            'uname'   : helper.get_session_uname(),  # 只能淘汰自己的鼠笼
        })
        if db_obj==None:
            # 不存在的鼠笼
            return json.dumps({'ret':-2, 'msg':'鼠笼参数错误！'})


        # 此笼的小鼠杀死
        mice=json.loads(user_data.mice)
        mice_id = [ObjectId(i) for i in mice]

        db_mice = db.mouse.update_many({
            '_id'      : {'$in' : mice_id},
            'house_id' : user_data['house_id'], 
            'status'   : {'$nin' : ['killed', 'dead']}
        }, {'$set':{'status':'dead'}})

        return json.dumps({'ret':0,'msg':'小鼠已淘汰！'})


