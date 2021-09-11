# -*- coding: utf-8 -*-
from pywinauto.findwindows import find_windows

from pywecomauto.rpa.task.base_task import *


class ClosePopupTask(BaseTask):
    def run(self, handle):
        handles = find_windows(class_name='ConfirmFinancialCorpVersionWindow')
        if handles and len(handles) > 0:
            for handle in handles:
                connect(handle)
                click(Assets.Popup.BTN_GOT_ID, 1)
        handles = find_windows(class_name_re='WeWorkMessageBoxFrame|NetProxySettingFrame|ConfirmFinancialCorpVersionWindow')
        if handles and len(handles) > 0:
            for handle in handles:
                close_handle(handle)
