# -*- coding: utf-8 -*-
#

# 后台界面公用变量及函数

import web
import time, datetime, os, random
import re
from config import setting

web_session = None


ISOTIMEFORMAT=['%Y-%m-%d %X', '%Y-%m-%d', '%Y%m%d', '%Y%m%d%H%M', '%Y-%m-%d %H:%M']

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
PRIV_OP      = 0b00000010
PRIV_TRD     = 0b00001000
PRIV_AH      = 0b00010000
PRIV_DEL     = 0b00100000
PRIV_REV     = 0b01000000
PRIV_ART     = 0b10000000

# 菜单权限
MENU_LEVEL = {
    'ADMIN'    : 1,   # 平台管理员
    'ITEM'     : 2,   # 物品管理
    'AUC'      : 3,   # 拍卖操作
    'TRANS'    : 4,   # 交易操作
    'REV'      : 5,   # 评论操作
    'AUC_OP'   : 6,   # 拍卖管理
    'TRANS_OP' : 7,   # 交易管理
    'REV_OP'   : 8,   # 评论管理
    'ITEM_OP'  : 9,   # 物品管理
    'USER_OP'  : 10,  # 用户管理
}

user_level = {
    PRIV_VISITOR  : '访客',
    PRIV_ADMIN    : '管理员',
    PRIV_OP       : '平台管理员',
    PRIV_AH       : '拍卖行', 
    PRIV_TRD      : '交易者',  
    PRIV_DEL      : '经销商', 
    PRIV_REV      : '评论家', 
    PRIV_ART      : '艺术家', 
}

user_type = {
    'TRD'   : '交易者',
    'AH'    : '拍卖行',
    'OP'    : '平台管理员',
    'REV'   : '评论家',
    'DEL'   : '经销商',
    'ART'   : '艺术家',
    'ADMIN' : '管理员',
}

#################


# 为子文件传递session ---------------------

def set_session(s):
    global web_session
    web_session = s

def get_session_uname():
    return web_session.uname

def get_session_addr():
    return web_session.uid

#----------------------------------------


def get_privilege_name(privilege=None, menu_level=None):
    if privilege==None:
        privilege = web_session.privilege

    name = ['?']
    p = int(privilege)
    #if p==PRIV_ADMIN:
    #    return user_level[PRIV_ADMIN]
    if p&(PRIV_ADMIN|PRIV_OP|PRIV_TRD|PRIV_AH|PRIV_DEL|PRIV_REV|PRIV_ART):
        if menu_level==None:
            menu_level = web_session.menu_level  # '----X--X----XXX---'
        for k in MENU_LEVEL.keys():
            if menu_level[MENU_LEVEL[k]]=='X':
                name.append(k)
    return name


RAND_BASE=[
    'abcdefghijklmnopqrstuvwxyz',
    '0123456789',
]

def my_rand(n=4, base=0):
    return ''.join([random.choice(RAND_BASE[base]) for ch in range(n)])

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
        if privilege&(PRIV_TRD|PRIV_DEL|PRIV_ART|PRIV_REV):
            render = web.template.render('templates/user', base=layout, globals=globals)
        elif privilege&(PRIV_AH|PRIV_OP):
            render = web.template.render('templates/super', base=layout, globals=globals)
        elif privilege&PRIV_ADMIN:
            render = web.template.render('templates/admin', base=layout, globals=globals)
        else:
            render = web.template.render('templates/visitor', base=layout, globals=globals)
    else:
        render = web.template.render('templates/visitor', base=layout, globals=globals)

    # to find memory leak
    #_unreachable = gc.collect()
    #print('Unreachable object: %d' % _unreachable)
    #print('Garbage object num: %s' % str(gc.garbage))

    return render

