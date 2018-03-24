#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 试验组内公告修改

url = ('/grp_admin/news_edit')


#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()

        user_data=web.input()

        # 课题组id取自session, 2017-12-12
        group_list = helper.get_session_group_list()
        group_id = '' if len(group_list)==0 else group_list[0]

        r2 = db.groups.find_one({'group_id' : group_id})
        if r2 is None:
            return render.info('课题组错误！')  

        return render.grpad_news_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            r2.get('news',''))


    def POST(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()

        user_data=web.input(news='')

        # 课题组id取自session, 2017-12-12
        group_list = helper.get_session_group_list()
        group_id = '' if len(group_list)==0 else group_list[0]

        db.groups.update_one({'group_id' : group_id}, 
            {'$set' : {'news' : user_data['news']}})

        return render.info('成功保存！','/grp_admin/news_edit')
