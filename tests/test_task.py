# -*- coding: utf-8 -*-
import re
import unittest

from pywinauto.findwindows import find_windows
from win32gui import SetWindowText

from pywecomauto.task import ClientCheckTask
from pywecomauto.task import LoginTask
from pywecomauto.util import launcher


def clear_dict(d):
    if d is None:
        return None
    elif isinstance(d, list):
        return list(filter(lambda x: x is not None, map(clear_dict, d)))
    elif not isinstance(d, dict):
        return d
    else:
        r = dict(
            filter(lambda x: x[1] is not None,
                   map(lambda x: (x[0], clear_dict(x[1])),
                       d.items())))
        if not bool(r):
            return None
        return r


class TaskTestSuite(unittest.TestCase):

    def test_client(self):
        p = launcher.start(2)
        handles = find_windows(class_name='WeChatLogin')
        print('handles:', handles)
        for h in handles:
            task = LoginTask()
            url1 = task.run(h)
            print(url1)

    def test_qrcode_task(self):
        task = LoginTask()
        url1 = task.run(0x411190)
        print(url1)
        assert url1 is not None

    def test_login_task(self):
        task = ClientCheckTask()
        task.run(0x5A311E)
        assert True

    def test_userinfo(self):
        title = 'WeCom|BLACK|Spot|叶伟|毅|10_4'
        values = re.findall("\\|(\\d+)_(\\d+)$", title[title.rindex("|"):])
        p = '^WeCom\\|(.{%s})\\|(.{%s})' % values[0]
        values = re.findall(p, title)
        print(values)
        SetWindowText(0x200BF6, '企业微信')
