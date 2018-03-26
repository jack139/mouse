#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 实验员添加品系备注

url = ('/grp_user/bloodline_comment')


#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')

        render = helper.create_render()

        user_data=web.input(blood_id='')

        r2 = db.bloodline.find_one({'_id':ObjectId(user_data.blood_id)})
        if r2 is None:
            return render.info('品系id错误！')  

        if helper.get_session_uname() not in r2['user_list']:
            return render.info('无权添加此品系备注！')  

        return render.user_bloodline_comment(helper.get_session_uname(), helper.get_privilege_name(), 
            user_data.blood_id, r2.get('user_comment',{}).get(helper.get_session_uname(),'') )


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')

        render = helper.create_render()

        user_data=web.input(blood_id='', user_comment='')

        r2 = db.bloodline.find_one({'_id':ObjectId(user_data.blood_id)})
        if r2 is None:
            return render.info('品系id错误！')  

        if helper.get_session_uname() not in r2['user_list']:
            return render.info('无权添加此品系备注！')  

        user_comment = r2.get('user_comment',{})
        user_comment[helper.get_session_uname()] = user_data.user_comment

        db.bloodline.update_one({'_id':ObjectId(user_data.blood_id)}, 
            {'$set' : {'user_comment' : user_comment}})

        return render.info('成功保存！','/grp_user/bloodline_comment?blood_id=%s'%user_data.blood_id)
