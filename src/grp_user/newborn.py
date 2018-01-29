#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, json
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

#  新生小鼠

url = ('/grp_user/newborn')

class handler:

    def POST(self):
        web.header("Content-Type", "application/json")
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            return json.dumps({'ret':-1,'msg':'无访问权限'})

        param = web.input(house_id='', num='')

        if param.house_id=='' or param.num=='':
            return json.dumps({'ret':-1, 'msg':'参数错误'})

        if not param.num.isdigit():
            return json.dumps({'ret':-3, 'msg':'num参数错误'})

        # 检查house_id
        db_obj=db.house.find_one({
            'house_id': param.house_id,
            'uname'   : helper.get_session_uname(),  # 只能管理自己的鼠笼
        })
        if db_obj==None:
            # 不存在的鼠笼
            return json.dumps({'ret':-2, 'msg':'鼠笼参数错误！'})

        if db_obj['type']!='breed':
            return json.dumps({'ret':-4, 'msg':'不是繁殖笼！'})

        # 找到父本和母本
        r2 = db.mouse.find({'house_id' : param.house_id}, sort=[('birth_d', 1)])
        if (r2 is None) or (r2.count()<2):
            # 数量不足
            return json.dumps({'ret':-5, 'msg':'未找到父本和母本！'})

        print r2[0]

        if r2[0]['sex']=='F' and r2[1]['sex']=='M':
            father = r2[1]
            mother = r2[0]
        elif r2[0]['sex']=='M' and r2[1]['sex']=='F':
            father = r2[0]
            mother = r2[1]
        else: # 性别不对
            return json.dumps({'ret':-6, 'msg':'未找到父本或母本！'})


        # 假设添加日期为出生日期， 应该需要可以输入
        birth_d = time.strftime("%Y%m%d", time.localtime()) # 格式 yyyymmdd
        divide_d = time.strftime("%Y%m%d", time.localtime(time.time()+3600*24*8)) # 格式 yyyymmdd,, 8天分笼

        for i in xrange(int(param.num)):
            update_set={
                'tag'        : '',
                'father_tag' : father['tag'],
                'mother_tag' : mother['tag'],
                'birth_d'    : birth_d,
                'divide_d'   : divide_d,
                'blood_code' : '',
                'gene_code'  : '',
                'note'       : '',
                'house_id'   : param.house_id,
                'sex'        : '',
                'status'     : 'live', # 正常
                'last_tick'  : int(time.time()),  # 更新时间戳
                'owner_uname' : helper.get_session_uname(),
                'group_id'    : helper.get_session_group_list()[0],
            }
            db_mice = db.mouse.insert_one(update_set)

        return json.dumps({'ret':0,'msg':'添加小鼠完成'})

