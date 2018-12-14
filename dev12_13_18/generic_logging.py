# -*- coding: UTF-8 -*-

import logging
import time
import os
import sys

from CONFIG import RECORD_LOGS, LOG_CONSOLE, WRITE_LATEST
from CONFIG import LATEST_LEVEL, CONSOLE_LEVEL, OUTPUT_LEVEL

HEADER = ("="*40) + "[%s]" + ("="*40) + '\n'


def new_handlers():
    current_header = HEADER % time.ctime()
    hdlrs = []
    formatter = logging.Formatter('[%(asctime)s] [%(filename)s:%(lineno)d/%(levelname)s]: %(message)s',
                                  '%H:%M:%S')
    filename = 'logs/DUMMY.log'
    if not os.path.exists('logs'):
        os.mkdir('logs')
    if RECORD_LOGS:
        filename = time.ctime()
        while os.path.exists('logs/'+filename+'.log'):
            filename += '-'  # Make sure the filename isn't already taken

        filename = 'logs/'+filename+'.log'
        with open(filename, "w") as fp:
            fp.write(current_header)
        file_logger = logging.FileHandler(filename)
        file_logger.setLevel(OUTPUT_LEVEL)
        file_logger.setFormatter(formatter)
        hdlrs.append(file_logger)
    if WRITE_LATEST:
        with open('logs/latest.log', "w") as fp:
            fp.write(current_header)
        latest = logging.FileHandler('logs/latest.log')
        latest.setLevel(LATEST_LEVEL)
        latest.setFormatter(formatter)
        hdlrs.append(latest)
    if LOG_CONSOLE:
        print ('\n')
        print (current_header.strip())
        console_logger = logging.StreamHandler(sys.stdout)
        console_logger.setLevel(CONSOLE_LEVEL)
        console_logger.setFormatter(formatter)
        hdlrs.append(console_logger)
    return hdlrs, filename


handlers = new_handlers()
filename = handlers[1]
handlers = handlers[0]
