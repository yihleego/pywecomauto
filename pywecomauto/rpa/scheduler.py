# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import threading
import time
import urllib.request

from pywecomauto.common.rsa_sign import sign_sha256
from pywecomauto.database.database_manager import *
from pywecomauto.database.models import now, Task, Client, ClientStatus, TaskType, TaskStatus, Notification, NotificationStatus, after_seconds
from pywecomauto.openapi.service import to_sign_content
from pywecomauto.rpa.task.client_check_task import ClientCheckTask
from pywecomauto.rpa.task.contact_task import ContactTask
from pywecomauto.rpa.task.group_message_task import GroupMessageTask
from pywecomauto.rpa.task.login_task import LoginTask
from pywecomauto.rpa.task.logout_task import LogoutTask
from pywecomauto.rpa.task.personal_message_task import PersonalMessageTask
from pywecomauto.rpa.win_manager import find_handles

QUEUE = []
TASKS = {
    TaskType.CHECK: ClientCheckTask(),
    TaskType.LOGIN: LoginTask(),
    TaskType.LOGOUT: LogoutTask(),
    TaskType.CONTACT: ContactTask(),
    TaskType.PERSONAL_MESSAGE: PersonalMessageTask(),
    TaskType.GROUP_MESSAGE: GroupMessageTask(),
}


async def execute_tasks(event):
    thread = threading.Thread(target=watch_client_runnable, args=(event,))
    thread.start()
    thread2 = threading.Thread(target=notify_runnable, args=(event,))
    thread2.start()
    while event.is_set():
        try:
            executed = await check_client_status() \
                       or await check_client_timeout() \
                       or await execute_qrcode_task() \
                       or await execute_biz_task()
            if not executed:
                await asyncio.sleep(1)
        except Exception as e:
            logging.error('Failed to execute tasks', exc_info=True)
    logging.info('Stopped executing tasks')


async def execute_qrcode_task():
    task = get_loginable_task()
    if not task:
        return False
    try:
        client = get_idle_client()
        if not client:
            logging.error(f'No client available for task {task.id}')
            update_task(Task(id=task.id, status=TaskStatus.UNAVAILABLE.value, finished_time=now()))
            insert_entity(Notification(task_id=task.id))
            return True
        update_client_by_id(Client(id=client.id, company_name=task.company_name, user_name=task.user_name, status=ClientStatus.IDLE.value, expired_time=after_seconds(60)))
        qrcode = TASKS[TaskType.LOGIN].run(client.handle)
        logging.debug(f'QRCode: {qrcode}')
    except Exception as e:
        logging.error('Failed to obtain QRCode', exc_info=True)
        update_task(Task(id=task.id, status=TaskStatus.FAILED.value, finished_time=now(), message=str(e)))
        insert_entity(Notification(task_id=task.id))
    return True


async def execute_biz_task():
    task = get_executable_task()
    if not task:
        return False
    try:
        result = None
        client = get_using_client(task.company_name, task.user_name)
        if task.type == TaskType.LOGIN.value:
            if not client:
                return True
        elif task.type == TaskType.LOGOUT.value:
            if client:
                update_task(Task(id=task.id, status=TaskStatus.RUNNING.value, executed_time=now()))
                result = TASKS[task.type].run(client.handle)
        else:
            if not client:
                return True
            update_task(Task(id=task.id, status=TaskStatus.RUNNING.value, executed_time=now()))
            result = TASKS[task.type].run(client.handle)
        update_task(Task(id=task.id, status=TaskStatus.FINISHED.value, finished_time=now(), result=result))
        insert_entity(Notification(task_id=task.id))
    except Exception as e:
        logging.error('Failed to execute task', exc_info=True)
        update_task(Task(id=task.id, status=TaskStatus.FAILED.value, finished_time=now(), message=str(e)))
        insert_entity(Notification(task_id=task.id))
    return True


async def check_client_status():
    global QUEUE
    if len(QUEUE) <= 0:
        return False
    QUEUE.clear()
    major_handles = find_handles(class_name='WeWorkWindow')
    minor_handles = find_handles(class_name='WeChatLogin')
    current_handles = set(major_handles + minor_handles)
    clients = list_all_clients()
    db_handles = set([c.handle for c in clients])
    handles_to_insert = current_handles.difference(db_handles)
    handles_to_delete = db_handles.difference(current_handles)
    if handles_to_delete:
        delete_client_by_handles(handles_to_delete)
    if handles_to_insert:
        insert_entities([Client(process=0, handle=handle) for handle in handles_to_insert])
    for handle in major_handles:
        try:
            userinfo = TASKS[TaskType.CHECK].run(handle)
            if not userinfo:
                continue
            update_client_by_handle(Client(handle=handle, company_name=userinfo.get('company_name'), user_name=userinfo.get('user_name'), status=ClientStatus.USING.value))
        except Exception as e:
            logging.error('Failed to check client', exc_info=True)
    return True


async def check_client_timeout():
    clients = list_timeout_clients()
    if not clients:
        return False
    for client in clients:
        update_client_by_id(Client(id=client.id, status=ClientStatus.IDLE.value))
        if not client.company_name or not client.user_name:
            continue
        tasks = list_tasks_by_user(client.company_name, client.user_name)
        if not tasks:
            continue
        for task in tasks:
            update_task(Task(id=task.id, status=TaskStatus.TIMEOUT.value, finished_time=now()))
            insert_entity(Notification(task_id=task.id))
    return True


def watch_client_runnable(event):
    global QUEUE
    old_handles = find_handles(class_name_re='WeWorkWindow|WeChatLogin')
    old_handles.sort()
    QUEUE.append(1)
    while event.is_set():
        try:
            new_handles = find_handles(class_name_re='WeWorkWindow|WeChatLogin')
            new_handles.sort()
            if old_handles != new_handles:
                old_handles = new_handles
                QUEUE.append(1)
            time.sleep(1)
        except Exception as e:
            logging.error('Failed to watch client', exc_info=True)
    logging.info('Stopped watching client thread')


def notify_runnable(event):
    while event.is_set():
        notifications = list_notifications()
        if not notifications:
            time.sleep(1)
            continue
        task = None
        url = None
        for n in notifications:
            try:
                task = get_task(n.task_id)
                if not task:
                    update_notification(Notification(id=n.id, status=NotificationStatus.IGNORED.value, response=f'Task {n.task_id} cannot be found'))
                    continue
                app = get_app(1)
                if not app or not app.url:
                    update_notification(Notification(id=n.id, status=NotificationStatus.IGNORED.value))
                    continue
                url = app.url
                result = build_result(app, task)
                data = json.dumps(result, ensure_ascii=False)
                req = urllib.request.Request(url=url, method='POST', data=data.encode('utf-8'), headers={'Content-Type': 'application/json'})
                res = urllib.request.urlopen(req)
                update_notification(Notification(id=n.id, status=NotificationStatus.SUCCESS.value, request=data, response=str(res.read(), encoding="utf-8")))
                logging.debug(f'Notified, URL:{url}, result:{result}', exc_info=True)
            except Exception as e:
                logging.error(f'Failed to notify, URL:{url}', exc_info=True)
                update_notification(Notification(id=n.id, status=NotificationStatus.FAILURE.value, response=str(e)))
                if task and count_notification_by_task_id(task.id) < 3:
                    insert_entity(Notification(task_id=task.id, notified_time=after_seconds(60)))
    logging.info('Stopped notifying thread')


def build_result(app, task):
    data = {'task_id': task.id,
            'company_name': task.company_name,
            'user_name': task.user_name,
            'type': task.type,
            'result': task.result,
            'status': task.status,
            'scheduled_time': task.scheduled_time,
            'executed_time': task.executed_time,
            'finished_time': task.finished_time}
    result = {'success': True if task.status == TaskStatus.FINISHED.value else False,
              'data': json.dumps(data, ensure_ascii=False),
              'message': task.message}
    result['signature'] = sign_sha256(app.private_key, to_sign_content(result))
    return result
