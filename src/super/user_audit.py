# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 用户审核

url = ('/plat/user_audit')

PAGE_SIZE = 8

class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_OP, 'USER_OP'):
            raise web.seeother('/')

        render = helper.create_render()

        # 链上数据
        r1 = fork_api('/query/audit/user/list', {
            'status' : 'WAIT'
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.user_audit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['user_list'])
