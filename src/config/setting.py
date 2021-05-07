#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
#from pymongo import MongoClient

#####
debug_mode = True   # Flase - production, True - staging
#####
#
enable_proxy = True
http_proxy = 'http://192.168.2.108:8888'
https_proxy = 'https://192.168.2.108:8888'
proxy_list = ['192.168.2.103']
enable_local_test = True
#####
'''
db_serv_list='127.0.0.1'
# db_serv_list='mongodb://10.168.11.151:27017,10.252.95.145:27017,10.252.171.8:27017/?replicaSet=rs0'

cli = {
    'web'  : MongoClient(db_serv_list),
}
# MongoClient('10.168.11.151', replicaset='rs0', readPreference='secondaryPreferred') # 使用secondary 读
# MongoClient('mongodb://10.168.11.151:27017,10.252.95.145:27017,10.252.171.8:27017/?replicaSet=rs0')

db_web = cli['web']['face_db']
db_web.authenticate('ipcam','ipcam')

db_primary = db_web
'''

db_web = db_primary = None

thread_num = 1
auth_user = ['test','gt']
cs_admin = ['cs0']

tmp_path = '/usr/local/nginx/html/xah/static/tmp'
logs_path = '/usr/local/nginx/logs'
image_store_path = '/usr/local/nginx/html/xah/static/image/product'

app_host='wx.jack139.top'
wx_host='wx.jack139.top'
image_host='wx.jack139.top/static'
notify_host='wx.jack139.top'
app_pool=['wx.jack139.top']

WX_store = {
    '000' : { # 测试
        'wx_appid' : 'wxe74bcaaaddf09466',
        'wx_appsecret' : '50712d327e2cba931d23d061b2596953',
        'mch_id' : '1408035102',
    },

}


# 微信设置
region_id = '000'
wx_setting = WX_store[region_id]

order_fuffix=''

http_port=8000
https_port=443

mail_server='127.0.0.1'
sender='"jack139"<jack139@gmail.com>'
worker=['jack139@gmail.com']

web.config.debug = debug_mode

config = web.storage(
    email = 'jack139@gmail.com',
    site_name = 'ipcam',
    site_des = '',
    static = '/static'
)

############# 消息中间件设置

REDIS_CONFIG = {
    'SERVER' : '127.0.0.1',
    'PORT'   : '7480',
    'PASSWD' : 'e18ffb7484f4d69c2acb40008471a71c',
    'REQUEST-QUEUE' : 'cardnum-synchronous-asynchronous-queue',
    'REQUEST-QUEUE-NUM' : 1,
    'MESSAGE_TIMEOUT' : 10, # 结果返回消息超时，单位：秒
}


# dispatcher 中 最大线程数
MAX_DISPATCHER_WORKERS = 8


############ chain setting

SYS_ADMIN = "bid1art16zs5zpmsw5wezyrpnls76ytdy7ws2zpqan9ey9"

CHAIN_API_HOST = "127.0.0.1"
CHAIN_API_PORT = "8888"