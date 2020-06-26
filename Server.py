# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 12:50'

import logging
import os
from logging.handlers import TimedRotatingFileHandler

from Settings import LOG_FORMAT
from app import create_app

if __name__ == '__main__':
    app = create_app()
    os.environ['HADOOP_USER_NAME'] = 'hdfs'
    handler = TimedRotatingFileHandler('snapshot_server.log', when='D', interval=1, backupCount=7,
                                       encoding='utf-8', delay=False, utc=True)
    app.logger.addHandler(handler)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    app.logger.setLevel(logging.DEBUG)
    app.run(host='127.0.0.1', port=5000, debug=True)
