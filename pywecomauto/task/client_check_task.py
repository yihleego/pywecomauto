# -*- coding: utf-8 -*-
import re

from pywinauto.findwindows import find_window, find_windows
from sqlalchemy.testing.plugin.plugin_base import logging
from win32gui import GetWindowText, SetWindowText

from pywecomauto.task.base_task import *

TITLE_PREFIX = 'WeCom|'
TITLE_FORMAT = 'WeCom|{}|{}|{}_{}'


class ClientCheckTask(BaseTask):
    def run(self, handle):
        userinfo = self.get_userinfo(handle)
        if userinfo:
            return userinfo
        hwnd = get_hwnd(handle)
        process = hwnd.process_id()
        self.close_existing_windows(process)
        userinfo = self.find_userinfo(handle, process)
        if userinfo:
            logging.debug(f'Obtained userinfo: {userinfo}')
            self.set_userinfo(handle, userinfo)
            return userinfo

    def find_userinfo(self, handle, process):
        config_device = None
        edit_device = None
        try:
            connect(handle)
            click([Assets.Menu.BTN_MENU, Assets.Menu.BTN_MENU_HOVER], 1)

            menu_handle = find_window(class_name="DuiMenuWnd", process=process)
            if not menu_handle:
                return
            connect_silent(menu_handle)
            click(Assets.Menu.ITEM_SETTING, 1)

            config_handle = find_window(class_name='ConfigWindow', process=process)
            if not config_handle:
                return
            config_device = connect(config_handle)

            label_userinfo_pos = click([Assets.Setting.LABEL_USERINFO_SELECTED, Assets.Setting.LABEL_USERINFO], 1)
            if not label_userinfo_pos:
                return
            double_click((label_userinfo_pos[0] + 139, label_userinfo_pos[1] + 21), 0.5)
            copy("")
            keyevent("^c")
            company = paste()

            click(Assets.Setting.BTN_EDIT, 1)

            edit_handle = find_window(class_name='ModifyUserInfoWindow', process=process)
            if not edit_handle:
                return
            edit_device = connect(edit_handle)
            label_name_pos = exists(Assets.Setting.LABEL_NAME)
            if not label_name_pos:
                return
            click((label_name_pos[0] + 100, label_name_pos[1] + 0), 0.5)
            copy("")
            keyevent("^a^c")
            user_name = paste()
            return {'company': company, 'name': user_name}
        finally:
            if config_device:
                config_device.close()
            if edit_device:
                edit_device.close()

    def get_userinfo(self, handle):
        title = GetWindowText(handle)
        if not title or not title.startswith(TITLE_PREFIX):
            return
        suffixes = re.findall("\\|(\\d+)_(\\d+)$", title[title.rindex("|"):])
        if not suffixes or len(suffixes[0]) != 2:
            return
        p = '^WeCom\\|(.{%s})\\|(.{%s})' % (suffixes[0][0], suffixes[0][1])
        values = re.findall(p, title)
        if not values or len(values[0]) != 2:
            return
        userinfo = values[0]
        return {'company': userinfo[0], 'name': userinfo[1]}

    def set_userinfo(self, handle, userinfo):
        SetWindowText(handle, TITLE_FORMAT.format(userinfo['company'], userinfo['name'], len(userinfo['company']), len(userinfo['name'])))

    def close_existing_windows(self, process):
        handles = find_windows(class_name_re='ConfigWindow|ModifyUserInfoWindow', process=process)
        if not handles:
            return
        for handle in handles:
            close_handle(handle)
