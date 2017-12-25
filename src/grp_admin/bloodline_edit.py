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

# 品系信息编辑

url = ('/grp_admin/bloodline_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(blood_id='')

        blood_data = { 'blood_code' : '', '_id':'n/a'}

        if user_data.blood_id != '': 
            db_obj=db.bloodline.find_one({'_id':ObjectId(user_data.blood_id)})
            if db_obj!=None:
                # 已存在的obj
                blood_data = db_obj

        return render.grpad_bloodline_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            blood_data)


    def POST(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(blood_id='',blood_code='',name='')

        if user_data.name.strip()=='':
            return render.info('品系名不能为空！')  

        blood_code = user_data['blood_code'].strip()

        try:
            update_set={
                'blood_code'  : blood_code,
                'name'        : user_data['name'],
                'status'      : user_data['status'],
                'note'        : user_data['note'],
                'last_tick'   : int(time.time()),  # 更新时间戳
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        if user_data['blood_id']=='n/a': # 新建
            r1 = db.bloodline.find({'blood_code':blood_code})
            if r1.count()>0:
                return render.info('品系编码不能重复！')

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
