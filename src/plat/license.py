#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 授权管理

url = ('/plat/license')

PAGE_SIZE = 30

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'EA_ADMIN'):
            raise web.seeother('/')
        user_data=web.input(page='0')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        # 分页获取数据
        db_sku = db.ea_license.find({},
            sort=[ ('status', -1) ],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        data = [ i for i in db_sku ]

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num // PAGE_SIZE + 1
        else:
            num = num // PAGE_SIZE
        
        return render.license(helper.get_session_uname(), helper.get_privilege_name(), data,
            range(0, num), int(user_data['page']))
