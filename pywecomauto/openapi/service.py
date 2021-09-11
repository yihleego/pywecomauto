# -*- coding: utf-8 -*-
from pywecomauto.common.rsa_sign import verify_sha256
from pywecomauto.database.database_manager import *
from pywecomauto.database.models import *


def handle(data):
    if not verify(data):
        return 'Bad Request', 400
    func = METHODS.get(data['method'])
    if not func:
        return 'Bad Request', 400
    return func(json.loads(data['content']))


def create_tasks(content):
    tasks = [Task(company_name=data.get('company_name'),
                  user_name=data.get('user_name'),
                  type=data.get('type'),
                  scheduled_time=data.get('scheduled_time'),
                  content=json.dumps(data.get('content'), ensure_ascii=False))
             for data in content]
    insert_entities(tasks)
    return to_success([to_dict(task) for task in tasks])


def delete_tasks(content):
    affected_rows = delete_task_by_ids(content["id"])
    return to_success(affected_rows)


def query_tasks(content):
    tasks = list_tasks_by_ids(content["id"])
    return to_success([t.to_dict() for t in tasks])


def verify(data):
    app_id = data.get('app_id')
    method = data.get('method')
    timestamp = data.get('timestamp')
    signature = data.get('signature')
    content = data.get('content')
    if not app_id or not method or not timestamp or not signature or not content:
        return False
    app = get_app(data.get('app_id'))
    if not app:
        return False
    return verify_sha256(app.public_key, to_sign_content(data), signature)


def to_sign_content(content):
    data = content.copy()
    if 'signature' in data:
        data.pop('signature')
    keys = sorted(data)
    s = ''
    for k in keys:
        v = json.dumps(data[k], separators=(',', ':'), sort_keys=True, ensure_ascii=False) if isinstance(data[k], dict) else str(data[k])
        s = s + k + "=" + v + '&'
    return s


def to_success(data, message=None):
    return {"success": True,
            "data": data,
            "message": message}


def to_failure(data, message):
    return {"success": False,
            "data": data,
            "message": message}


METHODS = {
    'task.create': create_tasks,
    'task.delete': delete_tasks,
    'task.query': query_tasks,
}
