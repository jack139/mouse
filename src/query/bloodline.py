#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 品系列表，实验员查看，不能修改

url = ('/query/bloodline')

PAGE_SIZE = 50   

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER|helper.PRIV_TUTOR, 'QUERY'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(page='0')

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        # 本组用户数据
        group_list = helper.get_session_group_list()
        #group_id = '' if len(group_list)==0 else group_list[0]

        group_name = {'n/a':'n/a'}
        r2 = db.groups.find({'status':1})
        for x in r2:
            group_name[x['group_id']]=x['name']


        # 分页获取数据
        db_sku = db.bloodline.find({'group_id' : {'$in' : group_list}}, 
            sort=[('_id', -1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        bloodline = []
        for x in db_sku:
            bloodline.append({
                'blood_code' : x['blood_code'],
                'name'       : x.get('name', ''),
                'status'     : x.get('status', 'n/a'),
                'group_id'   : group_name[x.get('group_id','n/a')],
                'note'       : x.get('note',''),
            })

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE

        return render.q_bloodline(helper.get_session_uname(), helper.get_privilege_name(), 
            bloodline, range(0, num), helper.BLOODLINE_STATUS)
