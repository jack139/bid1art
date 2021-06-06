# -*- coding: utf-8 -*-
#
import web
import base64
from config import setting
import helper

from chain_api import fork_api

# 物品信息

url = ('/plat/get_image')

class handler:
    def GET(self):
        if not helper.logged():
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(hash='')

        if user_data.hash=='':
            return render.info('错误的参数！')  

        # 获取图片
        r1 = fork_api('/ipfs/download', {
            'hash' : user_data.hash,
        })
        if (r1 is None) or r1['code']!=0:
            return render.info('出错了，请联系管理员！(%s %s)'%\
                ((r1['code'], r1['msg']) if r1 else ('', '')))

        web.header('Content-Type', 'application/octet-stream')

        img_data = base64.b64decode(r1['data']['data'])

        return img_data
