import multiprocessing
import os
import time
import winreg

import psutil
import win32process

from pywecomauto.util.handler import find_handles, close_handle

BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
WEWORK_PROCESS_NAME = 'WXWork.exe'
WEWORK_DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIRECTORY))), r"WXWork\WXWork.exe")
WEWORK_REGISTRY_KEY = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\企业微信"
print('lanuch')


def close_handles():
    process_ids = []
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] == WEWORK_PROCESS_NAME:
            process_ids.append(proc.pid)
    if process_ids:
        handles = find_handles(process_ids=process_ids, handle_names=[r'\Tencent.WeWork.ExclusiveObject'])
        for handle in handles:
            close_handle(handle['process_id'], handle['handle'])


def launch():
    if os.path.exists(WEWORK_DEFAULT_PATH):
        client_path = WEWORK_DEFAULT_PATH
    else:
        client_path = get_client_path()
    if not client_path:
        return
    p = win32process.CreateProcess(client_path, '', None, None, 0, 0, None, None, win32process.STARTUPINFO())
    time.sleep(1)
    if p and len(p) == 4:
        return p[2]


def get_client_path():
    sub_key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, WEWORK_REGISTRY_KEY)
    values = winreg.QueryValueEx(sub_key, "DisplayIcon")
    if values and values[0]:
        path = values[0].strip()
        if path.startswith('\"') or path.startswith('\''):
            path = path[1:]
        if path.endswith('\"') or path.endswith('\''):
            path = path[:-1]
        return path


def start(number: int):
    multiprocessing.freeze_support()
    processes = []
    for i in range(number):
        # close_handles()
        p = multiprocessing.Process(target=close_handles)
        p.start()
        p.join()
        pid = launch()
        processes.append(pid)
    return processes
