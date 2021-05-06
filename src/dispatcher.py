# -*- coding: utf-8 -*-

# 后台调度程序，异步执行，使用redis作为消息队列

import sys, json, time, random
import concurrent.futures
from datetime import datetime

import app_helper as helper
import logger
from config.setting import REDIS_CONFIG, MAX_DISPATCHER_WORKERS

import binascii

from gotalk_lib import gotalk
from talkbot_lib import gensim_bot, gensim_index

logger = logger.get_logger(__name__)


def process_api(request_id, request_msg):
    request = request_msg
    try:
        if request['api']=='talkbot':
            r = gensim_bot.qa_bot_db(request['data'])
            result = { 'code' : 200, 'data' : { 'msg':'success', 'reply' : r, 'request_id' : request_id} }

        elif request['api']=='talkbot_calc':
            r = gensim_index.index_from_db(helper.db)
            result = { 'code' : 200, 'data' : { 'msg':'success', 'result' : r, 'request_id' : request_id} }

        elif request['api']=='gotalk_qa':
            r = gotalk.qa(request['data'])
            result = { 'code' : 200, 'data' : { 'msg':'success', 'reply' : r, 'request_id' : request_id} }

        elif request['api']=='gotalk_qa_with_knowledge':
            r = gotalk.qa_with_knowledge(request['data'][0], request['data'][1])
            result = { 'code' : 200, 'data' : { 'msg':'success', 'reply' : r, 'request_id' : request_id} }

        else: # 未知 api
            logger.error('Unknown api: '+request['api']) 

            result = { 'code' : 9900, 'data': {'msg' : '未知 api 调用'}}

    except binascii.Error as e:
        logger.error("编码转换异常: %s" % e)
        result = { 'code' : 9901, 'data': {'msg' : 'base64编码异常: '+str(e)}}

    except Exception as e:
        logger.error("未知异常: %s" % e, exc_info=True)
        result = { 'code' : 9998, 'data': {'msg' : '未知错误: '+str(e)}}

    return result



def process_thread(msg_body):
    try:
        # for keras 2.3
        #import keras.backend.tensorflow_backend as tb
        #tb._SYMBOLIC_SCOPE.value = True

        logger.info('{} Calling api: {}'.format(msg_body['request_id'], msg_body['data'].get('api', 'Unknown'))) 

        start_time = datetime.now()

        api_result = process_api(msg_body['request_id'], msg_body['data'])

        logger.info('1 ===> [Time taken: {!s}]'.format(datetime.now() - start_time))
        
        # 发布redis消息
        helper.redis_publish(msg_body['request_id'], api_result)
        
        logger.info('{} {} [Time taken: {!s}]'.format(msg_body['request_id'], msg_body['data']['api'], datetime.now() - start_time))

        sys.stdout.flush()

    except Exception as e:
        logger.error("process_thread异常: %s" % e, exc_info=True)



if __name__ == '__main__':
    if len(sys.argv)<2:
        print("usage: dispatcher.py <QUEUE_NO.>")
        sys.exit(2)

    queue_no = sys.argv[1]

    print('Request queue NO. ', queue_no)

    sys.stdout.flush()

    while 1:
        # redis queue
        ps = helper.redis_subscribe(REDIS_CONFIG['REQUEST-QUEUE']+queue_no)

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_DISPATCHER_WORKERS) # 建议与cpu核数相同

        for item in ps.listen():        #监听状态：有消息发布了就拿过来
            logger.info('reveived: type='+item['type']) 
            if item['type'] == 'message':
                #print(item)
                msg_body = json.loads(item['data'].decode('utf-8'))

                future = executor.submit(process_thread, msg_body)
                logger.info('Thread future: '+str(future)) 

                sys.stdout.flush()
