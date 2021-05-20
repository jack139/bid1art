# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from helper import logged
from helper import create_render

from chain_api import fork_api

# 用户管理

url = ('/admin/user_setting')


class handler:
    def GET(self):
        if logged(helper.PRIV_ADMIN|helper.PRIV_OP, 'USER_OP'):
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

            return render.user_setting(helper.get_session_uname(), helper.get_privilege_name(), r1['data']['user'])
        else:
            raise web.seeother('/')

    def POST(self):
        if logged(helper.PRIV_ADMIN|helper.PRIV_OP, 'USER_OP'):
            render = create_render()
            user_data=web.input(chain_addr='', bank_acc_name='', 
                bank_name='', bank_acc_no='', address='', phone='', email='')

            if user_data.chain_addr=='':
                return render.info('参数错误！')  

            # 链上修改用户信息
            r1 = fork_api('/biz/user/modify', {
                'caller_addr'   : helper.get_session_addr(),
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
