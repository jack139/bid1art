# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 审核评论

url = ('/plat/rev_audit_edit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_OP, 'REV_OP'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(rev_id='', item_id='')

        if '' in (user_data.rev_id, user_data.item_id):
            return render.info('错误的参数！')  

        # 获取用户信息
        r1, err = fork_api('/query/review/info', {
            'id' : user_data.rev_id,
            'item_id' : user_data.item_id,
        })
        if err:
            return render.info(err)

        # 获取艺术品信息
        r2, err = fork_api('/query/item/info', {
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

        return render.rev_audit_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['review'], r2['data']['item'], status_list)


    def POST(self):
        if not helper.logged(helper.PRIV_OP, 'REV_OP'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(rev_id='', item_id='', status='')

        if '' in (user_data.rev_id, user_data.item_id, user_data.status):
            return render.info('参数错误！')  

        # 链上修改用户信息
        r1, err = fork_api('/biz/audit/review', {
            'caller_addr': helper.get_session_addr(),
            'id'         : user_data['rev_id'],
            'item_id'    : user_data['item_id'],
            'status'     : user_data['status'],
        })
        if err:
            return render.info(err)

        return render.info('成功保存！','/plat/rev_audit')
