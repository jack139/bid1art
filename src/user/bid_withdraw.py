# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 撤销出价

url = ('/bid/withdraw')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(auc_id='', bid_id='')

        if '' in (user_data.auc_id, user_data.bid_id):
            return render.info('错误的参数！')  

        # 链上新建用户
        r1 = fork_api('/biz/auction/bid/withdraw', {
            'caller_addr' : helper.get_session_addr(),
            'auction_id'  : user_data['auc_id'],
            'id'          : user_data['bid_id'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.info('出价已撤销！','/auc/info?auc_id=%s'%user_data['auc_id'])

