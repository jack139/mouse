#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, re
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
        user_data = web.input(blood_id='', field='')

        # 品系数据
        blood_data = { 'blood_code' : '', '_id':'n/a'}

        if user_data.blood_id != '': 
            db_obj=db.bloodline.find_one({'_id':ObjectId(user_data.blood_id)})
            if db_obj!=None:
                # 已存在的obj
                blood_data = db_obj

        # 本组用户数据
        group_list = helper.get_session_group_list()

        users=[]            
        db_user=db.user.find({
            'privilege'  : helper.PRIV_USER, 
            'group_list' : '' if len(group_list)==0 else group_list[0],
        }).sort([('_id',1)])

        return render.grpad_bloodline_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            blood_data, [x for x in db_user], user_data['field'])


    def POST(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(blood_id='',blood_code='',name='',user_list=[],owner_user='')

        #print user_data

        #if user_data.name.strip()=='':
        #    return render.info('品系名不能为空！')  

        blood_code = user_data['blood_code'].strip()

        b_list = blood_code.split(',')  # 格式：品系名,基因型1,基因型2,...
        #if not b_list[0].replace('_','').isalnum(): # 格式：品系名,基因型1(+/+),基因型2(+/-),...
        #    return render.info('品系编码只能为字母和数字的组合！')  

        #for x in b_list[1:]:
        #    if re.search(r'^[A-Za-z0-9]+\((\+|\-)/(\+|\-)\)', x) is None:
        #        return render.info('品系编码中基因型格式错误！')  

        for x in b_list:
            if not x.replace('_','').isalnum():
                return render.info('品系编码只能为字母和数字的组合！')  

        # 本组用户数据
        group_list = helper.get_session_group_list()
        group_id = '' if len(group_list)==0 else group_list[0]

        try:
            update_set={
                'blood_code'  : blood_code,
                'name'        : user_data['name'],
                'status'      : user_data['status'],
                'note'        : user_data['note'],
                'user_list'   : user_data['user_list'],
                'owner_user'  : user_data['owner_user'],
                'group_id'    : group_id,
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
