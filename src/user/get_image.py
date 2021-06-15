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
        r1, err = fork_api('/ipfs/download', {
            'hash' : user_data.hash,
        })
        if err:
            return render.info(err)

        img_data = base64.b64decode(r1['data']['data'])

        if img_data[:2] == b'\xFF\xD8':
            web.header('Content-type', 'image/jpeg')
        elif img_data[:4] == b'\x89\x50\x4E\x47':
            web.header('Content-type', 'image/png')
        else:
            web.header('Content-type', 'application/octet-stream')

        return img_data
