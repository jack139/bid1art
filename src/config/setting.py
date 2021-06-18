# -*- coding: utf-8 -*-
import web


#####
debug_mode = True   # Flase - production, True - staging
#####
#
enable_proxy = True

thread_num = 1

tmp_path = '/usr/local/nginx/html/xah/static/tmp'
logs_path = '/usr/local/nginx/logs'
static_image_path = '../static/image'
image_store_path = '../static/image/product'


http_port=8000
https_port=443


web.config.debug = debug_mode

config = web.storage(
    email = 'jack139@gmail.com',
    site_name = 'bid1art',
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

SYS_ADMIN = "bid1art14k8kjdlh5tepamzp0zasqag3uk65au3u9sc84x"
#SYS_ADMIN = "bid1art156yfvjguxp95s4wx2z6usgjg8zpzcqydnqus9s"  # home env

CHAIN_API_HOST = "127.0.0.1"
CHAIN_API_PORT = "8888"


# 显示列表一页的数量
PAGE_SIZE = 20
