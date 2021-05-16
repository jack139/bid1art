# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 新建拍卖请求

url = ('/auc/add')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
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

        # 检查发起者是否是艺术品所有人
        if r1['data']['item']['owner_addr']!=helper.get_session_addr():
            return render.info('只有所有人可以发起拍卖！')

        render = helper.create_render()
        return render.auc_new(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(), 
            r1['data']['item'])


    def POST(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(owner_addr='', auc_house_id='', reserved_price='', item_id='')
        print(user_data)

        if user_data.owner_addr!=helper.get_session_addr():
            return render.info('只有所有人可以发起拍卖！')

        if '' in [user_data.owner_addr, user_data.auc_house_id, user_data.reserved_price, user_data.item_id]:
            return render.info('所有者链地址、拍卖行id、底价均不能为空！')  

        # 链上新建用户
        r1 = fork_api('/biz/auction/new', {
            'seller_addr'    : user_data['seller_addr'],
            'auc_house_id'   : user_data['auc_house_id'],
            'item_id'        : user_data['item_id'],
            'reserved_price' : user_data['reserved_price'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.info('提交成功！','/auc/list')
