#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
#from libs import pos_func
import helper

db = setting.db_web

# 客户信息编辑

url = ('/plat/license_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'EA_ADMIN'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(lic_id='')

        lic_data = { 'lic_id' : 'n/a'}

        if user_data.lic_id != '': 
            db_obj=db.ea_license.find_one({'_id':ObjectId(user_data.lic_id)})
            if db_obj!=None:
                # 已存在的obj
                lic_data = db_obj
                lic_data['lic_id']=lic_data['_id']

        return render.license_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            lic_data)


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'EA_ADMIN'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(lic_id='',user_name='', user_cardid='', user_cellphone='', type='', status='', expired='')

        print(user_data)

        if '' in [user_data.lic_id, user_data.user_name, user_data.user_cardid, user_data.user_cellphone, \
            user_data.type, user_data.status, user_data.expired]:
            return render.info('必填项不能为空！')  

        #
        license = user_data.license

        if user_data['lic_id']=='n/a': # 新建
            lic_id = None
            message = '新建'

            # 生成新的 license 
            license = helper.my_rand(18).upper()
            r2 = db.ea_license.find_one({'license':license})
            if r2: # 两次重复的概率比较小，所以不检查
                license = helper.my_rand(16).upper()
        else:
            lic_id = ObjectId(user_data['lic_id'])
            message = '修改'


        try:
            update_set={
                'license'   : license,
                'type'      : user_data['type'],
                'grade'     : int(user_data['grade']),
                'status'    : int(user_data['status']),
                'created'   : helper.time_str(),
                'expired'   : user_data['expired'],
                'last_tick' : int(time.time()),  # 更新时间戳
                'note'      : user_data.get('note','').strip(),
                'user'      : {
                    'name'      : user_data['user_name'].strip(),
                    'gender'    : user_data['user_gender'],
                    'city'      : user_data.get('user_city','').strip(),
                    'cardid'    : user_data['user_cardid'].strip(),
                    'platform'  : user_data.get('user_platform','').strip(),
                    'cellphone' : user_data.get('user_cellphone','').strip(),
                    'mail'      : user_data.get('user_mail','').strip(),
                    'wxid'      : user_data.get('user_wxid','').strip(),
                },
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        if user_data['lic_id']=='n/a':
            update_set['history'] = [(helper.time_str(), helper.get_session_uname(), message)]
            r2 = db.ea_license.insert_one(update_set)

        else:
            db.ea_license.update_one({'_id' : lic_id}, {
                '$set'  : update_set,
                '$push' : {
                    'history' : (helper.time_str(), helper.get_session_uname(), message), 
                }  # 纪录操作历史
            })

        return render.info('成功保存！', '/plat/license')
