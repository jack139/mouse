#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 实验员员鼠笼设置

url = ('/grp_user/house_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
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

        db_obj=db.house.find_one({
            'house_id': user_data.house_id,
            'uname'   : helper.get_session_uname(),
        })
        if db_obj!=None:
            # 已存在的鼠笼
            house_data = db_obj

        # 此笼的小鼠信息
        db_mice = db.mouse.find({
            'house_id' : user_data['house_id'], 
            'status'   : {'$nin' : ['killed', 'dead']}
        }).sort([('_id',1)])

        mice = [i for i in db_mice]

        # 小鼠品系数据
        db_blood = db.bloodline.find({
            'status'    : 'ready',
            'user_list' : helper.get_session_uname(),
        })

        return render.user_house_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            house_data, db_user, helper.HOUSE_TYPE, db_blood, mice, helper.MOUSE_STATUS)


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(house_id='',type='',test_will_end_d='')

        if user_data.house_id.strip()=='':
            return render.info('参数错误！')

        if user_data.type=='':
            return render.info('请设置鼠笼类型！')

        #if user_data.blood_code=='':
        #    return render.info('请设置小鼠品系！')

        #shelf_id = u'-'.join(user_data['house_id'].split('-')[:3])
        #group_id = helper.get_session_group_list()[0]

        r2 = db.house.find_one({
            'house_id' : user_data['house_id'],
            'uname'    : helper.get_session_uname(),
        })
        if r2 is None: # 不错存在的house_id，或者无权限修改的鼠笼
            return render.info('鼠笼参数错误！')

        message = '修改'

        #r3 = db.mouse.find({
        #    'house_id' : user_data['house_id'], 
        #    'status'   : {'$nin' : ['killed', 'dead']}
        #})
        #if r3.count()>0 and r3[0]['blood_code']!=user_data['blood_code']:
        #    # 修改所有小鼠的品系
        #    db.mouse.update_many({
        #        'house_id' : user_data['house_id'], 
        #        'status'   : {'$nin' : ['killed', 'dead']}
        #    }, {'$set':{'blood_code':user_data['blood_code']}})
        #    message += ':品系'

        # 准备要更新的字段
        update_set={
            'type'      : user_data['type'],
            'last_tick' : int(time.time()),  # 更新时间戳
        }

        if user_data['type']=='test':
            # 实验笼需要设置预计结束时间
            if user_data['test_will_end_d']=='':
                return render.info('请设置实验预计结束时间！')
            update_set['test_will_end_d'] = user_data['test_will_end_d']

            if r2['type']!='test': # 鼠笼类型修改为实验笼，记录实验开始时间
                update_set['test_start_d'] = time.strftime("%Y%m%d", time.localtime()) # 格式 yyyymmdd
                message += ':设置实验笼'


        db.house.update_one({'house_id':user_data['house_id']}, {
            '$set'  : update_set,
            '$push' : {
                'history' : (helper.time_str(), helper.get_session_uname(), '修改'), 
            }  # 纪录操作历史
        })

        return render.info('成功保存！', '/grp_user/house_info?house_id=%s' % user_data['house_id'])
