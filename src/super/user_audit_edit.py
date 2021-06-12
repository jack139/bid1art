# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 审核用户

url = ('/plat/user_audit_edit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_OP, 'USER_OP'):
            raise web.seeother('/')

        render = helper.create_render()
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

        return render.user_audit_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['user'], status_list)


    def POST(self):
        if not helper.logged(helper.PRIV_OP, 'USER_OP'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(chain_addr='', status='')

        if '' in [user_data.chain_addr, user_data.status]:
            return render.info('参数错误！')  

        # 链上修改用户信息
        r1, err = fork_api('/biz/audit/user', {
            'caller_addr': helper.get_session_addr(),
            'chain_addr' : user_data['chain_addr'],
            'status'     : user_data['status'],
        })
        if err:
            return render.info(err)

        return render.info('成功保存！','/plat/user_audit')
