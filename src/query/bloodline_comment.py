#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
#from libs import pos_func
import helper

db = setting.db_web

# 小鼠品系实验说明汇总

url = ('/query/bloodline_comment')

def bloodline_trans(v):  # a,b(+/-),c(+/-) ==> a,b,c
    a = v.split(',')
    b = []
    for x in a:
        b.append(x.split('(')[0])
    return ','.join(b)

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER|helper.PRIV_GRP_ADMIN|helper.PRIV_TUTOR, 'QUERY'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(blood_id='')

        r2 = db.bloodline.find_one({'_id':ObjectId(user_data.blood_id)})
        if r2 is None:
            return render.info('品系id错误！')  

        comment_list = {}

        for user in r2['user_list']: # 在使用该品系的用户里汇总
            house_list = []
            # 小鼠数据
            r3 = db.mouse.find({
                'owner_uname' : user,
                'status'      : {'$nin' : ['killed', 'dead']} # 只查活着的小鼠
            })
            for mouse in r3:
                if bloodline_trans(mouse['blood_code'])==r2['blood_code']: # 品系名和基因名相同的
                    house_list.append(mouse['house_id'])

            comment_list[user] = {
                'mouse_num'  : len(house_list),
                'house_list' : list(set(house_list)),
                'comment'    : r2.get('user_comment',{}).get(user,''),
            }

        return render.query_bloodline_comment(helper.get_session_uname(), helper.get_privilege_name(), 
            r2, comment_list)


    