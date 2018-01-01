#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 实验员小鼠列表

url = ('/grp_user/mice')

PAGE_SIZE = 50   

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(page='0')

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        # 当前实验员可查看的小鼠
        # 分页获取数据
        db_sku = db.mouse.find({'uname' : helper.get_session_uname()},
            sort=[('_id', 1),('status',-1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.user_mice(helper.get_session_uname(), helper.get_privilege_name(), 
            db_sku, range(0, num))
