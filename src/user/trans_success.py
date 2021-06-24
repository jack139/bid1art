# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 卖家确认收款（线下，这里只改状态）

url = ('/trans/success')


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

        # 获取艺术品信息
        r2, err = fork_api('/query/item/info', {
            'id' : r3['data']['trans']['item_id'],
        })
        if err:
            return render.info(err)

        # 只能看自己参与的交易
        if helper.get_session_addr() != r3['data']['trans']['seller_addr']:
            return render.info('错误的交易编码！')        

        # 链上修改订单状态
        r1, err = fork_api('/biz/audit/trans', {
            'caller_addr' : helper.get_session_addr(),
            'id'          : user_data['trans_id'],
            'status'      : 'SUCCESS',
            'action'      : 'success',
        })
        if err:
            return render.info(err)

        if r2['data']['item']['status']=='ONBID':
            # 链上修改艺术品状态信息
            r1, err = fork_api('/biz/audit/item', {
                'caller_addr': helper.get_session_addr(),
                'id'         : r3['data']['trans']['item_id'],
                'status'     : 'ACTIVE',
                'action'     : 'transaction complete',
            })
            if err:
                return render.info(err)

        return render.info('卖家已确认收款！','/trans/info?trans_id=%s'%user_data['trans_id'])
