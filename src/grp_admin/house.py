#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 鼠笼列表

url = ('/grp_admin/house')


#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(shelf_id='')

        if user_data['shelf_id']=='':
            return render.info('参数错误！')  

        # 获取笼架信息
        db_shelf = db.shelf.find_one({'shelf_id' : user_data['shelf_id']})
        if db_shelf is None:
            return render.info('笼架号错误！')  

        # 获取鼠笼数据
        houses = [{}]*(db_shelf['col'] * db_shelf['row']) # house_id 均从1开始计算
        db_sku = db.house.find({'shelf_id' : user_data['shelf_id']})
        for i in db_sku:
            _,_,_,r,c = i['house_id'].split('-') # 获取鼠笼位置
            houses[(int(r)-1)*db_shelf['col']+(int(c)-1)] = i
        
        now_day = helper.time_str(format=2)

        return render.grpad_house(helper.get_session_uname(), helper.get_privilege_name(), 
            houses, db_shelf, now_day)
