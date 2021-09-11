# -*- coding: utf-8 -*-
import asyncio
import logging
import signal
import threading

from pywecomauto.rpa.scheduler import execute_tasks

event = threading.Event()
loop = asyncio.new_event_loop()
task = loop.create_task(execute_tasks(event))


def stop(*args):
    event.clear()
    task.cancel()
    loop.stop()
    logging.info('RPA has been stopped')


def start():
    event.set()
    # loop.add_signal_handler(signal.Signals.SIGINT, stop)
    # loop.add_signal_handler(signal.Signals.SIGTERM, stop)
    signal.signal(signal.Signals.SIGINT, stop)
    signal.signal(signal.Signals.SIGTERM, stop)
    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        logging.info('Tasks has been canceled')
    finally:
        task.cancel()
        loop.close()


if __name__ == '__main__':
    start()
