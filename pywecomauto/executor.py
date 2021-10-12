# -*- coding: utf-8 -*-
import logging
import threading
import time

from pywecomauto.server import Server
from pywecomauto.watchdog import Watchdog


def run(event):
    lock = threading.Lock()
    Watchdog(event, lock).run()
    Server('localhost', '9999').run()
    while event.is_set():
        try:
            ok = check_client_status() or check_client_timeout() or execute_task()
            if not ok:
                time.sleep(1)
        except:
            logging.error('Failed to execute tasks', exc_info=True)
    logging.info('Stopped executing tasks')
