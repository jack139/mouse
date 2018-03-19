#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 实验员修改

url = ('/grp_admin/credit_edit')


#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()

        user_data=web.input(uid='')


        if user_data['uid']=='':
            return render.info('参数错误！')  

        r2 = db.user.find_one({'_id':ObjectId(user_data.uid)})
        if r2 is None:
            return render.info('uid参数错误！')  

        r3 = db.credit.find({'uname' : r2['uname']}, sort=[('date_t', -1)])

        return render.grpad_credit_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            r2, helper.CREDIT_LIST, r3)


    def POST(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()

        user_data=web.input(uname='', credit='', comment='')

        if '' in (user_data['uname'], user_data['credit']):
            return render.info('请设置评分！')  

        # 课题组id取自session, 2017-12-12
        group_list = helper.get_session_group_list()
        group_id = '' if len(group_list)==0 else group_list[0]

        db.credit.insert_one({
            'uname' : user_data['uname'],
            'group_id' : group_id,
            'credit' : int(user_data['credit']),
            'comment' : user_data['comment'],
            'date_t' : helper.time_str(),
        })

        # 更新用户的评分
        r2 = db.user.find_one({'uname' : user_data['uname']})
        credit_score = r2.get('credit_score', 100) - int(user_data['credit'])
        db.user.update_one({'uname' : user_data['uname']}, {'$set' : {'credit_score' : credit_score}})

        return render.info('成功保存！','/grp_admin/user')
