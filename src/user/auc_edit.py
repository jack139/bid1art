# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 修改拍卖信息

url = ('/auc/edit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'ITEM'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(auc_id='', pos='')

        if user_data.auc_id=='':
            return render.info('错误的参数！')  

        # 获取拍卖信息
        r1, err = fork_api('/query/auction/info', {
            'id' : user_data.auc_id,
        })
        if err:
            return render.info(err)

        if r1['data']['auction']['status']!='WAIT':
            return render.info('拍卖申请开始审核，不能修改！') 

        # 检查发起者是否是艺术品所有人
        if r1['data']['auction']['seller_addr']!=helper.get_session_addr():
            return render.info('只有发起人可以修改拍卖信息！')

        # 获取艺术品信息
        r2, err = fork_api('/query/item/info', {
            'id' : r1['data']['auction']['item_id'],
        })
        if err:
            return render.info(err)

        # 获取拍卖行信息
        r3, err = fork_api('/query/auction_house/list', {})
        if err:
            return render.info(err)

        return render.auc_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['auction'], r2['data']['item'], r3['data']['ah_list'], user_data['pos'])


    def POST(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'ITEM'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(auc_id='', auc_house_id='', reserved_price='')

        if '' in [user_data.auc_id, user_data.auc_house_id, user_data.reserved_price]:
            return render.info('参数错误！')  

        try:
            float(user_data.reserved_price)
        except ValueError:
            return render.info('底价必须是数字！')  

        # 获取拍卖信息
        r1, err = fork_api('/query/auction/info', {
            'id' : user_data.auc_id,
        })
        if err:
            return render.info(err)

        if r1['data']['auction']['status']!='WAIT':
            return render.info('拍卖申请开始审核，不能修改！') 

        # 检查发起者是否是艺术品所有人
        if r1['data']['auction']['seller_addr']!=helper.get_session_addr():
            return render.info('只有发起人可以修改拍卖信息！')

        # 链上修改用户信息
        r1, err = fork_api('/biz/auction/modify', {
            'caller_addr'      : helper.get_session_addr(),
            'id'               : user_data['auc_id'],
            'auction_house_id' : user_data['auc_house_id'],
            'reserved_price'   : user_data['reserved_price'],
        })
        if err:
            return render.info(err)

        return render.info('成功保存！','/auc/list')
