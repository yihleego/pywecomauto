create table client
(
    id           integer primary key autoincrement,
    created_time text,
    updated_time text,
    expired_time text,
    process      integer not null,
    handle       integer not null,
    name         text,
    company      text,
    status       integer not null default 0
);
create unique index uk_client_handle on client (handle);
create unique index uk_client_name_company on client (name, company);

create table task
(
    id            integer primary key autoincrement,
    created_time  text,
    updated_time  text,
    executed_time text,
    finished_time text,
    name          text    not null,
    company       text    not null,
    type          integer not null,
    priority      integer not null default 0,
    content       text,
    result        text,
    message       text,
    status        integer not null default 0
);
create index idx_task_name_company on task (name, company);

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
