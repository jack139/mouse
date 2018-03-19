#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 实验员管理

url = ('/grp_admin/user')


#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()

        group_list = helper.get_session_group_list()

        users=[]            
        db_user=db.user.find({
            'privilege'  : {'$in': [helper.PRIV_USER, helper.PRIV_TUTOR]}, 
            'group_list' : '' if len(group_list)==0 else group_list[0],
        }).sort([('_id',1)])
        if db_user.count()>0:
            for u in db_user:
                if u['uname']=='settings':
                    continue
                users.append([u['uname'],u['_id'],int(u['privilege']),
                    u['full_name'],u['login'],u['user_type'],u.get('credit_score',100)])
        
        return render.grpad_user(helper.get_session_uname(), helper.get_privilege_name(), users)

