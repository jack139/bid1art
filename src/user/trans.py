# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 拍卖列表

url = ('/trans/list')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        user_data=web.input(page='1', seller='', buyer='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('page参数错误！')  

        if user_data['buyer']=='' and user_data['seller']=='':
            return render.info('参数错误！')  

        # 链上数据
        if len(user_data['seller'])>0: # 发起者自己可以看到所有状态的自己的拍卖
            r1, err = fork_api('/query/trans/list_by_condition', {
                'page'  : int(user_data['page']),
                'limit' : setting.PAGE_SIZE,
                'cate'  : 'seller',
                'condition' : helper.get_session_addr(),
            })
        else:
            r1, err = fork_api('/query/trans/list_by_condition', {
                'page'  : int(user_data['page']),
                'limit' : setting.PAGE_SIZE,
                'cate'  : 'buyer',
                'condition' : helper.get_session_addr(),
            })
        if err:
            return render.info(err)

        return render.trans(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['trans_list'], int(user_data['page']), 
            len(r1['data']['trans_list'])==setting.PAGE_SIZE, len(user_data['buyer'])>0)
