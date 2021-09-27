# -*- coding: utf-8 -*-
import json
import logging
import threading
import time
import urllib.request

from pywinauto.findwindows import find_windows

from pywecomauto.manager import *
from pywecomauto.models import *
from pywecomauto.task import *

QUEUE = []
TASKS = {
    TaskType.CHECK: ClientCheckTask(),
    TaskType.LOGIN: LoginTask(),
    TaskType.LOGOUT: LogoutTask(),
    TaskType.CONTACT: ContactTask(),
    TaskType.PERSONAL_MESSAGE: PersonalMessageTask(),
    TaskType.GROUP_MESSAGE: GroupMessageTask(),
}


async def run(event):
    thread = threading.Thread(target=watch_client_runnable, args=(event,))
    thread.start()
    thread2 = threading.Thread(target=notify_runnable, args=(event,))
    # thread2.start()
    while event.is_set():
        try:
            ok = check_client_status() or check_client_timeout() or execute_task()
            if not ok:
                time.sleep(1)
        except:
            logging.error('Failed to execute tasks', exc_info=True)
    logging.info('Stopped executing tasks')


def check_client_status():
    global QUEUE
    if len(QUEUE) <= 0:
        return False
    QUEUE.clear()
    major_handles = find_windows(class_name='WeWorkWindow')
    minor_handles = find_windows(class_name='WeChatLogin')
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
            update_client_by_handle(Client(handle=handle, company_name=userinfo.get('company'), user_name=userinfo.get('name'), status=ClientStatus.USING.value))
        except Exception:
            logging.error('Failed to check client', exc_info=True)
    return True


def check_client_timeout():
    clients = list_timeout_clients()
    if not clients:
        return False
    for client in clients:
        update_client_by_id(Client(id=client.id, status=ClientStatus.IDLE.value))
    return True


def execute_task():
    task = get_next_task()
    if not task:
        return False
    try:
        update_task(Task(id=task.id, status=TaskStatus.RUNNING.value, executed_time=now()))
        client = get_using_client(task.company, task.name)
        if task.type == TaskType.LOGIN.value:
            result = execute_login_task(task, client)
        elif task.type == TaskType.LOGOUT.value:
            result = execute_logout_task(task, client)
        else:
            result = execute_biz_task(task, client)
        update_task(Task(id=task.id, status=TaskStatus.FINISHED.value, finished_time=now(), result=result))
        insert_entity(Notification(task_id=task.id))
    except Exception as e:
        logging.error(f'Failed to execute the task({task.id})', exc_info=True)
        if isinstance(e, TaskException):
            status = e.status
        else:
            status = TaskStatus.FAILED.value
        update_task(Task(id=task.id, status=status, finished_time=now(), message=str(e)))
        insert_entity(Notification(task_id=task.id))
    return True


def execute_login_task(task, client):
    if client:
        return True
    client = get_idle_client()
    if not client:
        raise TaskException(TaskStatus.UNAVAILABLE.value)
    qrcode = TASKS[task.type].run(client.handle)
    update_client_by_id(Client(id=client.id, company_name=task.company, user_name=task.name, status=ClientStatus.IDLE.value, expired_time=after_seconds(60)))
    return qrcode


def execute_logout_task(task, client):
    if not client:
        return True
    return TASKS[task.type].run(client.handle)


def execute_biz_task(task, client):
    if not client:
        raise TaskException(TaskStatus.UNLOGGED.value)
    return TASKS[task.type].run(client.handle)


def watch_client_runnable(event):
    global QUEUE
    old_handles = find_windows(class_name_re='WeWorkWindow|WeChatLogin')
    old_handles.sort()
    QUEUE.append(1)
    while event.is_set():
        try:
            new_handles = find_windows(class_name_re='WeWorkWindow|WeChatLogin')
            new_handles.sort()
            if old_handles != new_handles:
                old_handles = new_handles
                QUEUE.append(1)
            time.sleep(1)
        except Exception:
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
                url = 'app.url'
                result = build_result(task)
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


def build_result(task):
    data = {'task_id': task.id,
            'company': task.company,
            'name': task.name,
            'type': task.type,
            'result': task.result,
            'status': task.status,
            'scheduled_time': task.scheduled_time,
            'executed_time': task.executed_time,
            'finished_time': task.finished_time}
    result = {'success': True if task.status == TaskStatus.FINISHED.value else False,
              'data': json.dumps(data, ensure_ascii=False),
              'message': task.message}
    return result
