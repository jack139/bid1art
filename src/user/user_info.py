# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 用户信息

url = ('/user/info')

class handler:
    def GET(self):
        if not helper.logged():
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(uid='')

        if user_data.uid=='':
            return render.info('错误的参数！')  

        # 非管理员只能看自己的用户信息
        if (not helper.logged(helper.PRIV_AH|helper.PRIV_OP)) and user_data.uid!=helper.get_session_addr():
            return render.info('无权查看！')  

        # 获取用户信息
        r1, err = fork_api('/query/user/info', {
            'chain_addr' : user_data.uid,
        })
        if err:
            return render.info(err)

        # 获取用户账户
        r2, err = fork_api('/query/user/credit_balance', {
            'chain_addr' : user_data.uid,
        })
        if err:
            return render.info(err)

        return render.user_info(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['user'], helper.user_type, r2['data']['balance'])
