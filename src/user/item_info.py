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
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(item_id='')

        if user_data.item_id=='':
            return render.info('错误的参数！')  

        # 获取用户信息
        r1 = fork_api('/query/item/info', {
            'id' : user_data.item_id,
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.item_info(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['item'])