# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 拍卖列表

url = ('/auc/list')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        user_data=web.input(page='1', seller='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('page参数错误！')  

        # 链上数据
        if len(user_data['seller'])>0: # 发起者自己可以看到所有状态的自己的拍卖
            r1 = fork_api('/query/auction/list', {
                'page'  : int(user_data['page']),
                'limit' : setting.PAGE_SIZE,
                'seller_addr' : user_data['seller'],
            })
        else:
            r1 = fork_api('/query/auction/list_by_status', {
                'page'  : int(user_data['page']),
                'limit' : setting.PAGE_SIZE,
                'status' : 'ACTIVE|INIT|OPEN|CLOSE', # 可显示的状态
            })            
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.auc(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['auction_list'], int(user_data['page']), 
            len(r1['data']['auction_list'])==setting.PAGE_SIZE, len(user_data['seller']))
