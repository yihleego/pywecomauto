# -*- coding: utf-8 -*-
from pywecomauto.rpa.task.base_message_task import BaseMessageTask


class PersonalMessageTask(BaseMessageTask):
    def run(self, handle):
        print(1)
