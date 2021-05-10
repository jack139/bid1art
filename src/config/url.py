# -*- coding: utf-8 -*-

import os

urls = [
	'/',                'Login',
	'/login',           'Login',
	'/logout',          'Reset',
]

## ---- 分布式部署---------------------------------
app_dir = ['admin', 'user']
app_list = []
for i in app_dir:
	tmp_list = ['%s.%s' % (i,x[:-4])  for x in os.listdir(i) if x[:2]!='__' and x.endswith('.pyc')]
	tmp_list2 = ['%s.%s' % (i,x[:-3])  for x in os.listdir(i) if x[:2]!='__' and x.endswith('.py')]
	if len(tmp_list)>0: 
		app_list.extend(tmp_list)
	else: # tmp_list2 用于测试，未编译成pyc
		app_list.extend(tmp_list2)


for i in app_list:
	tmp_app = __import__(i, None, None, ['*'])
	if not hasattr(tmp_app, 'url'):
		print(tmp_app)
		continue
	urls.extend((tmp_app.url, i+'.handler'))

#-----------------------------------------------------
