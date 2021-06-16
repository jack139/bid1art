# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 买家付款（线下付，这里只改状态）

url = ('/trans/pay')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(trans_id='')

        if user_data.trans_id=='':
            return render.info('错误的参数！')  

        # 获取成交信息
        r3, err = fork_api('/query/trans/info', {
            'id' : user_data.trans_id,
        })
        if err:
            return render.info(err)

        # 只能看自己参与的交易
        if helper.get_session_addr() != r3['data']['trans']['buyer_addr']:
            return render.info('错误的交易编码！')        

        # 链上新建用户
        r1, err = fork_api('/biz/audit/trans', {
            'caller_addr' : helper.get_session_addr(),
            'id'          : user_data['trans_id'],
            'status'      : 'PAID',
            'action'      : 'pay',
        })
        if err:
            return render.info(err)

        return render.info('买家已付款！','/trans/info?trans_id=%s'%user_data['trans_id'])

