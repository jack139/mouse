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
        print param

        if param.target_house_id=='' and param.mice=='':
            return json.dumps({'ret':-1, 'msg':'参数错误'})

        mice=json.loads(param.mice)

        mice2 = [ObjectId(i) for i in mice]

        if len(mice2)>helper.MAX_MOUSE_NUM: # 此处加限制，防止用过多老鼠出错的方式，抢占预分配的鼠笼
            return json.dumps({'ret':-4, 'msg':'小鼠太多，目标鼠笼容纳不下！'})

        # 检查house_id
        db_obj=db.house.find_one({
            'house_id': param.target_house_id,
            #'uname'   : helper.get_session_uname(),  # 只能移动自己的鼠笼
        })

        while 1: # 死循环，方便程序结构，无他用
            # 自己的鼠笼，可以移动
            if db_obj and db_obj['uname']==helper.get_session_uname():
                if db_obj['expired_d']<helper.time_str(format=2):
                    return json.dumps({'ret':-4, 'msg':'不能移动到已过期的鼠笼！'})
                break

            # 其他人的鼠笼， 不能移动
            if db_obj and db_obj['uname']!='':
                return json.dumps({'ret':-2, 'msg':'鼠笼已被使用，只能移动自己的鼠笼！'})

            # 不存在的鼠笼，或者无主的鼠笼
            #if db_obj==None or db_obj['uname']==''：
            
            # 检查是否是预分配的鼠笼
            shelf_id = '-'.join(param.target_house_id.split('-')[:3])
            r3 = db.shelf.find_one({'shelf_id':shelf_id})
            if r3 and (helper.get_session_uname() in r3.get('appoint',[])): # 是否是预分配的笼架

                if r3['appoint_expired_d']<helper.time_str(format=2):
                    return json.dumps({'ret':-5, 'msg':'不能移动到已过期的预分配鼠笼！'})

                group_list = helper.get_session_group_list()
                group_id = '' if len(group_list)==0 else group_list[0]

                # 自动更新鼠笼信息
                update_set={
                    'house_id'  : param.target_house_id,
                    'shelf_id'  : shelf_id,
                    'type_list' : r3['appoint_type_list'],
                    'status'    : 1,
                    'uname'     : helper.get_session_uname(),
                    'group_id'  : group_id,
                    'expired_d' : r3['appoint_expired_d'],
                    'last_tick' : int(time.time()),  # 更新时间戳
                }

                db.house.update_one({'house_id':param.target_house_id}, {
                    '$set'  : update_set,
                    '$push' : {
                        'history' : (helper.time_str(), helper.get_session_uname(), '修改'), 
                    }  # 纪录操作历史
                }, upsert=True)

            else:
                return json.dumps({'ret':-6, 'msg':'只能移动自己的鼠笼！'})

            break


        # 检查鼠笼是否超出最大数量
        r2=db.mouse.find({
            'house_id' : param.target_house_id,
            'status'   : {'$nin' : ['killed', 'dead']},
        })

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


