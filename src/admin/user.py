# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from helper import logged
from helper import create_render

from chain_api import fork_api

# 用户管理

url = ('/admin/user')


class handler:
    def GET(self):
        if logged(helper.PRIV_ADMIN|helper.PRIV_OP, 'USER_OP'):
            user_data=web.input(page='1')
            render = create_render()

            if not user_data['page'].isdigit():
                return render.info('page参数错误！')  

            # 链上用户列表
            r1, err = fork_api('/query/user/list', {
                'page'  : int(user_data['page']),
                'limit' : setting.PAGE_SIZE,
            })
            if err:
                return render.info(err)

            users=[]
            for u in r1['data']['user_list']:
                users.append([u['login_name'],u['chain_addr'],u['user_type'],u['reg_date'],u['status']])

            return render.user(helper.get_session_uname(), helper.get_privilege_name(), users, 
                int(user_data['page']), len(users)==setting.PAGE_SIZE)
        else:
            raise web.seeother('/')

