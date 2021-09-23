# -*- coding: utf-8 -*-

from pywecomauto.task.base_message_task import BaseMessageTask


class GroupMessageTask(BaseMessageTask):
    def run(self, handle):
        print(1)
