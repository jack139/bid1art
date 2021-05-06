#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web, json, time
import app_helper, helper

db = app_helper.db

url = ('/qa/test')

# 检查license, 返回初始参数
class handler:
    def POST(self):
        web.header('Content-Type', 'application/json')
        param = web.input(k='', q='')

        knowledge = param.k.strip()
        question = param.q.strip()

        print("k--> ", knowledge)
        print("q--> ", question)

        ## 异步处理调用  
        request_id = app_helper.gen_request_id()

        request_msg = {  #  -------  gotalk 回答
            'api'  : 'gotalk_qa_with_knowledge',
            'data' : [knowledge, question],
        }

        anwser = '出错了！'

        # 异步处理

        # 在发redis消息前注册, 防止消息漏掉
        ps = app_helper.redis_subscribe(request_id)

        # 发布消息给redis
        r = app_helper.redis_publish_request(request_id, request_msg)
        if r is None:
            print("消息队列异常")
        else:    
            # 通过redis订阅等待结果返回
            ret = app_helper.redis_sub_receive(ps, request_id)               
            ret2 = json.loads(ret['data'].decode('utf-8'))

            #print(ret2)

            if ret2['code']==200: # 内部成功使用 200
                if ret2['data']['reply'] is not None:
                    anwser = ret2['data']['reply']
                else:
                    anwser = '没找到答案'

        print("anwser--> ", anwser)

        # 返回
        return json.dumps({'ret' : 0, 'data' : { 'data' : anwser }})

    def GET(self):
        return self.POST()