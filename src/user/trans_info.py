# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 成交交易信息

url = ('/trans/info')

class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(trans_id='', pos='')

        if user_data.trans_id=='':
            return render.info('错误的参数！')  

        # 获取成交信息
        r3, err = fork_api('/query/trans/info', {
            'id' : user_data.trans_id,
        })
        if err:
            return render.info(err)

        # 只能看自己参与的交易
        if helper.get_session_addr() not in (r3['data']['trans']['seller_addr'], r3['data']['trans']['buyer_addr']):
            return render.info('错误的交易编码！')        

        # 获取拍卖信息
        r1, err = fork_api('/query/auction/info', {
            'id' : r3['data']['trans']['auction_id'],
        })
        if err:
            return render.info(err)

        # 获取艺术品信息
        r2, err = fork_api('/query/item/info', {
            'id' : r1['data']['auction']['item_id'],
        })
        if err:
            return render.info(err)

        return render.trans_info(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['auction'], r2['data']['item'], r3['data']['trans'], user_data['pos'])
