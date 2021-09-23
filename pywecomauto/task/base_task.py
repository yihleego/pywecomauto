# -*- coding: utf-8 -*-
import os
from enum import Enum

import airtest.core.api
import airtest.core.win
import pyperclip
from airtest.core.cv import Template
from airtest.core.helper import G
from airtest.core.settings import Settings
from airtest.core.win import Windows
from pywinauto.controls.hwndwrapper import HwndWrapper

Settings.CVSTRATEGY = ["tpl", "sift", "brisk"]
Settings.FIND_TIMEOUT_TMP = 0.6
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(ROOT_PATH, 'assets/')
TEMP_PATH = os.path.join(ROOT_PATH, 'temp/')


class HackWindows(Windows):
    def connect(self, handle=None, **kwargs):
        if handle:
            handle = int(handle)
            self.app = self._app.connect(handle=handle)
            self._top_window = self.app.window(handle=handle).wrapper_object()
        else:
            for k in ["process", "timeout"]:
                if k in kwargs:
                    kwargs[k] = int(kwargs[k])
            self.app = self._app.connect(**kwargs)
            self._top_window = self.app.top_window().wrapper_object()

    def set_foreground(self):
        self._top_window.set_focus()
        super(HackWindows, self).set_foreground()

    def close(self):
        self._top_window.close()


G.CUSTOM_DEVICES['windows'] = HackWindows


def connect(handle):
    if handle:
        device = airtest.core.api.connect_device("Windows:///" + str(handle))
        device.set_foreground()
        device.move((0, 0))
        return device


def connect_silent(handle):
    if handle:
        device = airtest.core.api.connect_device("Windows:///" + str(handle))
        return device


def get_hwnd(handle):
    return HwndWrapper(handle)


def exists(v):
    if isinstance(v, Template):
        return airtest.core.api.exists(v)
    elif isinstance(v, str):
        return airtest.core.api.exists(Template(ASSETS_PATH + v))
    elif isinstance(v, tuple):
        return v
    elif isinstance(v, list):
        for i in v:
            r = exists(i)
            if r:
                return r
    else:
        return None


def click(v, wait_time=0):
    ok = exists(v)
    if ok:
        airtest.core.api.touch(ok)
        wait(wait_time)
        return ok
    else:
        return False


def double_click(v, wait_time=0):
    ok = exists(v)
    if ok:
        airtest.core.api.double_click(ok)
        wait(wait_time)
        return ok
    else:
        return False


def keyevent(key, wait_time=0):
    airtest.core.api.keyevent(key)
    wait(wait_time)


def copy(v, wait_time=0):
    pyperclip.copy(v)
    wait(wait_time)


def paste(wait_time=0):
    v = pyperclip.paste()
    wait(wait_time)
    return v


def wait(wait_time=0):
    if wait_time > 0:
        airtest.core.api.sleep(wait_time)


def close_handle(handle):
    HwndWrapper(handle).close()


def partition(s, l):
    return [s[i:i + l] for i in range(0, len(s), l)]


class Asset(Enum):
    class Login(Enum):
        REFRESH_QRCODE = ''

    class Main(Enum):
        REFRESH_QRCODE = ''


class BaseTask:
    def run(self, handle):
        pass


class Assets:
    class Main:
        pass

    class Login:
        BTN_REFRESH_QRCODE = 'login/btn_refresh_qrcode.png'
        BTN_SWITCH_ACCOUNT = 'login/btn_switch_account.png'

    class Menu:
        BTN_MENU = 'menu/btn_menu.png'
        BTN_MENU_HOVER = 'menu/btn_menu_hover.png'
        ITEM_MESSAGE_MANAGER = 'menu/item_message_manager.png'
        ITEM_SETTING = 'menu/item_setting.png'

    class Setting:
        BTN_EDIT = 'setting/btn_edit.png'
        LABEL_NAME = 'setting/label_name.png'
        LABEL_USERINFO = 'setting/label_userinfo.png'
        LABEL_USERINFO_SELECTED = 'setting/label_userinfo_selected.png'

    class Popup:
        BTN_GOT_ID = 'popup/btn_got_it.png'
