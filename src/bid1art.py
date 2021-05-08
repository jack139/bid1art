#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 本地调试
# uwsgi --http 127.0.0.1:8000  --wsgi-file bid1art.py --check-static ../

import web
import os, sys, gc
import time, json
from decimal import Decimal
from bson.objectid import ObjectId
from config.url import urls
from config import setting
#from config.mongosession import MongoStore
from config.redissession import RedisStore
import helper, app_helper
from libs import rand_code

from helper import time_str
from helper import get_privilege_name
from helper import logged
from helper import create_render

from chain_api import fork_api

db = setting.db_web  # 默认db使用web本地
db_primary = setting.db_primary

app = web.application(urls, globals())
application = app.wsgifunc()

#--session---------------------------------------------------
web.config.session_parameters['cookie_name'] = 'bid1art_session'
web.config.session_parameters['secret_key'] = 'f6102bff8452386b8ca1'
web.config.session_parameters['timeout'] = 86400
web.config.session_parameters['ignore_expiry'] = True

if setting.debug_mode==False:
    ### for production
    session = web.session.Session(app, RedisStore(), 
        initializer={'login': 0, 'privilege': 0, 'uname':'', 'uid':'', 'menu_level':''})
else:
    ### for staging,
    if web.config.get('_session') is None:
        session = web.session.Session(app, RedisStore(), 
            initializer={'login': 0, 'privilege': 0, 'uname':'', 'uid':'', 'menu_level':''})
        web.config._session = session
    else:
        session = web.config._session

#----------------------------------------

# 在请求前检查helper.web_session, 调试阶段会出现此现象
def my_processor(handler): 
    if helper.web_session==None:
        print('set helper.web_session')
        helper.set_session(session)     
    return  handler() 

app.add_processor(my_processor)
#----------------------------------------

gc.set_threshold(300,5,5)

user_level = helper.user_level

###########################################

def my_crypt(codestr):
    import hashlib
    return hashlib.sha1(b"sAlT139-"+codestr.encode('utf-8')).hexdigest()

class Login:
    def GET(self):
        if logged():
            render = create_render()
            result = 0
            return render.portal(session.uname, get_privilege_name(), [result])
        else:
            render = create_render()
            signup=0

            # 生成验证码
            rand=app_helper.my_rand(4).upper()
            session.uid = rand # uid 临时存放验证码
            session.menu_level = 0 # 暂存输入验证码次数
            png2 = rand_code.gen_rand_png(rand)

            return render.login(signup, png2)

    def POST(self):
        chainaddr, passwd, rand = web.input().chainaddr, web.input().passwd, web.input().rand

        passwd = ' '.join(passwd.split()) # 去掉回车，只间隔一个空格
        name=''
        menu_level = 60*'-'

        render = create_render()

        session.login = 0
        session.privilege = 0
        session.uname=''

        if session.menu_level>=5:
            print('-----> 刷验证码！')
            return render.login_error('验证码错误，请重新登录！')
        if session.uid != rand.upper():
            session.menu_level += 1
            return render.login_error('验证码错误，请重新登录！')

        # 链上验证用户
        r1 = fork_api('/query/user/verify', {
            'chain_addr' : chainaddr,
            'mystery'    : passwd,
        })
        if (r1 is None) or r1['code']!=0:
            return render.login_error('登录失败，请重新登录！(%s %s)'%\
                ((r1['code'], r1['msg']) if r1 else ('', '')))

        if r1['data']['verified']==False:
            return render.login_error('密码错误，请重新登录！')

        if chainaddr==setting.SYS_ADMIN: # 管理员
            privilege = helper.PRIV_ADMIN
            name = 'admin'
            pos = helper.MENU_LEVEL['ADMIN']
            menu_level = menu_level[:pos]+'X'+menu_level[pos+1:]

        else:
            # 获取用户信息
            r1 = fork_api('/query/user/info', {
                'chain_addr' : chainaddr,
            })
            if (r1 is None) or r1['code']!=0:
                return render.login_error('出错了，请联系管理员！(%s %s)'%\
                    ((r1['code'], r1['msg']) if r1 else ('', '')))

            name = r1['data']['user']['login_name']
            # 不同用户权限
            if r1['data']['user']['user_type'] in ['TRD', 'DEL', 'ART']:
                privilege = helper.PRIV_TRD
                pos = helper.MENU_LEVEL['TRD']
                menu_level = menu_level[:pos]+'X'+menu_level[pos+1:]
            elif r1['data']['user']['user_type'] == 'AH':
                privilege = helper.PRIV_AH
                pos = helper.MENU_LEVEL['AH']
                menu_level = menu_level[:pos]+'X'+menu_level[pos+1:]
                pos = helper.MENU_LEVEL['REV'] # 拍卖行也有评论权限
                menu_level = menu_level[:pos]+'X'+menu_level[pos+1:]
            elif r1['data']['user']['user_type'] == 'REV':
                privilege = helper.PRIV_REV
                pos = helper.MENU_LEVEL['REV']
                menu_level = menu_level[:pos]+'X'+menu_level[pos+1:]

        # 设置session
        session.login = 1
        session.uname = name
        session.uid = chainaddr
        session.privilege = privilege
        session.menu_level = menu_level
        raise web.seeother('/')


class Reset:
    def GET(self):
        session.login = 0
        session.kill()
        render = create_render()
        return render.logout()



########## Admin 功能 ####################################################

class AdminUser:
    def GET(self):
        PAGE_SIZE = 20
        if logged(helper.PRIV_ADMIN):
            user_data=web.input(page='1')
            render = create_render()

            if not user_data['page'].isdigit():
                return render.info('page参数错误！')  

            # 链上用户列表
            r1 = fork_api('/query/user/list', {
                'page'  : int(user_data['page']),
                'limit' : PAGE_SIZE,
            })
            if (r1 is None) or r1['code']!=0:
                return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

            users=[]
            for u in r1['data']['user_list']:
                users.append([u['login_name'],u['chain_addr'],u['user_type'],u['reg_date'],u['status']])

            return render.user(session.uname, user_level[session.privilege], users, 
                int(user_data['page']), len(users)==PAGE_SIZE)
        else:
            raise web.seeother('/')


class AdminUserSetting:     
    def GET(self):
        if logged(helper.PRIV_ADMIN):
            render = create_render()
            user_data=web.input(uid='')

            if user_data.uid=='':
                return render.info('错误的参数！')  

            # 获取用户信息
            r1 = fork_api('/query/user/info', {
                'chain_addr' : user_data.uid,
            })
            if (r1 is None) or r1['code']!=0:
                return render.info('出错了，请联系管理员！(%s %s)'%\
                    ((r1['code'], r1['msg']) if r1 else ('', '')))

            return render.user_setting(session.uname, user_level[session.privilege], r1['data']['user'])
        else:
            raise web.seeother('/')

    def POST(self):
        if logged(helper.PRIV_ADMIN):
            render = create_render()
            user_data=web.input(chain_addr='', bank_acc_name='', 
                bank_name='', bank_acc_no='', address='', phone='', email='')

            if user_data.chain_addr=='':
                return render.info('参数错误！')  

            # 链上修改用户信息
            r1 = fork_api('/biz/user/modify', {
                'chain_addr'    : user_data['chain_addr'],
                'bank_acc_name' : user_data['bank_acc_name'],
                'bank_name'     : user_data['bank_name'],
                'bank_acc_no'   : user_data['bank_acc_no'],
                'address'       : user_data['address'],
                'phone'         : user_data['phone'],
                'email'         : user_data['email'],
            })
            if (r1 is None) or r1['code']!=0:
                return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

            return render.info('成功保存！','/admin/user')
        else:
            raise web.seeother('/')

class AdminUserAdd:     
    def GET(self):
        if logged(helper.PRIV_ADMIN):
            render = create_render()
            return render.user_new(session.uname, user_level[session.privilege])
        else:
            raise web.seeother('/')

    def POST(self):
        if logged(helper.PRIV_ADMIN):
            render = create_render()
            user_data=web.input(login_name='', user_type='', bank_acc_name='', 
                bank_name='', bank_acc_no='', address='', phone='', email='', referrer='')
            print(user_data)

            if user_data.login_name=='':
                return render.info('用户名不能为空！')  

            # 链上新建用户
            r1 = fork_api('/biz/user/register', {
                'login_name'    : user_data['login_name'],
                'user_type'     : user_data['user_type'],
                'bank_acc_name' : user_data['bank_acc_name'],
                'bank_name'     : user_data['bank_name'],
                'bank_acc_no'   : user_data['bank_acc_no'],
                'address'       : user_data['address'],
                'phone'         : user_data['phone'],
                'email'         : user_data['email'],
                'referrer'      : user_data['referrer'],
            })
            if (r1 is None) or r1['code']!=0:
                if r1 and r1['code']==9009:
                    return render.info('用户名已存在！请修改后再试。')
                else:   
                    return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

            return render.info('注册成功！<p>请妥善保存以下信息：</p><p>链地址：%s</p><p>密码字符串：\n%s</p>'%\
                (r1['data']['chain_addr'], r1['data']['mystery']),'/admin/user')
            #else:
            #    return render.info('用户名已存在！请修改后重新添加。')
        else:
            raise web.seeother('/')


class AdminStatus: 
    def GET(self):
        import os

        if logged(helper.PRIV_ADMIN):
            render = create_render()
        
            uptime=os.popen('uptime').readlines()
            takit=os.popen('pgrep -f "uwsgi_*.sock"').readlines()
            error_log=os.popen('tail %s/error.log' % setting.logs_path).readlines()
            uwsgi_log=os.popen('tail %s/uwsgi_fair.log' % setting.logs_path).readlines()
            df_data=os.popen('df -h').readlines()

            return render.status(session.uname, user_level[session.privilege],{
                'uptime'      : uptime,
                'takit'       : takit,
                'error_log'   : error_log,
                'uwsgi_log'   : uwsgi_log,
                'df_data'     : df_data})
        else:
            raise web.seeother('/')

class AdminData: 
    def GET(self):
        if logged(helper.PRIV_ADMIN):
            render = create_render()
    
            return render.data(session.uname, user_level[session.privilege],
                {
                  'active'    : 0,
                  'nonactive' : 0,
                  'admin'     : 0,
                  'sessions'  : 0,
                  'device'    : 0,
                  'todo'      : 0,
                  'sleep'     : 0,
                  'lock'      : 0,
                  'idle_time' : 0,
                })
        else:
            raise web.seeother('/')


#if __name__ == "__main__":
#   web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
#   app.run()
