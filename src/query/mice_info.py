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

url = ('/query/mice_info')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER|helper.PRIV_GRP_ADMIN|helper.PRIV_TUTOR, 'QUERY'):
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

        # 品系信息
        db_blood = db.bloodline.find({
            'user_list' : helper.get_session_uname(),
        })

        return render.query_mice_info(helper.get_session_uname(), helper.get_privilege_name(), 
            mouse_data, db_blood)


    