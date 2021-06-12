# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 评论审核

url = ('/plat/rev_audit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_OP, 'REV_OP'):
            raise web.seeother('/')

        user_data=web.input(page='1')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('page参数错误！')  

        # 链上数据
        r1, err = fork_api('/query/review/list_by_status', {
            'page'   : int(user_data['page']),
            'limit'  : setting.PAGE_SIZE,
            'status' : 'WAIT'
        })
        if err:
            return render.info(err)

        return render.rev_audit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['review_list'], int(user_data['page']), len(r1['data']['review_list'])==setting.PAGE_SIZE)
