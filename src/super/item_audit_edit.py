# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 审核艺术品

url = ('/plat/item_audit_edit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_OP, 'ITEM_OP'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(item_id='')

        if user_data.item_id=='':
            return render.info('错误的参数！')  

        # 获取用户信息
        r1, err = fork_api('/query/item/info', {
            'id' : user_data.item_id,
        })
        if err:
            return render.info(err)

        status_list = [
            ('WAIT', '待审核'),
            ('ACTIVE', '正常使用'),
            ('NOGO', '审核不通过'),
            ('LOCK', '锁定'),
        ]

        return render.item_audit_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['item'], status_list)


    def POST(self):
        if not helper.logged(helper.PRIV_OP, 'ITEM_OP'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(item_id='', status='')

        if '' in [user_data.item_id, user_data.status]:
            return render.info('参数错误！')  

        # 链上修改用户信息
        r1, err = fork_api('/biz/audit/item', {
            'caller_addr': helper.get_session_addr(),
            'id'         : user_data['item_id'],
            'status'     : user_data['status'],
        })
        if err:
            return render.info(err)

        return render.info('成功保存！','/plat/item_audit')
