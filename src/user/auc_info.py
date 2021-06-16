# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 物品信息

url = ('/auc/info')

class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            if not helper.logged(helper.PRIV_AH, 'AUC_OP'):
                raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(auc_id='', pos='')

        if user_data.auc_id=='':
            return render.info('错误的参数！')  

        # 获取拍卖信息
        r1, err = fork_api('/query/auction/info', {
            'id' : user_data.auc_id,
        })
        if err:
            return render.info(err)

        # 获取艺术品信息
        r2, err = fork_api('/query/item/info', {
            'id' : r1['data']['auction']['item_id'],
        })
        if err:
            return render.info(err)

        # 获取出价清单
        r3, err = fork_api('/query/bid/list', {
            'auction_id' : user_data.auc_id,
            'status'     : 'ACTIVE|WITHDRAW',
            'page'       : 1,
            'limit'      : 2000, # TODO: 如果超过2000个出价，会有显示问题
        })
        if err:
            return render.info(err)

        r3['data']['bid_list'] = sorted(r3['data']['bid_list'], key=lambda x: x['bid_time'], reverse=True)

        return render.auc_info(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['auction'], r2['data']['item'], r3['data']['bid_list'], user_data['pos'])
