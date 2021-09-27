# -*- coding: utf-8 -*-
import asyncio
import logging
import signal
import threading

from pywecomauto.executor import run


def start():
    print('start')
    global event
    global task
    global loop
    event = threading.Event()
    event.set()
    loop = asyncio.new_event_loop()
    task = loop.create_task(run(event))
    signal.signal(signal.Signals.SIGINT, stop)
    signal.signal(signal.Signals.SIGTERM, stop)
    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        logging.warning('Canceled')
    finally:
        task.cancel()
        loop.close()


def stop(*args):
    print('stop', args)
    event.clear()
    task.cancel()
    loop.stop()
    logging.info('Stopped')


if __name__ == '__main__':
    start()
