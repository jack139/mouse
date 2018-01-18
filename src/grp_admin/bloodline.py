#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 鼠笼列表

url = ('/grp_admin/bloodline')

PAGE_SIZE = 50   

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(page='0')

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  


        # 本组用户数据
        group_list = helper.get_session_group_list()
        group_id = '' if len(group_list)==0 else group_list[0]

        # 分页获取数据
        db_sku = db.bloodline.find({'group_id' : group_id},
            sort=[('_id', -1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE

        return render.grpad_bloodline(helper.get_session_uname(), helper.get_privilege_name(), 
            db_sku, range(0, num), helper.BLOODLINE_STATUS)
