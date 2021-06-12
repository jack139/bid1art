# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

from helper import logged
from helper import create_render

from chain_api import fork_api0

# 用户管理

url = ('/admin/user_add')


class handler:
    def GET(self):
        if logged(helper.PRIV_ADMIN|helper.PRIV_OP, 'USER_OP'):
            render = create_render()
            return render.user_new(helper.get_session_uname(), helper.get_privilege_name())
        else:
            raise web.seeother('/')

    def POST(self):
        if logged(helper.PRIV_ADMIN|helper.PRIV_OP, 'USER_OP'):
            render = create_render()
            user_data=web.input(login_name='', user_type='', bank_acc_name='', 
                bank_name='', bank_acc_no='', address='', phone='', email='', referrer='')
            #print(user_data)

            if user_data.login_name=='':
                return render.info('用户名不能为空！')  

            if user_data['user_type']=='OP':
                user_type = 'OP|ITEM_OP|REV_OP|USER_OP'
            elif user_data['user_type'] in ['TRD', 'DEL', 'ART']:
                user_type = user_data['user_type']+'|ITEM|AUC|TRANS'
            elif user_data['user_type']=='AH':
                user_type = 'AH|AUC_OP|TRANS_OP'
            elif user_data['user_type']=='REV':
                user_type = 'REV|REV'
            else:
                return render.info('用户类型错误！')

            # 链上新建用户
            r1 = fork_api0('/biz/user/register', {
                'caller_addr'   : helper.get_session_addr(),
                'login_name'    : user_data['login_name'],
                'user_type'     : user_type,
                'bank_acc_name' : user_data['bank_acc_name'],
                'bank_name'     : user_data['bank_name'],
                'bank_acc_no'   : user_data['bank_acc_no'],
                'address'       : user_data['address'],
                'phone'         : user_data['phone'],
                'email'         : user_data['email'],
                'referrer'      : user_data['referrer'],
            })
            if (r1 is None) or r1['code']!=0:
                if r1 and r1['code']==9009:
                    return render.info('用户名已存在！请修改后再试。')
                else:   
                    return render.info('出错了，请稍后再试！(%s %s)'%((r1['code'], r1['msg']) if r1 else ('', '')))

            return render.info('注册成功！<p>请妥善保存以下信息：</p><p>链地址：%s</p><p>密码字符串：\n%s</p>'%\
                (r1['data']['chain_addr'], r1['data']['mystery']),'/admin/user')
            #else:
            #    return render.info('用户名已存在！请修改后重新添加。')
        else:
            raise web.seeother('/')
