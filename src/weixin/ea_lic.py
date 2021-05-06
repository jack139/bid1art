#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web, json, time
import app_helper, helper

db = app_helper.db

url = ('/ea/lic')

LICENSES = [
    '098F6BCD4621D373CADE4E832627B4F6',
    'AD0234829205B9033196BA818F7A872B',
    '8AD8757BAA8564DC136C1E07507F4A98',
]

# 检查license, 返回初始参数
class handler:        
    def POST(self):
        web.header('Content-Type', 'text/plain')
        param = web.input(license='')

        license = param.license.strip()

        print('License: ', license)

        if license == '':
            return 'FALSE|Need License'

        ## 是否已报名成功
        #r2 = db.signup_user.find_one({
        #    'name'  : name,
        #    'phone' : phone,
        #    'completed': 1,
        #}) 

        #if r2:
        #    return json.dumps({'ret' : -5, 'msg' : '您已报过名了！欢迎您参会！'})

        if license in LICENSES:
            # 返回
            # multiplier = 2.0;  
            # increament = 0.1;
            # MA_Period1 = 2.0;
            # MA_Period2 = 60.0;

            return 'TRUE|2.0|0.1|2.0|60.0|'
        else:
            return 'FALSE|WRONG License'

    def GET(self):
        return self.POST()