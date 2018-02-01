#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, re
from bson.objectid import ObjectId
from config import setting
from libs import gene
import helper

db = setting.db_web

# 小鼠信息编辑

url = ('/grp_user/mice_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(mouse_id='',from_house='')

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
            # 需要检查鼠笼类型的限制
            house.append(i['house_id'])

        # 品系信息
        db_blood = db.bloodline.find({
            'status'    : 'ready',
            'user_list' : helper.get_session_uname(),
        })

        # 生成父系和母系的基因系列
        parent_gene = []
        if user_data.mouse_id != '':
            if mouse_data.get('mother_tag', '')!='' and mouse_data.get('father_tag', '')!='':
                r3 = db.mouse.find({'tag' : {'$in':[mouse_data['mother_tag'], mouse_data['father_tag']]}})
                if r3.count()==2:
                    parent_gene = gene.genetic2(r3[0]['blood_code'], r3[1]['blood_code'])
                    print parent_gene

        return render.user_mice_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            mouse_data, house, db_blood, user_data['from_house'], parent_gene)


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'GROUP_USER'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(mouse_id='',tag='',mother_tag='',birth_d='',divide_d='',
            sex='',blood_code='',gene_code='',house_id='',father_tag='',from_house='')

        #if user_data.mother_tag.strip()=='':
        #    return render.info('亲本耳标不能为空！')  

        if '' in (user_data.birth_d,user_data.divide_d,user_data.sex):
            return render.info('请填写不能为空小鼠信息！')  

        group_id = helper.get_session_group_list()[0]

        # 同一实验组内，耳标不能重复
        if len(user_data['tag'].strip())>0:
            r2 = db.mouse.find_one({'group_id' : group_id, 'tag' : user_data['tag'].strip(), })
            if r2 is not None:
                if str(r2['_id'])!=user_data['mouse_id']:
                    return render.info('耳标已存在，请重新输入！')  

        # 检查品系编码格式
        blood_code = user_data['blood_code'].strip()

        if len(blood_code)>0:
            b_list = blood_code.split(',')  # 格式：品系名,基因型1(+/+),基因型2(+/-),...
            if not b_list[0].replace('_','').isalnum():
                return render.info('品系编码只能为字母和数字的组合！')  

            for x in b_list[1:]:
                if re.search(r'^[A-Za-z0-9]+\((\+|\-)/(\+|\-)\)', x) is None:
                    return render.info('品系编码中基因型格式错误！')  

        # 检查鼠笼是否超出最大数量
        r4=db.mouse.find({
            'house_id' : user_data['house_id'],
            '_id'      : {'$ne' : ObjectId(user_data['mouse_id'])},
        })

        if r4.count()+1>helper.MAX_MOUSE_NUM:
            return render.info('目标鼠笼容纳不下！')  

        try:
            update_set={
                'tag'        : user_data['tag'].strip(),
                'mother_tag' : user_data['mother_tag'].strip(),
                'father_tag' : user_data['father_tag'].strip(),
                'birth_d'    : user_data['birth_d'],
                'divide_d'   : user_data['divide_d'],
                'blood_code' : blood_code,
                'gene_code'  : user_data['gene_code'].strip(),
                'note'       : user_data['note'],
                'house_id'   : user_data['house_id'],
                'sex'        : user_data['sex'],
                'status'     : 'live', # 正常
                'last_tick'  : int(time.time()),  # 更新时间戳
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        if user_data['mouse_id']=='n/a': # 新建
            update_set['owner_uname'] = helper.get_session_uname()
            update_set['group_id'] = group_id
            update_set['history'] =  [(helper.time_str(), helper.get_session_uname(), '新建')]
            db.mouse.insert_one(update_set)
        else:
            db.mouse.update_one({'_id':ObjectId(user_data['mouse_id'])}, {
                '$set'  : update_set,
                '$push' : {
                    'history' : (helper.time_str(), helper.get_session_uname(), '修改'), 
                }  # 纪录操作历史
            })

        if user_data['from_house']=='1' and user_data['mouse_id']!='n/a':
            return render.info('成功保存！', '/grp_user/mice_info?mouse_id=%s'%user_data['mouse_id'])
        else:
            return render.info('成功保存！', '/grp_user/mice')
