# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 审核成交交易

url = ('/plat/trans_audit_edit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_AH, 'AUC_OP'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(trans_id='')

        if user_data.trans_id=='':
            return render.info('错误的参数！')  

        # 获取交易信息
        r3, err = fork_api('/query/trans/info', {
            'id' : user_data.trans_id,
        })
        if err:
            return render.info(err)

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

        status_list = [
            ('WAIT', '待审核'),
            ('PAID', '已付款'),
            ('CHANGED', '变更所有权'),
            ('DELIVERY', '买家已收货'),
            ('PAYBACK', '向卖家付款'),
            ('ONWAY', '已发货'),
            ('LOCK', '锁定'),
        ]

        return render.trans_audit_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r3['data']['trans'], r1['data']['auction'], r2['data']['item'], status_list)


    def POST(self):
        if not helper.logged(helper.PRIV_AH, 'AUC_OP'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(trans_id='', status='')

        if '' in (user_data.trans_id, user_data.status):
            return render.info('参数错误！')  

        # 获取交易信息
        r3, err = fork_api('/query/trans/info', {
            'id' : user_data.trans_id,
        })
        if err:
            return render.info(err)


        if user_data.status=='CHANGED': 
            if r3['data']['trans']['status']!='PAID':
                return render.info('交易状态不是PAID，不能修改所有人！')  

            # 改变物品所有人
            r2, err = fork_api('/biz/item/change_owner', {
                'caller_addr': helper.get_session_addr(),
                'id'         : r3['data']['trans']['item_id'],
                'owner_addr' : r3['data']['trans']['buyer_addr'],
            })
            if err:
                return render.info(err)


        # 链上修改拍卖状态
        r1, err = fork_api('/biz/audit/trans', {
            'caller_addr': helper.get_session_addr(),
            'id'         : user_data['trans_id'],
            'status'     : user_data['status'],
            'action'     : user_data['status'].lower(),
        })
        if err:
            return render.info(err)

        return render.info('成功保存！','/plat/trans_audit')
