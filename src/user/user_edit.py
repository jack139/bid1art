# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 修改用户信息

url = ('/user/edit')

class handler:
    def GET(self):
        if not helper.logged():
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(uid='')

        if user_data.uid=='':
            return render.info('错误的参数！')  

        # 只能修改自己的用户信息
        if user_data.uid!=helper.get_session_addr():
            return render.info('无权修改！')  

        # 获取用户信息
        r1, err = fork_api('/query/user/info', {
            'chain_addr' : user_data.uid,
        })
        if err:
            return render.info(err)

        return render.user_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['user'], helper.user_type)


    def POST(self):
        if not helper.logged():
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(chain_addr='', bank_acc_name='', 
            bank_name='', bank_acc_no='', address='', phone='', email='')

        if user_data.chain_addr=='':
            return render.info('参数错误！')  

        # 只能修改自己的用户信息
        if user_data.chain_addr!=helper.get_session_addr():
            return render.info('无权修改！')  

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

        return render.info('成功保存！','/user/info?uid=%s'%helper.get_session_addr())
