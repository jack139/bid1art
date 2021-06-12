# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 审核拍卖申请

url = ('/plat/auc_audit_edit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_AH, 'AUC_OP'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(auc_id='')

        if user_data.auc_id=='':
            return render.info('错误的参数！')  

        # 获取用户信息
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

        status_list = [
            ('WAIT', '待审核'),
            ('INIT', '审核通过'),
            ('NOGO', '审核不通过'),
            ('LOCK', '锁定'),
        ]

        return render.auc_audit_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['auction'], r2['data']['item'], status_list)


    def POST(self):
        if not helper.logged(helper.PRIV_AH, 'AUC_OP'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(auc_id='', open_date='', close_date='', status='')

        if '' in (user_data.auc_id, user_data.status):
            return render.info('参数错误！')  

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

        # 只有艺术品是active时才能审核拍卖
        if r2['data']['item']['status']!='ACTIVE':
            return render.info('艺术品状态是%s，需要等待审核艺术品！'%r2['data']['item']['status']) 

        if user_data.status=='INIT':
            if '' in (user_data.open_date, user_data.close_date):
                return render.info('拍卖起始日期不能为空！')  

            if user_data.open_date > user_data.close_date:
                return render.info('拍卖开始时间不能大于拍卖截止时间！')  


        # 链上修改拍卖状态
        r3, err = fork_api('/biz/audit/auction', {
            'caller_addr': helper.get_session_addr(),
            'id'         : user_data['auc_id'],
            'status'     : user_data['status'],
            'open_date'  : user_data['open_date'],
            'close_date' : user_data['close_date'],
        })
        if err:
            return render.info(err)

        if user_data.status=='INIT':
            # 链上修改艺术品状态信息
            r3, err = fork_api('/biz/audit/item', {
                'caller_addr': helper.get_session_addr(),
                'id'         : r1['data']['auction']['item_id'],
                'status'     : 'ONBID',
            })
            if err:
                return render.info(err)

        return render.info('成功保存！','/plat/auc_audit')
