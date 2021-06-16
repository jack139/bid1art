# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 审核、处理成交交易

url = ('/plat/trans_audit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_AH, 'AUC_OP'):
            raise web.seeother('/')

        user_data=web.input(page='1')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('page参数错误！')  

        # 链上数据
        r1, err = fork_api('/query/trans/list_by_condition', {
            'page'   : int(user_data['page']),
            'limit'  : setting.PAGE_SIZE,
            'cate'   : 'status',
            'condition' : 'PAID|CHANGED|DELIVERY'
        })
        if err:
            return render.info(err)

        return render.trans_audit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['trans_list'], int(user_data['page']), len(r1['data']['trans_list'])==setting.PAGE_SIZE)
