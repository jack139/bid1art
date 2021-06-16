# -*- coding: utf-8 -*-
#
import web
import base64, os
from config import setting
import helper

from chain_api import fork_api

# 物品信息

url = ('/plat/get_image_by_item')

class handler:
    def GET(self):
        if not helper.logged():
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(item_id='')

        if user_data.item_id=='':
            return render.info('错误的参数！')  

        # 获取艺术品信息
        r1, err = fork_api('/query/item/info', {
            'id' : user_data.item_id,
        })
        if err:
            return render.info(err)

        # 检查是否有图片？
        if len(r1['data']['item']['image'])>0:
            # 获取图片
            r2, err = fork_api('/ipfs/download', {
                'hash' : r1['data']['item']['image'][0],
            })
            if err:
                return render.info(err)

            img_data = base64.b64decode(r2['data']['data'])
        else:
            # 没有图片，试用默认图片
            with open(os.path.join(setting.static_image_path, "wood-box.png"), 'rb') as f:
                img_data = f.read()

        if img_data[:2] == b'\xFF\xD8':
            web.header('Content-type', 'image/jpeg')
        elif img_data[:4] == b'\x89\x50\x4E\x47':
            web.header('Content-type', 'image/png')
        else:
            web.header('Content-type', 'application/octet-stream')

        return img_data
