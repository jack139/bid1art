# -*- coding: utf-8 -*-
#
import os
import web
from config import setting
import helper

from helper import logged
from helper import create_render


# 数据统计

url = ('/admin/data')

class handler:
    def GET(self):
        if logged(helper.PRIV_ADMIN|helper.PRIV_OP):
            render = create_render()
    
            return render.data(helper.get_session_uname(), helper.get_privilege_name(),
                {
                    'active'    : 0,
                    'nonactive' : 0,
                    'admin'     : 0,
                    'sessions'  : 0,
                    'device'    : 0,
                    'todo'      : 0,
                    'sleep'     : 0,
                    'lock'      : 0,
                    'idle_time' : 0,
                })
        else:
            raise web.seeother('/')
