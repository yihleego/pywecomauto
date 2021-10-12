# -*- coding: utf-8 -*-
import logging
import signal
import threading

from pywecomauto import executor


def start():
    global event
    event = threading.Event()
    event.set()
    executor.run(event)
    signal.signal(signal.Signals.SIGINT, stop)
    signal.signal(signal.Signals.SIGTERM, stop)


def stop(*args):
    event.clear()
    logging.info('Stopped')


if __name__ == '__main__':
    start()
