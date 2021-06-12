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
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(auc_id='')

        if user_data.auc_id=='':
            return render.info('错误的参数！')  

        # 获取拍卖信息
        r1 = fork_api('/query/auction/info', {
            'id' : user_data.auc_id,
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r1['code'], r1['msg']) if r1 else ('', '')))

        # 获取艺术品信息
        r2 = fork_api('/query/item/info', {
            'id' : r1['data']['auction']['item_id'],
        })
        if (r2 is None) or r2['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r2['code'], r2['msg']) if r2 else ('', '')))

        # 获取出价清单
        r3 = fork_api('/query/bid/list', {
            'auction_id' : user_data.auc_id,
            'status'     : 'ACTIVE|WITHDRAW',
            'page'       : 1,
            'limit'      : 2000, # TODO: 如果超过2000个出价，会有显示问题
        })
        if (r3 is None) or r3['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r3['code'], r3['msg']) if r3 else ('', '')))

        r3['data']['bid_list'] = sorted(r3['data']['bid_list'], key=lambda x: x['bid_time'], reverse=True)

        return render.auc_info(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['auction'], r2['data']['item'], r3['data']['bid_list'])