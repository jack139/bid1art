# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 拍卖列表

url = ('/auc/list')

PAGE_SIZE = 8

class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        user_data=web.input(page='1', seller='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('page参数错误！')  

        # 链上数据
        r1 = fork_api('/query/auction/list', {
            'page'  : int(user_data['page']),
            'limit' : PAGE_SIZE,
            'seller_addr' : user_data['seller'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.auc(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['auction_list'], int(user_data['page']), 
            len(r1['data']['auction_list'])==PAGE_SIZE, len(user_data['seller']))
