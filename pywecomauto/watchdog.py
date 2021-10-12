# -*- coding: utf-8 -*-
import asyncio
import logging
import threading
import time

from pywinauto.findwindows import find_windows, find_elements

from pywecomauto.models import TaskType, ClientStatus
from pywecomauto.task import *


class Watchdog:
    def __init__(self, event,lock):
        self.event = event
        self.lock = lock
        self.state = []
        self.clients = {}
        self.tasks = {
            TaskType.CHECK: ClientCheckTask(),
            TaskType.LOGIN: LoginTask(),
            TaskType.LOGOUT: LogoutTask(),
            TaskType.CONTACT: ContactTask(),
            TaskType.PERSONAL_MESSAGE: PersonalMessageTask(),
            TaskType.GROUP_MESSAGE: GroupMessageTask(),
        }

    def run(self):
        thread = threading.Thread(target=self.watch)
        thread.start()

    def watch(self):
        old_handles = []
        while self.event.is_set():
            try:
                new_handles = find_windows(class_name_re='WeWorkWindow|WeChatLogin')
                new_handles.sort()
                if old_handles != new_handles:
                    old_handles = new_handles
                    self.state.append(1)
                    asyncio.run(self.try_check())
                time.sleep(1)
            except:
                logging.error('Failed to watch client', exc_info=True)
        logging.info('Stopped watching client thread')

    async def try_check(self):
        if len(self.state) == 0:
            return
        self.lock.acquire()
        try:
            if len(self.state) == 0:
                return
            self.state.clear()
            self.check()
        except:
            logging.error('Failed to watch client', exc_info=True)
        finally:
            self.lock.release()

    def check(self):
        elements = find_elements(class_name_re='WeWorkWindow|WeChatLogin')
        handles = [e.handle for e in elements]
        # Remove clients that no longer exist.
        for handle in self.clients:
            if handle not in handles:
                self.clients.pop(handle)
        # Save clients.
        for e in elements:
            handle = e.handle
            if not handle or handle in self.clients:
                continue
            if e.class_name == 'WeChatLogin':
                self.clients[handle] = {'status': ClientStatus.OFFLINE}
            elif e.class_name == 'WeWorkWindow':
                userinfo = self.tasks[TaskType.CHECK].run(handle)
                if userinfo:
                    self.clients[handle] = {'handle': handle, 'process': e.process_id,
                                            'name': userinfo.get('name'), 'company': userinfo.get('company'),
                                            'status': ClientStatus.ONLINE}
                else:
                    self.tasks[TaskType.LOGOUT].run(handle)