#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 笼架列表

url = ('/grp_admin/shelf')

PAGE_SIZE = helper.PAGE_SIZE

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(page='0', v_shelf='')

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        # 获取课题组名字对照
        r3 = db.groups.find({'status':1})
        group_name = {'n/a':'n/a'}
        for i in r3:
            group_name[i['group_id']]=i['name']

        group_list = helper.get_session_group_list()

        v_shelf = user_data.v_shelf.strip()

        # 分页获取数据
        conditions = {
            'group_id' : '' if len(group_list)==0 else group_list[0]
        }

        if v_shelf!='':
            #conditions['shelf_id'] = v_shelf
            conditions['shelf_id'] = { '$regex' : u'%s.*'%v_shelf, '$options' : 'i' }

        db_sku = db.shelf.find(conditions,
            sort=[('shelf_id', 1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.grpad_shelf(helper.get_session_uname(), helper.get_privilege_name(), 
            db_sku, range(0, num), group_name)
