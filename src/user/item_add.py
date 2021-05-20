# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 物品管理

url = ('/item/add')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'ITEM'):
            raise web.seeother('/')

        render = helper.create_render()
        return render.item_new(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr())


    def POST(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'ITEM'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(owner_addr='', desc='', 
            detail='', date='', type='', subject='', media='', size='', base_price='')
        print(user_data)

        if '' in [user_data.owner_addr, user_data.desc, user_data.date]:
            return render.info('物品名称、所有者链地址、年代均不能为空！')  

        # 链上新建用户
        r1 = fork_api('/biz/item/new', {
            'caller_addr'  : helper.get_session_addr(),
            'owner_addr'   : user_data['owner_addr'],
            'desc'         : user_data['desc'],
            'detail'       : user_data['detail'],
            'date'         : user_data['date'],
            'type'         : user_data['type'],
            'subject'      : user_data['subject'],
            'media'        : user_data['media'],
            'size'         : user_data['size'],
            'base_price'   : user_data['base_price'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.info('提交成功！','/item/list')
