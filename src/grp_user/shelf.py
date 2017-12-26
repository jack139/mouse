#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 实验员笼架列表

url = ('/grp_user/shelf')

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

        # 获取课题组名字对照
        r3 = db.groups.find({'status':1})
        group_name = {'n/a':'n/a'}
        for i in r3:
            group_name[i['group_id']]=i['name']

        # 当前实验员可用的笼架
        r2 = db.house.distinct("shelf_id", {'uname':helper.get_session_uname()})

        # 分页获取数据
        db_sku = db.shelf.find({'shelf_id' : {'$in':r2}},
            sort=[('shelf_id', 1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.user_shelf(helper.get_session_uname(), helper.get_privilege_name(), 
            db_sku, range(0, num), group_name)
