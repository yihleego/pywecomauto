# -*- coding: utf-8 -*-
from pywinauto.findwindows import find_windows


def find_logged_in_client_handles():
    return find_windows(class_name='WeWorkWindow')


def find_not_logged_in_client_handles():
    return find_windows(class_name='WeChatLogin')


def find_handles(**kwargs):
    return find_windows(**kwargs)
