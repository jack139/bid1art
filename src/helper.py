#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# 后台界面公用变量及函数

import web
import time, datetime, os
import re
from config import setting
from app_helper import IS_TEST

db = setting.db_web

web_session = None

ISOTIMEFORMAT=['%Y-%m-%d %X', '%Y-%m-%d', '%Y%m%d']

def time_str(t=None, format=0):
    return time.strftime(ISOTIMEFORMAT[format], time.localtime(t))

def validateEmail(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

##############################################

# 用户等级
PRIV_VISITOR = 0b00000000
PRIV_ADMIN   = 0b00000001
PRIV_TRD     = 0b00001000
PRIV_AH      = 0b00010000
PRIV_DEL     = 0b00100000
PRIV_REV     = 0b01000000
PRIV_ART     = 0b10000000

# 菜单权限
MENU_LEVEL = {
    'ADMIN' : 1,   # 平台管理员
    'TRD'   : 2,   # 交易者
    'AH'    : 3,   # 拍卖行
    'DEL'   : 4,   # 经销商
    'REV'   : 5,   # 评论家
    'ART'   : 6,   # 艺术家
}

user_level = {
    PRIV_VISITOR  : '访客',
    PRIV_ADMIN    : '管理员',
    PRIV_TRD      : '交易者',  
    PRIV_AH       : '拍卖行', 
    PRIV_DEL      : '经销商', 
    PRIV_REV      : '评论家', 
    PRIV_ART      : '艺术家', 
}

#################


# 为子文件传递session ---------------------

def set_session(s):
    global web_session
    web_session = s

def get_session_uname():
    return web_session.uname

#----------------------------------------


def get_privilege_name(privilege=None, menu_level=None):
    if privilege==None:
        privilege = web_session.privilege

    name = ['?']
    p = int(privilege)
    if p==PRIV_ADMIN:
        return user_level[PRIV_ADMIN]
    if p&(PRIV_TRD|PRIV_AH|PRIV_DEL|PRIV_REV|PRIV_ART):
        if menu_level==None:
            menu_level = web_session.menu_level  # '----X--X----XXX---'
        for k in MENU_LEVEL.keys():
            if menu_level[MENU_LEVEL[k]]=='X':
                name.append(k)
    return name

def my_rand(n=5):
    import random
    return ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for ch in range(n)])

def logged(privilege = -1, menu_level=None):
    if web_session.login==1:
        if privilege == -1:  # 只检查login, 不检查权限
            return True
        else:
            if int(web_session.privilege) & privilege: # 检查特定权限
                if menu_level:
                    # 检查菜单权限
                    if web_session.menu_level[MENU_LEVEL[menu_level]]=='X':
                        return True
                    else:
                        return False
                else:
                    return True
            else:
                return False
    else:
        return False

def create_render(plain=False, globals={}, force_visitor=False):
    if plain: layout=None
    else: layout='layout'

    privilege = web_session.privilege

    # 强制使用visitor模板
    if force_visitor:
        return web.template.render('templates/visitor', base=layout, globals=globals)

    if logged():
        if privilege&(PRIV_AH|PRIV_REV):
            render = web.template.render('templates/super', base=layout, globals=globals)
        elif privilege&PRIV_ADMIN:
            render = web.template.render('templates/admin', base=layout, globals=globals)
        elif privilege&(PRIV_TRD|PRIV_DEL|PRIV_ART):
            render = web.template.render('templates/user', base=layout, globals=globals)
        else:
            render = web.template.render('templates/visitor', base=layout, globals=globals)
    else:
        render = web.template.render('templates/visitor', base=layout, globals=globals)

    # to find memory leak
    #_unreachable = gc.collect()
    #print('Unreachable object: %d' % _unreachable)
    #print('Garbage object num: %s' % str(gc.garbage))

    return render

