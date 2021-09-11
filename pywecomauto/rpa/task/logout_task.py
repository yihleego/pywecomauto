# -*- coding: utf-8 -*-
import os
import signal

from pywecomauto.rpa.task import BaseTask
from pywecomauto.rpa.task.base_task import get_hwnd


class LogoutTask(BaseTask):
    def run(self, handle):
        hwnd = get_hwnd(handle)
        os.kill(hwnd.process_id(), signal.SIGABRT)
