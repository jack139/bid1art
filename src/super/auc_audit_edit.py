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

        if '' in (user_data.auc_id, user_data.open_date, user_data.close_date, user_data.status):
            return render.info('拍卖起始日期不能为空！')  

        if user_data.open_date > user_data.close_date:
            return render.info('拍卖开始时间不能大于拍卖截止时间！')  

        # 链上修改用户信息
        r1 = fork_api('/biz/audit/auction', {
            'caller_addr': helper.get_session_addr(),
            'id'         : user_data['auc_id'],
            'status'     : user_data['status'],
            'open_date'  : user_data['open_date'],
            'close_date' : user_data['close_date'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.info('成功保存！','/plat/auc_audit')
