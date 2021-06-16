# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 物品信息

url = ('/item/info')

class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'ITEM'):
            if not helper.logged(helper.PRIV_REV, 'REV'): # REV 可以浏览
                if not helper.logged(helper.PRIV_AH, 'AUC_OP'):
                    if not helper.logged(helper.PRIV_OP, 'ITEM_OP'):
                        raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(item_id='', pos='')

        if user_data.item_id=='':
            return render.info('错误的参数！')  

        # 获取艺术品信息
        r1, err = fork_api('/query/item/info', {
            'id' : user_data.item_id,
        })
        if err:
            return render.info(err)

        # 获取评论信息
        if helper.logged(helper.PRIV_REV, 'REV'): # REV 可以看到未审核的评论
            rev_status = 'ACTIVE|WAIT'
        else:
            rev_status = 'ACTIVE'
        r2, err = fork_api('/query/review/list', {
            'item_id' : user_data.item_id,
            'status'  : rev_status,
            'page'    : 1,
            'limit'   : 1000,
        })
        if err:
            return render.info(err)

        return render.item_info(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['item'], r2['data']['review_list'], user_data['pos'])
