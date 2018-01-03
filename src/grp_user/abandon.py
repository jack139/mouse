#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

#  淘汰鼠笼所有小鼠

url = ('/grp_user/abandon')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(house_id='')

        if user_data['house_id']=='':
            return render.info('参数错误！')  

        # 检查house_id
        db_obj=db.house.find_one({
            'house_id': user_data.house_id,
            'uname'   : helper.get_session_uname(),  # 只能淘汰自己的鼠笼
        })
        if db_obj==None:
            # 不存在的鼠笼
            return render.info('鼠笼参数错误！')

        # 此笼的小鼠杀死
        db_mice = db.mouse.update_many({
            'house_id' : user_data['house_id'], 
            'status'   : {'$nin' : ['killed', 'dead']}
        }, {'$set':{'status':'dead'}})

        return render.info('此笼的小鼠已全部淘汰！', '/grp_user/house_info?house_id=%s'%user_data['house_id'])


