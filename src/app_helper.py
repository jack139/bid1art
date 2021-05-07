# -*- coding: utf-8 -*-
#

# 前端代码 公用变量及函数

import time, os, hashlib, random
import urllib, urllib3, json
import re
import redis

import logger
from config import setting
from config.setting import REDIS_CONFIG
#from app_settings import *  # app_settings.py将拼接在末尾

db = setting.db_web

logger = logger.get_logger(__name__)

#---------------------------- 标记是否在测试／staging环境，用于区别生成环境的一些设置
IS_TEST = 'dev' in setting.app_host
IS_STAGING = 'dev' in setting.app_host
#----------------------------

# 时间函数
ISOTIMEFORMAT=['%Y-%m-%d %X', '%Y-%m-%d', '%Y%m%d%H%M', '%Y-%m-%d %H:%M']

def time_str(t=None, format=0):
    return time.strftime(ISOTIMEFORMAT[format], time.localtime(t))

def validateEmail(email):
    if len(email) > 7:
      if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
          return 1
    return 0

RAND_BASE=[
    'abcdefghijklmnopqrstuvwxyz',
    '0123456789',
]

def my_rand(n=4, base=0):
    return ''.join([random.choice(RAND_BASE[base]) for ch in range(n)])



#==========================================================================



BLOCK_LIST = [
    '15000623214',
    #'13194084665',
]



# 查询session
def get_session(session_id):
    return db.app_sessions.find_one_and_update({'session_id':session_id},{'$set':{'attime':time.time()}})

# 检查session登录状态
def logged(session_id):
    session = get_session(session_id)
    if session==None:
        return None
    else:
        #db.app_user.update_one({'uname' : session['uname']},{
        #   '$set'  : {'last_time' : time_str()}
        #})
        if session['login']==1: # 登录后返回uname
            return session['uname']
        else:
            return None

# 检查session登录状态, 合并app与微信订单
def app_logged(session_id):
    session = get_session(session_id)
    if session==None:
        return None
    else:
        #db.app_user.update_one({'uname' : session['uname']},{
        #   '$set'  : {'last_time' : time_str()}
        #})
        if session['login']==1: # 登录后返回uname,openid
            return {'uname' : session['uname'], 'openid': session.get('openid',''),  'unionid': session.get('unionid',''),
                    'type': session.get('type','app')}
        else:
            return None

# 检查openid
def check_openid(openid):
    #r = db.app_user.find_one_and_update(
    #    {'openid' : openid},
    #    {'$set'   : {'last_time' : time_str()}},
    #    {'uname' : 1, 'openid':1}
    #)
    #if r:
    #    return {'uname' : r.get('uname',''), 'openid': r['openid']}
    #else:
        return None

# 微信检查session登录状态
def wx_logged(session_id):
    session = get_session(session_id)
    if session==None:
        return None
    else:
        #db.app_user.update_one({'uname' : session['uname']},{
        #   '$set'  : {'last_time' : time_str()}
        #})
        if session['login']==1: # 登录后返回uname
            #return session['uname']
            return {'uname' : session['uname'], 'openid': session['openid'], 'unionid': session.get('unionid','')}
        else:
            return None

def generate_sign(c): # c时列表，c[0]一定是app_id
    db_dev = db.app_device.find_one({'app_id' : c[0]}, {'private_key':1})
    if db_dev==None:
        return None
        #return json.dumps({'ret' : -3, 'msg' : 'app_id错误'})
    else:
        #验证签名
        sign_str = '%s%s' % (db_dev['private_key'], ''.join(i for i in c))
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()




# 生成order_id
def get_new_order_id(version='v1', prefix='acme'):
    if IS_TEST or IS_STAGING:
        surfix = '-test'
    else:
        surfix = ''

    cc=1
    while cc!=None:
        # order_id 城市(1位)+日期时间(6+4位)+随机数(5位)+版本
        order_id = '%s20%s%s%s%s' % (prefix,time_str(format=2)[2:],my_rand(6,1),version[-1],surfix)
        cc = db.order_app.find_one({'order_id' : order_id},{'_id':1})
    db.order_app.insert_one({'order_id':order_id}) # 先占位 2016-03-17,gt
    return order_id

# 取得设备类型
def get_devive_type(app_id):
    db_dev = db.app_device.find_one({'app_id':app_id},{'type':1})
    if db_dev:
        return db_dev['type']
    else:
        return ''


# 获取access_token，与wx.py 中相同
def get_token(force=False, region_id=None): # force==True 强制刷新
    if region_id==None:
        region_id = setting.region_id
    print('region: ', region_id)
    if not force:
        db_ticket = db.jsapi_ticket.find_one({'region_id':region_id})
        if db_ticket and int(time.time())-db_ticket.get('token_tick', 0)<3600:
            if db_ticket.get('access_token', '')!='':
                print(db_ticket['access_token'])
                return db_ticket['access_token']

    url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % \
        (setting.WX_store[region_id]['wx_appid'], setting.WX_store[region_id]['wx_appsecret'])
    f=urllib.urlopen(url)
    data = f.read()
    f.close()

    t=json.loads(data)
    if 'access_token' in t.keys():
        print(t)
        db.jsapi_ticket.update_one({'region_id':region_id},
            {'$set':{'token_tick':int(time.time()), 'access_token':t['access_token']}},upsert=True)
        return t['access_token']
    else:
        db.jsapi_ticket.update_one({'region_id':region_id},
            {'$set':{'token_tick':int(time.time()), 'access_token':''}},upsert=True)
        return ''

def wx_reply_msg0(openid, text, force=False, region_id=None):
    text0 = text.encode('utf-8') if type(text)==type(u'') else text
    body_data = '{"touser":"%s","msgtype":"text","text":{"content":"%s"}}' % (str(openid), text0)
    urllib3.disable_warnings()
    http = urllib3.PoolManager(num_pools=2, timeout=180, retries=False)
    url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s'%get_token(force, region_id)
    try:
        r = http.request('POST', url,
            headers={'Content-Type': 'application/json'},
            body=body_data)
        if r.status==200:
            return json.loads(r.data)
        else:
            print('http fail: ', r.status)
            return None
    except Exception as e:
        print('%s: %s (%s)' % (type(e), e, url))
        return None


def wx_reply_msg(openid, text, region_id=None):
    print('openid: ', openid)
    if region_id.strip()=='':
        print('region_id is BLANK')
        return None
    r = wx_reply_msg0(openid, text, region_id=region_id)
    if r==None or r.get('errcode', 0)!=0:
        # 发送失败，强制刷新token后再发一次
        print(r)
        r = wx_reply_msg0(openid, text, force=True, region_id=region_id)
    return r


########## 异步接口调用


# redis订阅
def redis_subscribe(queue_id):
    rc = redis.StrictRedis(host=REDIS_CONFIG['SERVER'], 
            port=REDIS_CONFIG['PORT'], db=1, password=REDIS_CONFIG['PASSWD'])
    ps = rc.pubsub()
    ps.subscribe(queue_id)  #从liao订阅消息
    logger.info('subscribe to : '+str((queue_id))) 
    return ps


# 从订阅接收, 值收一条
def redis_sub_receive(pubsub, queue_id):
    #for item in pubsub.listen():        #监听状态：有消息发布了就拿过来
    #    logger.debug('subscribe 2: '+str((queue_id, item))) 
    #    if item['type'] == 'message':
    #        #print(item)
    #        break

    start = time.time()
    while 1:
        item = pubsub.get_message()
        if item:
            logger.info('reveived: type='+item['type']) 
            if item['type'] == 'message':
                break

        # 检查超时
        if time.time()-start > REDIS_CONFIG['MESSAGE_TIMEOUT']:
            item = { 'data' : json.dumps({"code": 9997, 'data': {"msg": "消息队列超时"}}).encode('utf-8') }
            break

        # 释放cpu
        time.sleep(0.001)

    return item


# redis发布
def redis_publish(queue_id, data):
    logger.info('publish: '+queue_id)
    msg_body = json.dumps(data)

    rc = redis.StrictRedis(host=REDIS_CONFIG['SERVER'], 
            port=REDIS_CONFIG['PORT'], db=1, password=REDIS_CONFIG['PASSWD'])
    return rc.publish(queue_id, msg_body)


# 返回　请求队列　随机id
def choose_queue_redis():
    # 随机返回
    return random.randint(1, REDIS_CONFIG['REQUEST-QUEUE-NUM'])

# redis发布到请求队列
def redis_publish_request(request_id, data):
    msg_body = {
        'request_id' : request_id, # request id
        'data' : data,
    }

    # 设置发送的queue
    queue = REDIS_CONFIG['REQUEST-QUEUE']+str(choose_queue_redis())
    print('queue:', queue)

    return redis_publish(queue, msg_body)


# 生成request_id
def gen_request_id():
    return '%s%s'%(time_str(format=2),hashlib.md5(my_rand(10).encode('utf-8')).hexdigest())

