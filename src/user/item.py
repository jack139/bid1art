# -*- coding: utf-8 -*-
#
import web
import json
from config import setting
import helper

from chain_api import fork_api

# 物品管理

url = ('/item/list')



class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART|helper.PRIV_REV, 'ITEM'):
            if not helper.logged(helper.PRIV_REV, 'REV'): # REV 可以浏览
                raise web.seeother('/')

        user_data=web.input(page='1', owner='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('page参数错误！')  

        # 链上数据
        if len(user_data['owner'])>0: # 指定owner的所有艺术品
            r1, err = fork_api('/query/item/list', {
                'page'  : int(user_data['page']),
                'limit' : setting.PAGE_SIZE,
                'owner_addr' : user_data['owner'],
            })
        else: # 不限owner, 非 WAIT的
            r1, err = fork_api('/query/item/list_by_status', {
                'page'  : int(user_data['page']),
                'limit' : setting.PAGE_SIZE,
                'status' : 'ACTIVE|ONBID', # 显示 正常的 和 竞标中 的
            })
        if err:
            return render.info(err)

        items=[]
        for u in r1['data']['item_list']:
            items.append([u['id'],u['desc'],u['status'],
                json.loads(u['image']) if len(u['image'])>2 else [],
                u['detail']
            ])

        return render.item(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            items, int(user_data['page']), len(items)==setting.PAGE_SIZE, len(user_data['owner']))

