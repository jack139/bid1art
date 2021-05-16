# -*- coding: utf-8 -*-

# 本地调试
# uwsgi --http 127.0.0.1:8000  --wsgi-file bid1art.py --check-static ../

import web
import os, sys, gc
import time, json
from decimal import Decimal
from config.url import urls
from config import setting
from config.redissession import RedisStore
import helper
from libs import rand_code

from helper import get_privilege_name
from helper import logged
from helper import create_render

from chain_api import fork_api

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
            return render.portal(session.uname, get_privilege_name(), session.uid)
        else:
            render = create_render()
            signup=0

            # 生成验证码
            rand=helper.my_rand(4).upper()
            session.uid = rand # uid 临时存放验证码
            session.menu_level = 0 # 暂存输入验证码次数
            png2 = rand_code.gen_rand_png(rand)

            return render.login(signup, png2)

    def POST(self):
        chainaddr, passwd, rand = web.input().chainaddr, web.input().passwd, web.input().rand

        passwd = ' '.join(passwd.split()) # 去掉回车，只间隔一个空格
        name=''
        menu_level = 60*'-'
        menu_pri = []

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
            menu_pri=['ADMIN', 'USER_OP']

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
            menu_pri = []
            user_type = r1['data']['user']['user_type'].split('|')
            menu_pri = user_type[1:]
            if user_type[0] in ['TRD', 'DEL', 'ART']:
                privilege = helper.PRIV_TRD
            elif user_type[0] == 'AH':
                privilege = helper.PRIV_AH
            elif user_type[0] == 'REV':
                privilege = helper.PRIV_REV
            elif user_type[0] == 'OP': # 平台管理
                privilege = helper.PRIV_OP
            else:
                return render.login_error('用户权限错误！')

        for p in menu_pri:
            pos = helper.MENU_LEVEL[p]
            menu_level = menu_level[:pos]+'X'+menu_level[pos+1:]
        print(menu_level)


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


#if __name__ == "__main__":
#   web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
#   app.run()
