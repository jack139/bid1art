# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 修改评论

url = ('/rev/edit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_REV, 'REV'): 
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(rev_id='', item_id='')

        if '' in (user_data.rev_id, user_data.item_id):
            return render.info('错误的参数！')  

        # 获取评论信息
        r1 = fork_api('/query/review/info', {
            'id'      : user_data.rev_id,
            'item_id' : user_data.item_id,
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        # 检查修改这是不是评论本人
        if r1['data']['review']['reviewer_addr']!=helper.get_session_addr():
            return render.info('只有评论本人可以修改！')

        # 获取艺术品信息
        r2 = fork_api('/query/item/info', {
            'id' : r1['data']['review']['item_id'],
        })
        if (r2 is None) or r2['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%((r2['code'], r2['msg']) if r2 else ('', '')))

        return render.rev_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            r1['data']['review'], r2['data']['item'])


    def POST(self):
        if not helper.logged(helper.PRIV_REV, 'REV'): 
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(rev_id='', item_id='', detail='')

        if '' in [user_data.rev_id, user_data.item_id, user_data.detail.strip()]:
            return render.info('参数错误！')  

        # 获取评论信息
        r1 = fork_api('/query/review/info', {
            'id'      : user_data.rev_id,
            'item_id' : user_data.item_id,
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        # 检查修改人是不是评论本人
        if r1['data']['review']['reviewer_addr']!=helper.get_session_addr():
            return render.info('只有发起人可以修改拍卖信息！')

        # 链上修改用户信息
        r1 = fork_api('/biz/review/modify', {
            'caller_addr' : helper.get_session_addr(),
            'id'          : user_data['rev_id'],
            'item_id'     : user_data['item_id'],
            'detail'      : user_data['detail'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.info('提交成功！','/item/info?item_id=%s'%user_data['item_id'])
