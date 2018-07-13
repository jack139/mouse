#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import helper

db = helper.db


UNAME = {
    u'吴剑峰'   : 'wjf',
    u'陈长安'   : 'cca',
    u'赵一豪'   : 'zyh',
    u'何鹏'     : 'hp',
    u'刘艺菲'   : 'lyf',
    u'乔慕臻'   : 'qmz',
    u'王宇泽'   : 'wyz',
    u'杨道伟'   : 'ydw',
    u'张荧荧'   : 'zyy',
    u'梁波'     : 'lb2',
    u'洪茅'     : 'hm',
    u'马华彬'   : 'mhb',
    u'林怀鹏'   : 'lhp',
    u'张培培'   : 'zpp',
    u'黄凯'     : 'hk',

}

f=open('mouse.csv')

a=f.readline()

while True:
    b=f.readline().strip()
    if not b:
        break

    d=b.split(',')
    print d

    #print d[0].decode('gbk') # csv 使用gbk中文编码

    # 生成基本数据

    uname = UNAME[d[1].decode('gbk')]
    group_id = '00000001'

    # 笼架id
    shelf_id = '%s-%s-%s'%(d[20],d[21],[22])

    # 鼠笼id
    house_id = target_house_id = '%s-%s-%s'%(shelf_id,d[23],[24])

    # 小鼠品系信息
    blood_code = d[6]

    if len(d[8])>0 and len(d[9])>0:
        blood_code = blood_code + ',' + d[8] + d[9]

    if len(d[10])>0 and len(d[11])>0:
        blood_code = blood_code + ',' + d[10] + d[11]

    if len(d[12])>0 and len(d[13])>0:
        blood_code = blood_code + ',' + d[12] + d[13]

    if len(d[14])>0 and len(d[15])>0:
        blood_code = blood_code + ',' + d[14] + d[15]

    if len(d[16])>0 and len(d[17])>0:
        blood_code = blood_code + ',' + d[16] + d[17]

    if len(d[18])>0 and len(d[19])>0:
        blood_code = blood_code + ',' + d[18] + d[19]

    # 耳标
    tag = d[2]

    #检查鼠笼

    # 检查house_id
    db_obj=db.house.find_one({
        'house_id': target_house_id,
    })

    while 1: # 死循环，方便程序结构，无他用
        # 自己的鼠笼，可以移动
        if db_obj and db_obj['uname']==uname:
            if db_obj['expired_d']<helper.time_str(format=2):
                print '不能移动到已过期的鼠笼！'
                sys.exit(0)
            break

        # 其他人的鼠笼， 不能移动
        if db_obj and db_obj['uname']!='':
            print '鼠笼已被使用，只能移动自己的鼠笼！'
            sys.exit(0)

        # 不存在的鼠笼，或者无主的鼠笼
        #if db_obj==None or db_obj['uname']==''：
        
        # 检查是否是预分配的鼠笼
        shelf_id = '-'.join(target_house_id.split('-')[:3])
        r3 = db.shelf.find_one({'shelf_id':shelf_id})
        if r3 and (uname in r3.get('appoint',[])): # 是否是预分配的笼架

            if r3['appoint_expired_d']<helper.time_str(format=2):
                print '不能移动到已过期的预分配鼠笼！'
                sys.exit(0)

            #group_list = helper.get_session_group_list()
            #group_id = '' if len(group_list)==0 else group_list[0]

            # 自动更新鼠笼信息
            update_set={
                'house_id'  : target_house_id,
                'shelf_id'  : shelf_id,
                'type_list' : r3['appoint_type_list'],
                'status'    : 1,
                'uname'     : uname,
                'group_id'  : group_id,
                'expired_d' : r3['appoint_expired_d'],
                'last_tick' : int(time.time()),  # 更新时间戳
            }

            #db.house.update_one({'house_id':target_house_id}, {
            #    '$set'  : update_set,
            #    '$push' : {
            #        'history' : (helper.time_str(), uname, '修改'), 
            #    }  # 纪录操作历史
            #}, upsert=True)

            print update_set

        else:
            print '只能移动自己的鼠笼！'
            sys.exit(0)

        break


    #增加小鼠数据

    # 检查笼架所有权
    r6 = db.house.find_one({'house_id':house_id, 'uname':uname})
    if r6 is None:
        print '鼠笼可能不是您的！'
        sys.exit(0)

    # 同一实验组内，耳标不能重复
    if len(tag.strip())>0:
        r2 = db.mouse.find_one({'group_id' : group_id, 'tag' : tag.strip(), })
        if r2 is not None:
            #if str(r2['_id'])!=user_data['mouse_id']:
            print '耳标已存在，请重新输入！'
            sys.exit(0)

    # 检查品系编码格式
    blood_code = blood_code.strip()

    if len(blood_code)>0:
        b_list = blood_code.split(',')  # 格式：品系名,基因型1(+/+),基因型2(+/-),...
        #if not b_list[0].replace('_','').isalnum():
        #    return render.info('品系名只能为字母和数字的组合！')  

        for x in b_list[1:]:
            #if re.search(r'^[A-Za-z0-9]+\((\+|\-)/(\+|\-)\)', x) is None:
            if re.search(r'^.+\((\+|\-)/(\+|\-)\)', x) is None:
                print '品系编码中基因型格式错误！'
                sys.exit(0)

    try:
        update_set={
            'tag'        : tag.strip(),
            'mother_tag' : d['26'].strip(),
            'father_tag' : d['25'].strip(),
            'birth_d'    : d['3'],
            'divide_d'   : d['4'],
            'blood_code' : blood_code,
            #'gene_code'  : user_data['gene_code'].strip(),
            'note'       : d['7'],
            'house_id'   : house_id,
            'sex'        : d['5'].strip(),
            'status'     : 'live', # 正常
            'last_tick'  : int(time.time()),  # 更新时间戳
        }

        #if len(user_data['divide2_d'])>0:
        #    update_set['divide2_d'] = user_data['divide2_d']
    except ValueError:
        print '请在相应字段输入数字！'
        sys.exit(0)


    update_set['owner_uname'] = uname
    update_set['group_id'] = group_id
    update_set['history'] =  [(helper.time_str(), uname, '新建')]
    #db.mouse.insert_one(update_set)

    print update_set
