# -*- coding: utf-8 -*-
#
import web 
import os, base64
from config import setting
import helper

from chain_api import fork_api

# 物品管理

url = ('/item/edit')


class handler:
    def GET(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'ITEM'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(item_id='')

        item_data = { 'id':'n/a', 'owner_addr':helper.get_session_addr()}

        if user_data.item_id!='':
            # 获取用户信息
            r1 = fork_api('/query/item/info', {
                'id' : user_data.item_id,
            })
            if (r1 is None) or r1['code']!=0:
                return render.info('出错了，请联系管理员！(%s %s)'%\
                    ((r1['code'], r1['msg']) if r1 else ('', '')))

            # 检查是否可修改
            if r1['data']['item']['status'] not in ('WAIT', 'ACTIVE', 'NOGO'):
                return render.info('目前艺术品的状态，不能修改艺术品信息！')              

            item_data = r1['data']['item']

        return render.item_edit(helper.get_session_uname(), helper.get_privilege_name(), helper.get_session_addr(),
            item_data)


    def POST(self):
        if not helper.logged(helper.PRIV_TRD|helper.PRIV_DEL|helper.PRIV_ART, 'ITEM'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data=web.input(item_id='', owner_addr='', desc='', detail='', date='', type='', 
            subject='', media='', size='', base_price='')

        print("images: ", user_data.get('image'))

        if user_data['item_id']=='n/a': # 新建
            if '' in [user_data.owner_addr, user_data.desc, user_data.date]:
                return render.info('物品名称、所有者链地址、年代均不能为空！')  

            # 链上新建用户
            r1 = fork_api('/biz/item/new', {
                'caller_addr'  : helper.get_session_addr(),
                'owner_addr'   : user_data['owner_addr'],
                'desc'         : user_data['desc'],
                'detail'       : user_data['detail'],
                'date'         : user_data['date'],
                'type'         : user_data['type'],
                'subject'      : user_data['subject'],
                'media'        : user_data['media'],
                'size'         : user_data['size'],
                'base_price'   : user_data['base_price'],
            })
            if (r1 is None) or r1['code']!=0:
                return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

            # 填充已生成的 item_id
            user_data['item_id'] = r1['data']['id']

        else:
            if user_data.owner_addr=='':
                return render.info('参数错误！') 

            # 获取用户信息
            r1 = fork_api('/query/item/info', {
                'id' : user_data.item_id,
            })
            if (r1 is None) or r1['code']!=0:
                return render.info('出错了，请联系管理员！(%s %s)'%\
                    ((r1['code'], r1['msg']) if r1 else ('', '')))

            # 检查是否可修改
            if r1['data']['item']['status'] not in ('WAIT', 'ACTIVE', 'NOGO'):
                return render.info('目前艺术品的状态，不能修改艺术品信息！')              

            # 链上修改用户信息
            r1 = fork_api('/biz/item/modify', {
                'caller_addr': helper.get_session_addr(),
                'id'         : user_data['item_id'],
                'desc'       : user_data['desc'],
                'detail'     : user_data['detail'],
                'date'       : user_data['date'],
                'type'       : user_data['type'],
                'subject'    : user_data['subject'],
                'media'      : user_data['media'],
                'size'       : user_data['size'],
                'base_price' : user_data['base_price'],
            })
            if (r1 is None) or r1['code']!=0:
                return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))


        # 上传图片
        if len(user_data['image'])>0:
            image_list = user_data['image'].split(',')
            for im in image_list:
                if len(im)==46 and '.' not in im: # ipfs 标记
                    continue

                with open(os.path.join(setting.image_store_path, im[:2], im), 'rb') as f:
                    img_data = f.read()
                img_data = base64.b64encode(img_data).decode('utf-8')

                # 上传照片
                r1 = fork_api('/ipfs/upload/image', {
                    'caller_addr': helper.get_session_addr(),
                    'item_id'    : user_data['item_id'],
                    'image'      : img_data,
                })
                if (r1 is None) or r1['code']!=0:
                    return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

                print("hash", r1['data']['hash'])

        # TODO: 处理删除图片的情况！

        return render.info('成功保存！','/item/list')
