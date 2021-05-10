# -*- coding: utf-8 -*-

import logging
import web

#logging.basicConfig(filename='error.log',level=logging.DEBUG)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if 'environ' in web.ctx.keys():
            record.user_agent = web.ctx['environ']['HTTP_USER_AGENT']
            record.remote_addr = web.ctx['environ']['REMOTE_ADDR']
        else:
            record.user_agent = '-'
            record.remote_addr = '-'

        return super().format(record)

def get_logger(module_name):
    # create logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    #ch.addFilter(RequestFormatter())
    ch.setLevel(logging.INFO)

    # create formatter
    formatter = RequestFormatter('%(remote_addr)s %(user_agent)s %(asctime)s %(levelname)s %(name)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    return logger