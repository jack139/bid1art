# -*- coding: utf-8 -*-
#
import os
import web
from config import setting
import helper

from helper import logged
from helper import create_render


# 系统状态

url = ('/admin/status')

class handler:
    def GET(self):
        if logged(helper.PRIV_ADMIN|helper.PRIV_OP):
            render = create_render()
        
            uptime=os.popen('uptime').readlines()
            takit=os.popen('pgrep -f "uwsgi_*.sock"').readlines()
            error_log=os.popen('tail %s/error.log' % setting.logs_path).readlines()
            uwsgi_log=os.popen('tail %s/uwsgi_fair.log' % setting.logs_path).readlines()
            df_data=os.popen('df -h').readlines()

            return render.status(helper.get_session_uname(), helper.get_privilege_name(),{
                'uptime'      : uptime,
                'takit'       : takit,
                'error_log'   : error_log,
                'uwsgi_log'   : uwsgi_log,
                'df_data'     : df_data})
        else:
            raise web.seeother('/')
