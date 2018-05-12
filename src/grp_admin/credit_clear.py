#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 实验员评分清零

url = ('/grp_admin/credit_clear')


#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()

        #user_data=web.input(uid='')

        # 课题组id取自session, 2017-12-12
        group_list = helper.get_session_group_list()
        group_id = '' if len(group_list)==0 else group_list[0]

        db.user.update_many({'group_list' : group_id}, {'$set' : {'credit_score' : 100}})

        return render.info('评分已清零！','/grp_admin/user')

