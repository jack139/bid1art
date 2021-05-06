#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time, json
from bson.objectid import ObjectId
from config import setting
import helper
import app_helper

db = setting.db_web

# 聊天机器人规则编辑

url = ('/plat/talkbot_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TALKBOT'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(rule_id='')

        rule_data = { 'rule_id' : 'n/a' }

        if user_data.rule_id != '': 
            db_obj=db.talkbot.find_one({'_id':ObjectId(user_data.rule_id)})
            if db_obj!=None:
                # 已存在的obj
                rule_data = db_obj
                rule_data['rule_id']=rule_data['_id']

        return render.talkbot_edit(helper.get_session_uname(), helper.get_privilege_name(), rule_data )


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'TALKBOT'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(rule_id='', rule_name='')

        rule_name = user_data.rule_name.strip()
        if rule_name=='':
            return render.info('规则名不能为空！')  

        # 排除规则同名
        find_condition = {
            'rule_name'  : rule_name,
        }

        if user_data['rule_id']=='n/a': # 新建
            rule_id = None
            message = '新建'
        else:
            rule_id = ObjectId(user_data['rule_id'])
            message = '修改'
            find_condition['_id'] = { '$ne' : rule_id}  # 排除自己

        r1 = db.talkbot.find_one(find_condition)
        if r1 is not None:
            return render.info('规则名已存在，不能重复！')  


        try:
            update_set={
                'rule_name'  : rule_name,
                'question'   : user_data['question'], 
                'reply'      : user_data['reply'],
                'reply_type' : int(user_data['reply_type']),
                'available'  : int(user_data['available']),
                'last_tick'  : int(time.time()),  # 更新时间戳
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        if rule_id is None:
            update_set['history'] = [(helper.time_str(), helper.get_session_uname(), message)]
            r2 = db.talkbot.insert_one(update_set)
        else:
            db.talkbot.update_one({'_id':rule_id}, {
                '$set'  : update_set,
                '$push' : {
                    'history' : (helper.time_str(), helper.get_session_uname(), message), 
                }  # 纪录操作历史
            })

        # 刷新规则
        db.sys_refs.update_one({'name' : 'talkbot_update'}, {'$set' : {'last_tick' : int(time.time())}}, upsert=True)

        # 重新计算规则

        ## 异步处理调用
        request_id = app_helper.gen_request_id()

        request_msg = {
            'api'  : 'talkbot_calc'
        }

        # 异步处理

        # 在发redis消息前注册, 防止消息漏掉
        ps = app_helper.redis_subscribe(request_id)

        # 发布消息给redis
        r = app_helper.redis_publish_request(request_id, request_msg)
        if r is None:
            print("消息队列异常")
            return render.info('消息队列异常')  

        # 通过redis订阅等待结果返回
        ret = app_helper.redis_sub_receive(ps, request_id)               
        ret2 = json.loads(ret['data'].decode('utf-8'))

        print(ret2)

        #from talkbot_lib import gensim_index
        #if not gensim_index.index_from_db(db):
        #    return render.info('规则计算出错！', '/plat/talkbot_edit?rule_id='+user_data['rule_id'])
        #else:
        #    return render.info('成功保存！', '/plat/talkbot')

        if ret2['code']==200 and ret2['data']['result']:
            return render.info('成功保存！', '/plat/talkbot')
        else:
            return render.info('规则计算出错！', '/plat/talkbot_edit?rule_id='+user_data['rule_id'])
