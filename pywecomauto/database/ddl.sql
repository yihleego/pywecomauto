create table app
(
    id           integer primary key autoincrement,
    created_time text,
    updated_time text,
    name         text    not null,
    private_key  text    not null,
    public_key   text    not null,
    url          text,
    status       integer not null default 0
);
create unique index uk_app_name on app (name);

create table client
(
    id           integer primary key autoincrement,
    created_time text,
    updated_time text,
    expired_time text,
    process      integer not null,
    handle       integer not null,
    company_name text,
    user_name    text,
    alias        text,
    phone        text,
    avatar       text,
    status       integer not null default 0
);
create unique index uk_client_handle on client (handle);
create unique index uk_client_company_name_user_name on client (company_name, user_name);

create table task
(
    id             integer primary key autoincrement,
    created_time   text,
    updated_time   text,
    deleted_time   text,
    scheduled_time text,
    executed_time  text,
    finished_time  text,
    company_name   text    not null,
    user_name      text    not null,
    type           integer not null,
    content        text,
    result         text,
    message        text,
    status         integer not null default 0,
    deleted        integer not null default 0
);
create index idx_client_company_name_user_name on task (company_name, user_name);
create index idx_client_scheduled_time on task (scheduled_time);

create table notification
(
    id            integer primary key autoincrement,
    created_time  text,
    updated_time  text,
    notified_time text    not null,
    task_id       integer not null,
    request       text,
    response      text,
    status        integer not null default 0
);
create index idx_notification_task_id on notification (task_id);
