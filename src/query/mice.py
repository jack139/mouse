#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 小鼠信息检索
# 管理员、实验员、教师均可使用，权限不同

url = ('/query/mice')

PAGE_SIZE = helper.PAGE_SIZE

#  -------------------
class handler:  
    def GET(self):
        user_priv = ''
        if helper.logged(helper.PRIV_USER, 'QUERY'):
            user_priv = 'user'
        elif helper.logged(helper.PRIV_GRP_ADMIN, 'QUERY'):
            user_priv = 'admin'
        elif helper.logged(helper.PRIV_TUTOR, 'QUERY'):
            user_priv = 'tutor'
        else:
            raise web.seeother('/')

        render = helper.create_render(globals={ 'str': str })
        user_data=web.input(page='0')

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        group_list = helper.get_session_group_list()
        # 实验员、管理员可查看的本实验组的小鼠
        # 教师可以查看所属组的小鼠

        # 分页获取数据
        db_sku = db.mouse.find({'group_id' : { '$in':group_list }},
            sort=[('status',-1),('_id', 1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        # 课题组名
        group_name = {'' : 'n/a'}
        r2 = db.groups.find({'group_id' : {'$in' : group_list}})
        for i in r2:
            group_name[i['group_id']] = i['name']


        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.query_mice(helper.get_session_uname(), helper.get_privilege_name(), 
            db_sku, range(0, num), group_name)
