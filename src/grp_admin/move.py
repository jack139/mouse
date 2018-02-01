#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, json
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

#  管理移动指定小鼠，如果不是同一实验员，需要修改小鼠所有权

url = ('/grp_admin/move')

class handler:

    def POST(self):
        web.header("Content-Type", "application/json")
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            return json.dumps({'ret':-1,'msg':'无访问权限'})

        param = web.input(target_house_id='', mice='')

        if param.target_house_id=='' and param.mice=='':
            return json.dumps({'ret':-1, 'msg':'参数错误'})

        # 检查house_id
        db_obj=db.house.find_one({
            'house_id' : param.target_house_id,
            'group_id' : helper.get_session_group_list()[0],  # 只能移动自己实验组的鼠笼
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
            'house_id'    : db_obj['house_id'],
            'owner_uname' : db_obj.get('uname', ''),  # 设置小鼠所有人
            'last_tick'   : int(time.time()),  # 更新时间戳
        }})

        return json.dumps({'ret':0,'msg':'移动完成'})


