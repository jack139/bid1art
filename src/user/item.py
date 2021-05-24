# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 物品管理

url = ('/item/list')



class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'ITEM'):
            raise web.seeother('/')

        user_data=web.input(page='1', owner='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('page参数错误！')  

        # 链上数据
        r1 = fork_api('/query/item/list', {
            'page'  : int(user_data['page']),
            'limit' : setting.PAGE_SIZE,
            'owner_addr' : user_data['owner'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        items=[]
        for u in r1['data']['item_list']:
            items.append([u['id'],u['desc'],u['status']])

        return render.item(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            items, int(user_data['page']), len(items)==setting.PAGE_SIZE, len(user_data['owner']))

