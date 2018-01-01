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

# 小鼠信息编辑

url = ('/grp_user/mice_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(mouse_id='')

        # 小鼠数据
        mouse_data = {'_id':'n/a'}

        if user_data.mouse_id != '': 
            db_obj=db.mouse.find_one({'_id':ObjectId(user_data.mouse_id)})
            if db_obj!=None:
                # 已存在的obj
                mouse_data = db_obj

        # 获取鼠笼数据
        house = []
        db_sku = db.house.find({
            'uname'    : helper.get_session_uname(), # 只显示当前用户管理的鼠笼
            # 要增加条件，现在过期的鼠笼
        }).sort([('house_id',1)])
        for i in db_sku:
            houses.append(i['house_id'])

        # 品系信息
        db_blood = db.bloodline.find({
            'user_list' : helper.get_session_uname(),
        })

        return render.user_mice_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            mouse_data, house, db_blood)


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(blood_id='',blood_code='',name='',user_list=[])

        if user_data.name.strip()=='':
            return render.info('品系名不能为空！')  

        blood_code = user_data['blood_code'].strip()

        try:
            update_set={
                'blood_code'  : blood_code,
                'name'        : user_data['name'],
                'status'      : user_data['status'],
                'note'        : user_data['note'],
                'user_list'   : user_data['user_list'],
                'last_tick'   : int(time.time()),  # 更新时间戳
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        if user_data['blood_id']=='n/a': # 新建
            r1 = db.bloodline.find({'blood_code':blood_code})
            if r1.count()>0:
                return render.info('品系编码不能重复！')

            update_set['owner_uname'] = helper.get_session_uname()
            update_set['history'] =  [(helper.time_str(), helper.get_session_uname(), '新建')]
            db.bloodline.insert_one(update_set)
        else:
            r1 = db.bloodline.find({'_id': {'$ne':ObjectId(user_data['blood_id'])}, 'blood_code':blood_code})
            if r1.count()>0:
                return render.info('品系编码不能重复！')

            db.bloodline.update_one({'_id':ObjectId(user_data['blood_id'])}, {
                '$set'  : update_set,
                '$push' : {
                    'history' : (helper.time_str(), helper.get_session_uname(), '修改'), 
                }  # 纪录操作历史
            })

        return render.info('成功保存！', '/grp_admin/bloodline')
