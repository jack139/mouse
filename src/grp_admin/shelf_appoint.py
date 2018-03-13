#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, re
from bson.objectid import ObjectId
from config import setting
#from libs import pos_func
import helper

db = setting.db_web

# 品系信息编辑

url = ('/grp_admin/shelf_appoint')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(shelf_id='')


        db_obj=db.shelf.find_one({'_id':ObjectId(user_data.shelf_id)})
        if db_obj is None:
            # 已存在的obj
            return render.info('笼架不存在！')  

        # 本组用户数据
        group_list = helper.get_session_group_list()

        users=[]            
        db_user=db.user.find({
            'privilege'  : helper.PRIV_USER, 
            'group_list' : '' if len(group_list)==0 else group_list[0],
        }).sort([('_id',1)])

        return render.grpad_shelf_appoint(helper.get_session_uname(), helper.get_privilege_name(), 
            db_obj, [x for x in db_user])


    def POST(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(shelf_id='',user_list=[], shelf_id_id='')


        db.shelf.update_one({'_id':ObjectId(user_data['shelf_id'])}, {
            '$set'  : {'appoint' : user_data['user_list']},
            '$push' : {
                'history' : (helper.time_str(), helper.get_session_uname(), '修改预分配实验员'), 
            }  # 纪录操作历史
        })

        return render.info('成功保存！', '/grp_admin/house?shelf_id='+user_data['shelf_id_id'])
