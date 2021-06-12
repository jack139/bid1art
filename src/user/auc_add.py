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

        # 检查艺术品状态
        if r1['data']['item']['status']!='ACTIVE':
            return render.info('艺术品状态不是ACTIVE，不能申请拍卖！')

        # 获取拍卖行信息
        r2 = fork_api('/query/auction_house/list', {})
        if (r2 is None) or r2['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r2['code'], r2['msg']) if r2 else ('', '')))

        return render.auc_new(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(), 
            r1['data']['item'], r2['data']['ah_list'])


    def POST(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(auc_house_id='', reserved_price='', item_id='')

        if '' in [user_data.auc_house_id, user_data.reserved_price, user_data.item_id]:
            return render.info('拍卖行id、底价均不能为空！')  

        try:
            float(user_data.reserved_price)
        except ValueError:
            return render.info('底价必须是数字！')  

        # 获取用户信息
        r1 = fork_api('/query/item/info', {
            'id' : user_data.item_id,
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        # 检查发起者是否是艺术品所有人
        if r1['data']['item']['owner_addr']!=helper.get_session_addr():
            return render.info('只有艺术品所有人可以发起拍卖！')

        # 检查艺术品状态
        if r1['data']['item']['status']!='ACTIVE':
            return render.info('艺术品状态不是ACTIVE，不能申请拍卖！')

        # 链上新建用户
        r1 = fork_api('/biz/auction/new', {
            'caller_addr'      : helper.get_session_addr(),
            'seller_addr'      : helper.get_session_addr(),
            'auction_house_id' : user_data['auc_house_id'],
            'item_id'          : user_data['item_id'],
            'reserved_price'   : user_data['reserved_price'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.info('提交成功！','/auc/list')
