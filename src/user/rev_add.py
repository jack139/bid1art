# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from chain_api import fork_api

# 新建评论

url = ('/rev/add')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_REV, 'REV'): 
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


        render = helper.create_render()
        return render.rev_new(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(), 
            r1['data']['item'])


    def POST(self):
        if not helper.logged(helper.PRIV_REV, 'REV'): 
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(detail='', item_id='')

        if '' in [user_data.detail.strip(), user_data.item_id]:
            return render.info('评论内容不能为空！')  


        # 链上新建用户
        r1 = fork_api('/biz/review/new', {
            'caller_addr'   : helper.get_session_addr(),
            'reviewer_addr' : helper.get_session_addr(),
            'item_id'       : user_data['item_id'],
            'detail'        : user_data['detail'],
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

        return render.info('提交成功！','/item/info?item_id=%s'%user_data['item_id'])
