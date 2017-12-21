#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper, app_helper

db = setting.db_web

# 实验员修改

url = ('/grp_admin/user_edit')


#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()

        user_data=web.input(uid='')

        db_user={ '_id':'n/a', 'menu_level':60*'-', 'time':int(time.time())}

        if user_data.uid!='':
            r2=db.user.find_one({'_id':ObjectId(user_data.uid)})
            if r2:
                db_user = r2

        if db_user['_id']=='n/a':
            user_level_name = []
        else:
            user_level_name = helper.get_privilege_name(db_user['privilege'],db_user['menu_level'])

        # 取得当前管理员的group名称
        group_name = ['n/a', '']
        group_list = helper.get_session_group_list()
        if len(group_list)>0:
            db_grp = db.groups.find_one({'group_id':group_list[0]})
            if db_grp:
                group_name = [db_grp['name'], group_list[0]]

        return render.grpad_user_setting(helper.get_session_uname(), helper.get_privilege_name(), 
            db_user, helper.time_str(db_user['time']), user_level_name, group_name)


    def POST(self):
        if not helper.logged(helper.PRIV_GRP_ADMIN, 'GROUP_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()

        user_data=web.input(uid='', uname='', full_name='', passwd='', 
            user_type='', group_id='', priv=[])

        privilege = helper.PRIV_USER   # 课题组实验员
        priv = ['GROUP_USER']

        # 课题组id取自session, 2017-12-12
        if user_data['group_id']=='':
            return render.info('需设置所属课题组！')

        # 设置权限标记
        menu_level = 60*'-'
        #for p in user_data.priv: 
        for p in priv:
            pos = helper.MENU_LEVEL[p]
            menu_level = menu_level[:pos]+'X'+menu_level[pos+1:]

        # 更新数据
        update_set = {
            'login'      : int(user_data['login']), 
            'privilege'  : privilege, 
            'menu_level' : menu_level,
            'full_name'  : user_data['full_name'],
            'user_type'  : 'grp_user',  # 实验员
            'group_list' : [user_data['group_id']], # 只有一个元素list, 2017-12-14
        }

        # 如需要，更新密码
        if len(user_data['passwd'])>0:
            update_set['passwd']=app_helper.my_crypt(user_data['passwd'])
            update_set['pwd_update']=0

        if user_data['uid']=='n/a':
            # 新增
            update_set['uname']=user_data['uname'].lower().strip()
            if len(update_set['uname'])==0:
                return render.info('用户名不能为空！')
            r2=db.user.find_one({'uname': update_set['uname']})
            if r2:
                return render.info('用户名已存在！请修改后重新添加。')
            update_set['time']=int(time.time())
            db.user.insert(update_set)
        else:
            # 修改
            db.user.update_one({'_id':ObjectId(user_data['uid'])}, {'$set' : update_set })

        return render.info('成功保存！','/grp_admin/user')
