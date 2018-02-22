#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, json
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

#  移动指定小鼠

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
            'uname'   : helper.get_session_uname(),  # 只能移动自己的鼠笼
        })
        if db_obj==None:
            # 不存在的鼠笼
            return json.dumps({'ret':-2, 'msg':'鼠笼参数错误！'})

        mice=json.loads(param.mice)

        mice2 = [ObjectId(i) for i in mice]

        # 检查鼠笼是否超出最大数量
        r2=db.mouse.find({'house_id': param.target_house_id})

        if r2.count()+len(mice2)>helper.MAX_MOUSE_NUM:
            return json.dumps({'ret':-3, 'msg':'目标鼠笼容纳不下！'})

        # 移动小鼠
        db_mice = db.mouse.update_many({
            '_id' : {'$in' : mice2}, 
        }, {'$set':{
            'house_id'  : param.target_house_id,
            'last_tick' : int(time.time()),  # 更新时间戳
        }})

        # 设置分笼时间
        db.mouse.update_many({
            '_id'       : { '$in' : mice2 },
            'divide2_d' : { '$exists' : False } 
        }, {'$set':{
            'divide2_d'  : helper.time_str(format=2),
        }})
        return json.dumps({'ret':0,'msg':'移动完成'})


