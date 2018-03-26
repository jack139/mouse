#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 组管理员鼠笼设置

url = ('/grp_admin/house_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(house_id='')

        if user_data['house_id']=='':
            return render.info('参数错误！')  

        # 当前课题组的实验员列表
        group_list = helper.get_session_group_list()
        db_user=db.user.find({
            'privilege'  : helper.PRIV_USER, 
            'group_list' : '' if len(group_list)==0 else group_list[0],
        }).sort([('_id',1)])

        house_data = { 
            'house_id' : user_data['house_id'], 
            'status':0
        }

        db_obj=db.house.find_one({'house_id':user_data.house_id})
        if db_obj!=None:
            # 已存在的鼠笼
            house_data = db_obj

        # 此笼的小鼠信息
        db_mice = db.mouse.find({
            'house_id' : user_data['house_id'], 
            'status'   : {'$nin' : ['killed', 'dead']}
        }).sort([('_id',1)])


        return render.grpad_house_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            house_data, db_user, helper.HOUSE_TYPE, db_mice.count())


    def POST(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(house_id='',uname='',expired_d='',status='',type=[])

        if user_data.house_id.strip()=='':
            return render.info('参数错误！')

        if int(user_data.status)==1:
            if user_data.uname=='':
                return render.info('请设置实验员！')

            if user_data.type==[]:
                return render.info('请设置鼠笼可用类型！')

            if user_data.expired_d=='':
                return render.info('请设置鼠笼到期日期！')

        shelf_id = u'-'.join(user_data['house_id'].split('-')[:3])

        group_id = helper.get_session_group_list()[0]


        # 检查鼠笼过期时间不能超过笼架过期时间
        r2 = db.shelf.find_one({'shelf_id':shelf_id})
        if r2['group_id']!=group_id:
            return render.info('鼠笼所在笼架不属于本课题组！')
        if r2['expired_d']<user_data['expired_d']:
            return render.info('鼠笼过期时间不能超过所在笼架过期时间！')

        try:
            update_set={
                'house_id'  : user_data['house_id'],
                'shelf_id'  : shelf_id,
                'type_list' : user_data['type'],
                'status'    : int(user_data['status']),
                'uname'     : user_data['uname'],
                'group_id'  : group_id,
                'expired_d' : user_data['expired_d'],
                'last_tick' : int(time.time()),  # 更新时间戳
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        db.house.update_one({'house_id':user_data['house_id']}, {
            '$set'  : update_set,
            '$push' : {
                'history' : (helper.time_str(), helper.get_session_uname(), '修改'), 
            }  # 纪录操作历史
        }, upsert=True)

        return render.info('成功保存！', '/grp_admin/house_info?house_id=%s' % user_data['house_id'])
