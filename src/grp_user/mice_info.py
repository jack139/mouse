#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
#from libs import pos_func
import helper

db = setting.db_web

# 小鼠信息编辑

url = ('/grp_user/mice_info')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(mouse_id='')

        # 小鼠数据
        mouse_data = {'_id':'n/a'}

        if user_data.mouse_id != '': 
            db_obj=db.mouse.find_one({'_id':ObjectId(user_data.mouse_id)})
            if db_obj!=None:
                # 已存在的obj
                mouse_data = db_obj

        # 获取鼠笼数据
        house = []
        db_sku = db.house.find({
            'uname'    : helper.get_session_uname(), # 只显示当前用户管理的鼠笼
            # 要增加条件，现在过期的鼠笼
        }).sort([('house_id',1)])
        for i in db_sku:
            # 需要检查鼠笼类型的限制
            house.append(i['house_id'])

        # 品系信息
        db_blood = db.bloodline.find({
            'user_list' : helper.get_session_uname(),
        })

        return render.user_mice_info(helper.get_session_uname(), helper.get_privilege_name(), 
            mouse_data, house, db_blood)


    