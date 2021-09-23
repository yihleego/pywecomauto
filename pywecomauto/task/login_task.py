# -*- coding: utf-8 -*-
from pyzbar import pyzbar

from pywecomauto.task import BaseTask
from pywecomauto.task.base_task import connect, click, Assets


class LoginTask(BaseTask):
    def run(self, handle):
        device = connect(handle)
        click([Assets.Login.BTN_REFRESH_QRCODE, Assets.Login.BTN_SWITCH_ACCOUNT], 1)
        snapshot = device.snapshot()
        decoded = pyzbar.decode(snapshot)
        if decoded and decoded[0]:
            return decoded[0].data.decode('utf-8')
