# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 物品管理

url = ('/item/edit')


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

        # 检查是否可修改
        if r1['data']['item']['status'] not in ('WAIT', 'ACTIVE', 'NOGO'):
            return render.info('目前艺术品的状态，不能修改艺术品信息！')              

        return render.item_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['item'])

    def POST(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'ITEM'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(item_id='', owner_addr='', desc='', detail='', date='', type='', subject='', media='', size='', base_price='')

        if '' in [user_data.owner_addr, user_data.item_id]:
            return render.info('参数错误！')  

        # 获取用户信息
        r1 = fork_api('/query/item/info', {
            'id' : user_data.item_id,
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r1['code'], r1['msg']) if r1 else ('', '')))

        # 检查是否可修改
        if r1['data']['item']['status'] not in ('WAIT', 'ACTIVE', 'NOGO'):
            return render.info('目前艺术品的状态，不能修改艺术品信息！')              

        # 链上修改用户信息
        r1 = fork_api('/biz/item/modify', {
            'caller_addr': helper.get_session_addr(),
            'id'         : user_data['item_id'],
            'desc'       : user_data['desc'],
            'detail'     : user_data['detail'],
            'date'       : user_data['date'],
            'type'       : user_data['type'],
            'subject'    : user_data['subject'],
            'media'      : user_data['media'],
            'size'       : user_data['size'],
            'base_price' : user_data['base_price'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.info('成功保存！','/item/list')
