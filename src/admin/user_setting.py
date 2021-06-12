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
            r1, err = fork_api('/query/user/info', {
                'chain_addr' : user_data.uid,
            })
            if err:
                return render.info(err)

            status_list = [
                ('WAIT', '待审核'),
                ('ACTIVE', '正常使用'),
                ('NOGO', '审核不通过'),
                ('LOCK', '锁定'),
            ]

            return render.user_setting(helper.get_session_uname(), helper.get_privilege_name(), 
                r1['data']['user'], status_list)
        else:
            raise web.seeother('/')

    def POST(self):
        if logged(helper.PRIV_ADMIN|helper.PRIV_OP, 'USER_OP'):
            render = create_render()
            user_data=web.input(chain_addr='', bank_acc_name='', 
                bank_name='', bank_acc_no='', address='', phone='', email='', status='')

            if user_data.chain_addr=='':
                return render.info('参数错误！')  

            # 链上修改用户信息
            r1, err = fork_api('/biz/user/modify', {
                'caller_addr'   : helper.get_session_addr(),
                'chain_addr'    : user_data['chain_addr'],
                'bank_acc_name' : user_data['bank_acc_name'],
                'bank_name'     : user_data['bank_name'],
                'bank_acc_no'   : user_data['bank_acc_no'],
                'address'       : user_data['address'],
                'phone'         : user_data['phone'],
                'email'         : user_data['email'],
            })
            if err:
                return render.info(err)

            # 链上修改用户信息
            r1, err = fork_api('/biz/audit/user', {
                'caller_addr': helper.get_session_addr(),
                'chain_addr' : user_data['chain_addr'],
                'status'     : user_data['status'],
            })
            if err:
                return render.info(err)

            return render.info('成功保存！','/admin/user')
        else:
            raise web.seeother('/')
