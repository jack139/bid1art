# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 新建出价

url = ('/bid/new')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(auc_id='')

        if user_data.auc_id=='':
            return render.info('错误的参数！')  

        # 获取拍卖信息
        r1 = fork_api('/query/auction/info', {
            'id' : user_data.auc_id,
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r1['code'], r1['msg']) if r1 else ('', '')))

        # 检查艺术品状态
        if r1['data']['auction']['status']!='OPEN':
            return render.info('拍卖状态不是OPEN，不能出价！')

        # 检查出价者是否是卖家
        if r1['data']['auction']['seller_addr']==helper.get_session_addr():
            return render.info('卖家不能出价！')

        # 获取物品信息
        r2 = fork_api('/query/item/info', {
            'id' : r1['data']['auction']['item_id'],
        })
        if (r2 is None) or r2['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r2['code'], r2['msg']) if r2 else ('', '')))

        # 检查出价者是否是艺术品所有人
        if r2['data']['item']['owner_addr']==helper.get_session_addr():
            return render.info('艺术品所有人不能出价！')

        return render.bid_new(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(), 
            r1['data']['auction'], r2['data']['item'])


    def POST(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'AUC'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(bid_price='', auc_id='')

        if '' in [user_data.auc_id, user_data.bid_price]:
            return render.info('出价不能为空！')  

        try:
            float(user_data.bid_price)
        except ValueError:
            return render.info('出价必须是数字！')  

        # 获取拍卖信息
        r1 = fork_api('/query/auction/info', {
            'id' : user_data.auc_id,
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r1['code'], r1['msg']) if r1 else ('', '')))

        # 检查艺术品状态
        if r1['data']['auction']['status']!='OPEN':
            return render.info('拍卖状态不是OPEN，不能出价！')

        # 检查出价者是否是卖家
        if r1['data']['auction']['seller_addr']==helper.get_session_addr():
            return render.info('卖家不能出价！')

        # 获取出价清单
        r3 = fork_api('/query/bid/list', {
            'auction_id' : user_data.auc_id,
            'status'     : 'ACTIVE|WITHDRAW',
            'page'       : 1,
            'limit'      : 2000, # TODO: 如果超过2000个出价，会有显示问题
        })
        if (r3 is None) or r3['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r3['code'], r3['msg']) if r3 else ('', '')))

        # 检查出价必须大于底价
        if float(user_data['bid_price'])<float(r1['data']['auction']['reserved_price']):
            return render.info('出价必须拍卖底价！(%.2f)'%float(r1['data']['auction']['reserved_price']))

        # 检查出价大于最高价
        r3['data']['bid_list'] = sorted(r3['data']['bid_list'], key=lambda x: float(x['bid_price']), reverse=True)
        if len(r3['data']['bid_list'])>0:
            if float(user_data['bid_price'])<=float(r3['data']['bid_list'][0]['bid_price']):
                return render.info('出价必须高于历史出价！(%.2f)'%float(r3['data']['bid_list'][0]['bid_price']))

        # 链上新建用户
        r1 = fork_api('/biz/auction/bid', {
            'caller_addr' : helper.get_session_addr(),
            'buyer_addr'  : helper.get_session_addr(),
            'auction_id'  : user_data['auc_id'],
            'bid_price'   : user_data['bid_price'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.info('提交成功！','/auc/info?auc_id=%s'%user_data['auc_id'])
