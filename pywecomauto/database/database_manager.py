# -*- coding: utf-8 -*-
from sqlalchemy import exists, asc, not_, or_

from pywecomauto.database.database import open_session
from pywecomauto.database.models import now, Task, Client, ClientStatus, TaskStatus, TaskType, Notification, App


def insert_entity(entity):
    if not entity:
        return
    db = open_session()
    db.add(entity)
    db.commit()
    db.refresh(entity)
    db.close()


def insert_entities(entities):
    if not entities:
        return
    db = open_session()
    db.add_all(entities)
    db.commit()
    for entity in entities:
        db.refresh(entity)
    db.close()


def get_app(id):
    db = open_session()
    app = db.query(App).filter(App.id == id).one()
    db.close()
    return app


def get_app_by_secret(secret):
    db = open_session()
    app = db.query(App).filter(App.secret == secret).one()
    db.close()
    return app


def update_client_by_id(client):
    data = {'company_name': client.company_name,
            'user_name': client.user_name,
            'expired_time': client.expired_time,
            'status': client.status}
    db = open_session()
    db.query(Client) \
        .filter(Client.id == client.id) \
        .update(clear_dict(data), synchronize_session="fetch")
    db.commit()
    db.close()


def update_client_by_handle(client):
    data = {'company_name': client.company_name,
            'user_name': client.user_name,
            'expired_time': client.expired_time,
            'status': client.status}
    db = open_session()
    db.query(Client) \
        .filter(Client.handle == client.handle) \
        .update(clear_dict(data), synchronize_session="fetch")
    db.commit()
    db.close()


def delete_client_by_handles(handles):
    db = open_session()
    db.query(Client) \
        .filter(Client.handle.in_(handles)) \
        .delete(synchronize_session="fetch")
    db.commit()
    db.close()


def get_idle_client():
    db = open_session()
    client = db.query(Client) \
        .filter(Client.status == ClientStatus.IDLE.value) \
        .first()
    db.close()
    return client


def get_using_client(company_name, user_name):
    db = open_session()
    client = db.query(Client) \
        .filter(Client.company_name == company_name) \
        .filter(Client.user_name == user_name) \
        .filter(Client.status == 1) \
        .first()
    db.close()
    return client


def list_all_clients():
    db = open_session()
    clients = db.query(Client).all()
    db.close()
    return clients


def list_timeout_clients():
    db = open_session()
    clients = db.query(Client) \
        .filter(Client.status == ClientStatus.WAITING.value) \
        .filter(Client.expired_time <= now()) \
        .all()
    db.close()
    return clients


def update_task(task):
    data = {'status': task.status,
            'executed_time': task.executed_time,
            'finished_time': task.finished_time,
            'result': task.result,
            'message': task.message}
    db = open_session()
    db.query(Task).filter(Task.id == task.id).update(clear_dict(data), synchronize_session="fetch")
    db.commit()
    db.close()


def delete_task_by_ids(ids):
    db = open_session()
    r = db.query(Task) \
        .filter(Task.id.in_(ids)) \
        .filter(Task.deleted == 0) \
        .update({"deleted": 1, 'deleted_time': now()}, synchronize_session="fetch")
    db.commit()
    db.close()
    return r


def get_task(id):
    db = open_session()
    task = db.query(Task) \
        .filter(Task.id == id) \
        .filter(Task.deleted == 0) \
        .first()
    db.close()
    return task


def list_tasks_by_ids(ids):
    db = open_session()
    tasks = db.query(Task) \
        .filter(Task.id.in_(ids)) \
        .filter(Task.deleted == 0) \
        .all()
    db.close()
    return tasks


def get_loginable_task():
    db = open_session()
    task = db.query(Task) \
        .filter(Task.scheduled_time <= now()) \
        .filter(Task.status == TaskStatus.CREATED.value) \
        .filter(Task.type != TaskType.LOGOUT.value) \
        .filter(Task.deleted == 0) \
        .filter(not_(exists()
                     .where(Client.company_name == Task.company_name)
                     .where(Client.user_name == Task.user_name)
                     .where(Client.status.in_([ClientStatus.USING.value, ClientStatus.WAITING.value])))) \
        .order_by(asc(Task.scheduled_time)) \
        .first()
    db.close()
    return task


def get_executable_task():
    db = open_session()
    task = db.query(Task) \
        .filter(Task.scheduled_time <= now()) \
        .filter(Task.status == TaskStatus.CREATED.value) \
        .filter(Task.deleted == 0) \
        .filter(or_(exists()
                    .where(Client.company_name == Task.company_name)
                    .where(Client.user_name == Task.user_name)
                    .where(Client.status == ClientStatus.USING.value),
                    Task.type == TaskType.LOGOUT.value)) \
        .order_by(asc(Task.scheduled_time)) \
        .first()
    db.close()
    return task


def list_tasks_by_user(company_name, user_name):
    db = open_session()
    tasks = db.query(Task) \
        .filter(Task.company_name == company_name) \
        .filter(Task.user_name == user_name) \
        .filter(Task.deleted == 0) \
        .all()
    db.close()
    return tasks


def list_notifications():
    db = open_session()
    tasks = db.query(Notification) \
        .filter(Notification.notified_time <= now()) \
        .filter(Notification.status == 0) \
        .all()
    db.close()
    return tasks


def count_notification_by_task_id(task_id):
    db = open_session()
    count = db.query(Notification) \
        .filter(Notification.task_id == task_id) \
        .count()
    db.close()
    return count


def update_notification(notification):
    data = {'status': notification.status,
            'request': notification.request,
            'response': notification.response, }
    db = open_session()
    r = db.query(Notification) \
        .filter(Notification.id == notification.id) \
        .update(clear_dict(data), synchronize_session="fetch")
    db.commit()
    db.close()
    return r


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
