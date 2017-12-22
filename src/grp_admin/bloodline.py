#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 鼠笼列表

url = ('/grp_admin/bloodline')


#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input()

        # 获取品系数据
        db_sku = db.bloodline.find()
        
        return render.grpad_bloodline(helper.get_session_uname(), helper.get_privilege_name(), db_sku)
