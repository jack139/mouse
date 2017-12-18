#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import os, sys, gc
import time, json
from decimal import Decimal
from bson.objectid import ObjectId
from config.url import urls
from config import setting
from config.mongosession import MongoStore
import helper, app_helper
from libs import rand_code

from helper import time_str
from helper import get_privilege_name
from helper import logged
from helper import create_render

db = setting.db_web  # 默认db使用web本地
db_primary = setting.db_primary

app = web.application(urls, globals())
application = app.wsgifunc()

#--session---------------------------------------------------
web.config.session_parameters['cookie_name'] = 'pretty_session'
web.config.session_parameters['secret_key'] = 'f6102bff8452386b8ca1'
web.config.session_parameters['timeout'] = 86400
web.config.session_parameters['ignore_expiry'] = True

if setting.debug_mode==False:
    ### for production
    session = web.session.Session(app, MongoStore(db_primary, 'sessions'), 
        initializer={'login': 0, 'privilege': 0, 'uname':'', 'uid':'', 'menu_level':'', 'group_list':''})
else:
    ### for staging,
    if web.config.get('_session') is None:
        session = web.session.Session(app, MongoStore(db_primary, 'sessions'), 
            initializer={'login': 0, 'privilege': 0, 'uname':'', 'uid':'', 'menu_level':'', 'group_list':''})
        web.config._session = session
    else:
        session = web.config._session

#----------------------------------------

# 在请求前检查helper.web_session, 调试阶段会出现此现象
def my_processor(handler): 
    if helper.web_session==None:
        print 'set helper.web_session'
        helper.set_session(session)     
    return  handler() 

app.add_processor(my_processor)
#----------------------------------------

gc.set_threshold(300,5,5)

user_level = helper.user_level

###########################################


class Login:
    def GET(self):
        if logged():
            render = create_render()

            result = 0

            if logged(helper.PRIV_USER|helper.PRIV_GRP_ADMIN|helper.PRIV_TUTOR):
                # 提醒改密码
                db_user=db.user.find_one({'uname':session.uname},{'pwd_update':1})
                if int(time.time()) - db_user.get('pwd_update', 0) > 3600*24*30:
                    db.user.update_one({'uname':session.uname},{'$set' :{'pwd_update':int(time.time())}}) # 只提示一次， 2017-12-11
                    raise web.seeother('/settings_user?set_pwd=1')
                else:
                    return render.portal(session.uname, get_privilege_name(), [result])
            else:
                return render.portal(session.uname, get_privilege_name(), [result])
        else:
            render = create_render()

            db_sys = db.user.find_one({'uname':'settings'})
            if db_sys==None:
                signup=0
            else:
                signup=db_sys['signup']

            # 生成验证码
            rand=app_helper.my_rand(4).upper()
            session.uid = rand # uid 临时存放验证码
            session.menu_level = 0 # 暂存输入验证码次数
            png2 = rand_code.gen_rand_png(rand)

            return render.login(signup, png2)

    def POST(self):
        name0, passwd, rand = web.input().name, web.input().passwd, web.input().rand
        
        name = name0.lower()
        
        render = create_render()

        session.login = 0
        session.privilege = 0
        session.uname=''

        db_user=db.user.find_one({'uname':name})
        if db_user!=None and db_user['login']!=0:
            if session.menu_level>=5:
                print '-----> 刷验证码！'
                return render.login_error('验证码错误，请重新登录！')
            if session.uid != rand.upper():
                session.menu_level += 1
                return render.login_error('验证码错误，请重新登录！')
            if db_user.get('passwd')!=app_helper.my_crypt(passwd): # passwd 有可能不存在，如果新建用户未设置密码， 2017-12-11
                return render.login_error('密码错误，请重新登录！')

            session.login = 1
            session.uname = name
            session.uid = db_user['_id']
            session.privilege = int(db_user['privilege'])
            session.group_list = db_user.get('group_list',[])

            # 若是老用户则将session的权限位数增加至60
            session.menu_level = db_user['menu_level'] if len(db_user['menu_level']) == 60 else db_user['menu_level']+30*'-'
            raise web.seeother('/')
        else:
            return render.login_error()

class Reset:
    def GET(self):
        session.login = 0
        session.kill()
        render = create_render()
        return render.logout()

class SettingsUser:
    def _get_settings(self):
        db_user=db.user.find_one({'_id':session.uid},{'uname':1,'full_name':1})
        return db_user
    
    def GET(self):
        if not logged(helper.PRIV_USER|helper.PRIV_GRP_ADMIN):
            raise web.seeother('/')

        render = create_render()
        if web.input(set_pwd='')['set_pwd']=='1':
            return render.settings_user(session.uname, get_privilege_name(), self._get_settings(), '请重新设置密码')
        else:
            return render.settings_user(session.uname, get_privilege_name(), self._get_settings())
            

    def POST(self):
        if not logged(helper.PRIV_USER|helper.PRIV_GRP_ADMIN):
            raise web.seeother('/')

        render = create_render()
        #full_name = web.input().full_name
        old_pwd = web.input().old_pwd.strip()
        new_pwd = web.input().new_pwd.strip()
        new_pwd2 = web.input().new_pwd2.strip()
        
        if old_pwd!='':
            if new_pwd=='':
                return render.info('新密码不能为空！请重新设置。')
            if new_pwd!=new_pwd2:
                return render.info('两次输入的新密码不一致！请重新设置。')
            # 检查密码强度
            _num = 0
            _upper = 0
            _misc = 0
            for xx in new_pwd:
                if xx.isdigit():
                    _num = 1
                elif xx.isupper():
                    _upper = 1
                elif xx in '+-_/%$':
                    _misc = 1
            if _num+_upper+_misc<3:
                return render.info('密码强度太低，容易被破解，请重新输入！')

            db_user=db.user.find_one({'_id':session.uid},{'passwd':1})
            if app_helper.my_crypt(old_pwd)==db_user['passwd']:
                db.user.update_one({'_id':session.uid}, {'$set':{
                    'passwd'     : app_helper.my_crypt(new_pwd),
                    'pwd_update' : int(time.time()),
                    #'full_name'  : full_name
                }})
            else:
                return render.info('登录密码验证失败！请重新设置。')
        #else:
        #   db.user.update_one({'_id':session.uid}, {'$set':{'full_name':full_name}})

        return render.info('成功保存！','/')
            



########## Admin 功能 ####################################################

class AdminUser:
    def GET(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()

        users=[]            
        db_user=db.user.find({'privilege': {'$nin': [helper.PRIV_ADMIN,helper.PRIV_USER]}}).sort([('_id',1)])
        if db_user.count()>0:
            for u in db_user:
                if u['uname']=='settings':
                    continue
                users.append([u['uname'],u['_id'],int(u['privilege']),u['full_name'],u['login'],u['user_type']])
        return render.user(session.uname, user_level[session.privilege], users)
            


class AdminUserSetting:     
    def GET(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        user_data=web.input(uid='')

        r3 = db.groups.find({'status':1})

        db_user={ '_id':'n/a', 'menu_level':60*'-', 'time':int(time.time())}

        if user_data.uid!='':
            r2=db.user.find_one({'_id':ObjectId(user_data.uid)})
            if r2:
                db_user = r2

        if db_user['_id']=='n/a':
            user_level_name = []
        else:
            user_level_name = get_privilege_name(db_user['privilege'],db_user['menu_level'])
        return render.user_setting(session.uname, user_level[session.privilege], 
            db_user, time_str(db_user['time']), user_level_name, r3)


    def POST(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        user_data=web.input(uid='', uname='', full_name='', passwd='', 
            user_type='', group_id=[], priv=[])

        if user_data['user_type']=='grp_admin':
            privilege = helper.PRIV_GRP_ADMIN   # 课题组管理员
            priv = ['GROUP_ADMIN']
        else:
            privilege = helper.PRIV_TUTOR   # 指导教师
            priv = ['TUTOR']

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
            'user_type'  : user_data['user_type'],
            'group_list' : user_data['group_id'],
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

        return render.info('成功保存！','/admin/user')



class AdminSysSetting:      
    def GET(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()

        db_sys=db.user.find_one({'uname':'settings'})
        if db_sys!=None:
            return render.sys_setting(session.uname, user_level[session.privilege], db_sys)
        else:
            db.user.insert_one({'uname':'settings','signup':0,'login':0,
            'pk_count':1,'wt_count':1,'sa_count':1})
            return render.info('如果是新系统，请重新进入此界面。','/')  
            

    def POST(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        user_data=web.input(signup='0', pk_count='1', wt_count='1', sa_count='1')

        db.user.update_one({'uname':'settings'},{'$set':{
            'pk_count': int(user_data['pk_count']),
            'wt_count': int(user_data['wt_count']),
            'sa_count': int(user_data['sa_count']),
        }})

        return render.info('成功保存！','/admin/sys_setting')

            

class AdminSelfSetting:

    def _get_settings(self):
        db_user=db.user.find_one({'_id':session.uid})
        return db_user

    def GET(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        return render.self_setting(session.uname, user_level[session.privilege], self._get_settings())
            

    def POST(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        old_pwd = web.input().old_pwd.strip()
        new_pwd = web.input().new_pwd.strip()
        new_pwd2 = web.input().new_pwd2.strip()

        if old_pwd!='':
            if new_pwd=='':
                return render.info('新密码不能为空！请重新设置。')
            if new_pwd!=new_pwd2:
                return render.info('两次输入的新密码不一致！请重新设置。')
            db_user=db.user.find_one({'_id':session.uid},{'passwd':1})
            if app_helper.my_crypt(old_pwd)==db_user['passwd']:
                db.user.update_one({'_id':session.uid}, {'$set':{'passwd':app_helper.my_crypt(new_pwd)}})
                return render.info('成功保存！','/')
            else:
                return render.info('登录密码验证失败！请重新设置。')
        else:
            return render.info('未做任何修改。')

            

class AdminStatus: 
    def GET(self):
        import os

        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
    
        uptime=os.popen('uptime').readlines()
        takit=os.popen('pgrep -f "uwsgi_fair.sock"').readlines()
        error_log=os.popen('tail %s/error.log' % setting.logs_path).readlines()
        uwsgi_log=os.popen('tail %s/uwsgi_fair.log' % setting.logs_path).readlines()
        processor_log=os.popen('tail %s/processor.log' % setting.logs_path).readlines()
        df_data=os.popen('df -h').readlines()

        #import sms_mwkj
        #balance = sms_mwkj.query_balance()

        return render.status(session.uname, user_level[session.privilege],{
            'uptime'       :  uptime,
            'takit'     :  takit,
            'error_log' :  error_log,
            'uwsgi_log' :  uwsgi_log,
            'process_log'  :  processor_log,
            'df_data'     :  df_data})
            

class AdminData: 
    def GET(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()

        db_active=db.user.find({'$and': [{'login'    : 1},
                         {'privilege' : helper.PRIV_USER},
                        ]},
                        {'_id':1}).count()
        db_nonactive=db.user.find({'$and': [{'login'     : 0},
                         {'privilege' : helper.PRIV_USER},
                        ]},
                        {'_id':1}).count()
        db_admin=db.user.find({'privilege' : helper.PRIV_ADMIN}, {'_id':1}).count()

        db_sessions=db.sessions.find({}, {'_id':1}).count()
        db_device=db.device.find({}, {'_id':1}).count()
        db_todo=db.todo.find({}, {'_id':1}).count()
        db_sleep=db.todo.find({'status':'SLEEP'}, {'_id':1}).count()
        db_lock=db.todo.find({'lock':1}, {'_id':1}).count()
        db_thread=db.thread.find({}).sort([('tname',1)])
        idle_time = []
        for t in db_thread:
            idle_time.append(t)

        return render.data(session.uname, user_level[session.privilege],
            {
              'active'     :  db_active,
              'nonactive'   :  db_nonactive,
              'admin'       :  db_admin,
              'sessions'     :  db_sessions,
              'device'     :  db_device,
              'todo'         :  db_todo,
              'sleep'       :  db_sleep,
              'lock'         :  db_lock,
              'idle_time'   :  idle_time,
            })


PAGE_SIZE = 50            

class AdminGroup: 
    def GET(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        user_data=web.input(page='0')

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        # 分页获取数据
        db_sku = db.groups.find(
            sort=[('status', -1), ('group_id', -1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.group(session.uname, user_level[session.privilege], db_sku, range(0, num))


class AdminGroupEdit: 
    def GET(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        user_data = web.input(group_id='')

        group_data = { 'group_id' : 'n/a'}

        if user_data.group_id != '': 
            db_obj=db.groups.find_one({'group_id':user_data.group_id})
            if db_obj!=None:
                # 已存在的obj
                group_data = db_obj

        return render.group_edit(session.uname, user_level[session.privilege], group_data)


    def POST(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        user_data=web.input(group_id='',group_name='')

        if user_data.group_name.strip()=='':
            return render.info('课题组名不能为空！')

        if user_data['group_id']=='n/a': # 新建
            db_pk = db.user.find_one_and_update(
                {'uname'    : 'settings'},
                {'$inc'     : {'pk_count' : 1}},
                {'pk_count' : 1}
            )
            group_id = '0%07d' % db_pk['pk_count']
            message = '新建'
        else:
            group_id = user_data['group_id']
            message = '修改'

        try:
            update_set={
                'group_id'    : group_id,
                'name'        : user_data['group_name'],
                'note'        : user_data['note'],
                'status'      : int(user_data['status']),
                'last_tick'   : int(time.time()),  # 更新时间戳
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        db.groups.update_one({'group_id':group_id}, {
            '$set'  : update_set,
            '$push' : {
                'history' : (helper.time_str(), helper.get_session_uname(), message), 
            }  # 纪录操作历史
        }, upsert=True)

        return render.info('成功保存！', '/admin/group')



class AdminShelf: 
    def GET(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        user_data=web.input(page='0')

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        # 获取课题组名字对照
        r3 = db.groups.find({'status':1})
        group_name = {'n/a':'n/a'}
        for i in r3:
            group_name[i['group_id']]=i['name']

        # 分页获取数据
        db_sku = db.shelf.find(
            sort=[('shelf_id', -1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.shelf(session.uname, user_level[session.privilege], db_sku, range(0, num), group_name)


class AdminShelfEdit: 
    def GET(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        user_data = web.input(shelf_id='')

        r3 = db.groups.find({'status':1})

        shelf_data = { 'shelf_id' : 'n/a'}

        if user_data.shelf_id != '': 
            db_obj=db.shelf.find_one({'shelf_id':user_data.shelf_id})
            if db_obj!=None:
                # 已存在的obj
                shelf_data = db_obj

        return render.shelf_edit(session.uname, user_level[session.privilege], shelf_data, r3)


    def POST(self):
        if not logged(helper.PRIV_ADMIN):
            raise web.seeother('/')

        render = create_render()
        user_data=web.input(shelf_id='',area='',room='',shelf='')

        expired_d= user_data.expired_d.strip()
        if len(expired_d)!=6 or (not expired_d.isdigit()):
            return render.info('过期日期格式不对')

        if user_data['shelf_id']=='n/a': # 新建
            shelf_id = '%s-%s-%s' % (user_data['area'].strip(),user_data['room'].strip(),user_data['shelf'].strip())
            r2=db.shelf.find_one({'shelf_id':shelf_id})
            if r2:
                return render.info('此笼架已存在')
            message = '新建'
        else:
            shelf_id = user_data['shelf_id']
            message = '修改'

        try:
            update_set={
                'shelf_id'    : shelf_id,
                'group_id'    : user_data['group_id'],
                'expired_d'   : expired_d,
                'note'        : user_data['note'],
                'last_tick'   : int(time.time()),  # 更新时间戳
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        db.shelf.update_one({'shelf_id':shelf_id}, {
            '$set'  : update_set,
            '$push' : {
                'history' : (helper.time_str(), helper.get_session_uname(), message), 
            }  # 纪录操作历史
        }, upsert=True)

        return render.info('成功保存！', '/admin/shelf')


#if __name__ == "__main__":
#   web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
#   app.run()
