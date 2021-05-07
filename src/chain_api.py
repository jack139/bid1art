# coding:utf-8

import urllib3, json, base64, time, hashlib
from datetime import datetime
from config.setting import CHAIN_API_HOST, CHAIN_API_PORT

urllib3.disable_warnings()

pool = urllib3.PoolManager(num_pools=5, timeout=120, retries=False)


# 生成参数字符串
def gen_param_str(param1):
    param = param1.copy()
    name_list = sorted(param.keys())
    if 'data' in name_list: # data 按 key 排序, 中文不进行性转义，与go保持一致
        param['data'] = json.dumps(param['data'], sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return '&'.join(['%s=%s'%(str(i), str(param[i])) for i in name_list if str(param[i])!=''])


def fork_api(api_uri, data_para={}):
    body = {
        'version'   : '1',
        'sign_type' : 'SHA256', 
        'data'      : data_para,
    }

    secret = 'MjdjNGQxNGU3NjA1OWI0MGVmODIyN2FkOTEwYTViNDQzYTNjNTIyNSAgLQo='
    appid = '4fcf3871f4a023712bec9ed44ee4b709'
    unixtime = int(time.time())
    body['timestamp'] = unixtime
    body['appid'] = appid

    param_str = gen_param_str(body)
    sign_str = '%s&key=%s' % (param_str, secret)

    sha256 = hashlib.sha256(sign_str.encode('utf-8')).hexdigest().encode('utf-8')
    signature_str =  base64.b64encode(sha256).decode('utf-8')

    #print(sign_str.encode('utf-8'))
    #print(sha256)
    #print(signature_str)

    body['sign_data'] = signature_str

    body = json.dumps(body)
    #print(body)

    host = 'http://%s:%s'%(CHAIN_API_HOST, CHAIN_API_PORT)
    url = host+'/api/r1'+api_uri
    
    start_time = datetime.now()
    r = pool.urlopen('POST', url, body=body)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    print(r.status)
    if r.status==200:
        return json.loads(r.data.decode('utf-8'))
    else:
        print(r.data.decode('utf-8'))
        return None
