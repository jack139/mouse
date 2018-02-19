#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 小鼠信息检索
# 管理员、实验员、教师均可使用，权限不同

url = ('/query/mice')

PAGE_SIZE = helper.PAGE_SIZE

#  -------------------
class handler:  
    def GET(self):
        user_priv = ''
        if helper.logged(helper.PRIV_USER, 'QUERY'):
            user_priv = 'user'
        elif helper.logged(helper.PRIV_GRP_ADMIN, 'QUERY'):
            user_priv = 'admin'
        elif helper.logged(helper.PRIV_TUTOR, 'QUERY'):
            user_priv = 'tutor'
        else:
            raise web.seeother('/')

        render = helper.create_render(globals={ 'str': str })
        user_data=web.input(page='0', v_tag='', v_blood='', v_uname='', v_house='')

        print user_data

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        group_list = helper.get_session_group_list()
        group_id = '' if len(group_list)==0 else group_list[0]
        # 实验员、管理员可查看的本实验组的小鼠
        # 教师可以查看所属组的小鼠


        # 获取对应权限的参数列表

        if user_priv in ['admin', 'user']:
            # 实验员
            r2 = db.user.find({
                'privilege'  : helper.PRIV_USER, 
                'group_list' : group_id,
            }, sort=[('_id', 1)])
            uname_list = [i['uname'] for i in r2]

            # 鼠笼
            r3 = db.house.find({'group_id': group_id}, sort=[('_id', 1)])
            house_list = [i['house_id'] for i in r3]

            # 品系
            r4 = db.mouse.distinct("blood_code", {'group_id': group_id})
            blood_list = r4
            blood_list.remove('')
        elif user_priv == 'tutor':
            # 实验员
            r2 = db.user.find({
                'privilege'  : helper.PRIV_USER, 
                'group_list' : {'$in': group_list},
            }, sort=[('_id', 1)])
            uname_list = [i['uname'] for i in r2]

            # 鼠笼
            r3 = db.house.find({'group_id': {'$in' : group_list}}, sort=[('_id', 1)])
            house_list = [i['house_id'] for i in r3]

            # 品系
            r4 = db.mouse.distinct("blood_code", {'group_id': {'$in' : group_list}})
            blood_list = r4
        else:
            uname_list = []
            house_list = []
            blood_list = []

        # 检查参数合法性
        v_tag = user_data.v_tag.strip()
        v_house = '' if user_data.v_house not in house_list else user_data.v_house
        v_uname = '' if user_data.v_uname not in uname_list else user_data.v_uname
        v_blood = '' if user_data.v_blood not in blood_list else user_data.v_blood

        # 生成查询条件
        conditions = {'group_id' : { '$in':group_list }}
        if v_tag!='':
            conditions['tag'] = v_tag

        if v_uname!='':
            conditions['owner_uname'] = v_uname

        if v_house!='':
            conditions['house_id'] = v_house

        if v_blood!='':
            conditions['blood_code'] = v_blood

        print 'conditions: ', conditions

        # 分页获取数据
        db_sku = db.mouse.find(conditions,
            sort=[('status',-1),('_id', 1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        # 课题组名
        group_name = {'' : 'n/a'}
        r2 = db.groups.find({'group_id' : {'$in' : group_list}})
        for i in r2:
            group_name[i['group_id']] = i['name']


        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.query_mice(helper.get_session_uname(), helper.get_privilege_name(), 
            db_sku, range(0, num), group_name, uname_list, house_list, blood_list)
