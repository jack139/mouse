#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 实验员员鼠笼设置

url = ('/grp_user/house_info')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(house_id='')

        if user_data['house_id']=='':
            return render.info('参数错误！')  

        # 当前课题组的实验员列表
        group_list = helper.get_session_group_list()
        db_user=db.user.find({
            'privilege'  : helper.PRIV_USER, 
            'group_list' : '' if len(group_list)==0 else group_list[0],
        }).sort([('_id',1)])

        house_data = { 
            'house_id' : user_data['house_id'], 
            'status':0
        }

        db_obj=db.house.find_one({
            'house_id': user_data.house_id,
            'uname'   : helper.get_session_uname(),
        })
        if db_obj!=None:
            # 已存在的鼠笼
            house_data = db_obj

        # 此笼的小鼠信息
        db_mice = db.mouse.find({
            'house_id' : user_data['house_id'], 
            'status'   : {'$nin' : ['killed', 'dead']}
        }).sort([('_id',1)])

        mice = [i for i in db_mice]

        # 获取鼠笼数据
        house = []
        db_sku = db.house.find({
            'uname'    : helper.get_session_uname(), # 只显示当前用户管理的鼠笼
            # 要增加条件，现在过期的鼠笼
        }).sort([('house_id',1)])
        for i in db_sku:
            # 需要检查鼠笼类型的限制
            if i['house_id']!=user_data['house_id']:
                house.append(i['house_id'])

        return render.user_house_info(helper.get_session_uname(), helper.get_privilege_name(), 
            house_data, db_user, helper.HOUSE_TYPE, mice, helper.MOUSE_STATUS, house)

