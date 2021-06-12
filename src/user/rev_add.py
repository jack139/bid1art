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
        r1, err = fork_api('/query/item/info', {
            'id' : user_data.item_id,
        })
        if err:
            return render.info(err)

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
        r1, err = fork_api('/biz/review/new', {
            'caller_addr'   : helper.get_session_addr(),
            'reviewer_addr' : helper.get_session_addr(),
            'item_id'       : user_data['item_id'],
            'detail'        : user_data['detail'],
        })
        if err:
            return render.info(err)

        return render.info('提交成功！','/item/info?item_id=%s'%user_data['item_id'])
